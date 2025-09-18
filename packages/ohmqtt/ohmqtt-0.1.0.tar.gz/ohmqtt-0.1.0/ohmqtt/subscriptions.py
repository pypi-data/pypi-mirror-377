from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
import threading
from typing import Callable, Final, Sequence, TYPE_CHECKING
import weakref

from .connection import Connection, InvalidStateError, MessageHandlers
from .error import MQTTError
from .handles import SubscribeHandle, UnsubscribeHandle
from .logger import get_logger
from .mqtt_spec import MAX_PACKET_ID, MQTTReasonCode, MQTTQoS
from .packet import (
    MQTTPublishPacket,
    MQTTSubscribePacket,
    MQTTSubAckPacket,
    MQTTUnsubscribePacket,
    MQTTUnsubAckPacket,
    MQTTConnAckPacket,
)
from .property import MQTTSubscribeProps, MQTTUnsubscribeProps
from .topic_alias import InboundTopicAlias
from .topic_filter import validate_topic_filter, validate_share_name, join_share, match_topic_filter

if TYPE_CHECKING:
    from .client import Client

logger: Final = get_logger("subscriptions")

SubscribeCallback = Callable[["Client", MQTTPublishPacket], None]


class NoMatchingSubscriptionError(Exception):
    """Exception raised when no matching subscription is found when unsubscribing."""


class ReconfiguredError(Exception):
    """A subscribe operation was reconfigured before being acknowledged."""


class RetainPolicy(IntEnum):
    """Policy for broker sending retained messages upon a subscription.

    ALWAYS: Always send retained messages on subscription.

    ONCE: Only send retained messages on the first subscription to a topic.

    NEVER: Never send retained messages on subscription."""
    ALWAYS = 0
    ONCE = 1
    NEVER = 2


class _SubscriptionState(IntEnum):
    """Internal state of a subscription."""
    SUBSCRIBING = 0
    SUBSCRIBED = 1
    UNSUBSCRIBING = 2
    UNSUBSCRIBED = 3


@dataclass(match_args=True, slots=True)
class Subscription:
    """All the data about a request for subscription."""
    topic_filter: str
    callback: SubscribeCallback
    max_qos: MQTTQoS = MQTTQoS.Q2
    share_name: str | None = None
    no_local: bool = False
    retain_as_published: bool = False
    retain_policy: RetainPolicy = RetainPolicy.ALWAYS
    sub_id: int | None = None
    user_properties: tuple[tuple[str, str], ...] | None = None
    state: _SubscriptionState = field(default=_SubscriptionState.SUBSCRIBING)
    effective_filter: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        validate_topic_filter(self.topic_filter)
        if self.share_name is not None:
            validate_share_name(self.share_name)
        self.effective_filter = join_share(self.topic_filter, self.share_name)

    def render_sub(self) -> MQTTSubscribePacket:
        """Render the subscription into a SUBSCRIBE packet."""
        opts = self.max_qos.value | (self.retain_policy << 4) | (self.retain_as_published << 3) | (self.no_local << 2)
        props = MQTTSubscribeProps()
        if self.sub_id is not None:
            props.SubscriptionIdentifier = {self.sub_id}
        if self.user_properties is not None:
            props.UserProperty = self.user_properties
        return MQTTSubscribePacket(
            topics=[(self.effective_filter, opts)],
            properties=props,
        )

    def render_unsub(self) -> MQTTUnsubscribePacket:
        """Render the subscription into an UNSUBSCRIBE packet."""
        props = MQTTUnsubscribeProps()
        return MQTTUnsubscribePacket(
            topics=[self.effective_filter],
            properties=props,
        )


class Subscriptions:
    """Container for MQTT subscriptions and their callbacks."""
    __slots__ = (
        "__weakref__",
        "_client",
        "_cond",
        "_connection",
        "_inflight_sub_packet_ids",
        "_inflight_unsub_packet_ids",
        "_next_sub_packet_id",
        "_next_unsub_packet_id",
        "_sub_handles",
        "_subscriptions",
        "_topic_alias",
        "_unsub_handles",
    )

    def __init__(
        self,
        handlers: MessageHandlers,
        connection: Connection,
        client: weakref.ReferenceType[Client],
    ) -> None:
        self._connection = connection
        self._client = client
        self._cond = threading.Condition(connection.fsm.lock)
        self._topic_alias = InboundTopicAlias()
        self._subscriptions: dict[str, Subscription] = {}
        self._sub_handles: weakref.WeakValueDictionary[str, SubscribeHandle] = weakref.WeakValueDictionary()
        self._unsub_handles: weakref.WeakValueDictionary[str, UnsubscribeHandle] = weakref.WeakValueDictionary()
        self._inflight_sub_packet_ids: dict[int, str] = {}
        self._inflight_unsub_packet_ids: dict[int, str] = {}
        self._next_sub_packet_id = 1
        self._next_unsub_packet_id = 1

        handlers.register(MQTTSubAckPacket, self.handle_suback)
        handlers.register(MQTTUnsubAckPacket, self.handle_unsuback)

    def subscribe(
        self,
        topic_filter: str,
        callback: SubscribeCallback,
        max_qos: MQTTQoS = MQTTQoS.Q2,
        *,
        share_name: str | None = None,
        no_local: bool = False,
        retain_as_published: bool = False,
        retain_policy: RetainPolicy = RetainPolicy.ALWAYS,
        sub_id: int | None = None,
        user_properties: Sequence[tuple[str, str]] | None = None,
    ) -> SubscribeHandle:
        """Add a subscription with a callback.

        Repeated calls to subscribe with the same combination of share_name and topic_filter will reconfigure
        the existing subscription with the new parameters, discarding the previous callback.

        :return: A SubscribeHandle which can be used to wait for ack."""
        sub = Subscription(
            topic_filter=topic_filter,
            callback=callback,
            max_qos=max_qos,
            share_name=share_name,
            no_local=no_local,
            retain_as_published=retain_as_published,
            retain_policy=retain_policy,
            sub_id=sub_id,
            user_properties=tuple(user_properties) if user_properties is not None else None,
        )
        with self._cond:
            self._subscriptions[sub.effective_filter] = sub
            if (existing := self._sub_handles.get(sub.effective_filter, None)) is not None and existing.ack is None and existing.exc is None:
                existing.exc = ReconfiguredError("Topic was reconfigured")
                self._cond.notify_all()
            handle = SubscribeHandle(self._cond)
            self._sub_handles[sub.effective_filter] = handle
            self._flush_packets()
            return handle

    def _flush_packets(self) -> None:
        """Try to send all pending SUBSCRIBE and UNSUBSCRIBE packets."""
        with self._cond:
            pending_subs = [
                sub for sub in self._subscriptions.values() if (
                    sub.state == _SubscriptionState.SUBSCRIBING and sub.effective_filter not in self._inflight_sub_packet_ids.values()
                )
            ]
            for sub in pending_subs:
                sub_packet = sub.render_sub()
                sub_packet.packet_id = self._get_next_sub_packet_id()
                self._inflight_sub_packet_ids[sub_packet.packet_id] = sub.effective_filter
                try:
                    self._connection.send(sub_packet)
                except InvalidStateError:
                    logger.debug("Connection closed, SUBSCRIBE not sent")
                    del self._inflight_sub_packet_ids[sub_packet.packet_id]
                    return

            pending_unsubs = [
                sub for sub in self._subscriptions.values() if (
                    sub.state == _SubscriptionState.UNSUBSCRIBING and sub.effective_filter not in self._inflight_unsub_packet_ids.values()
                )
            ]
            for sub in pending_unsubs:
                unsub_packet = sub.render_unsub()
                unsub_packet.packet_id = self._get_next_unsub_packet_id()
                self._inflight_unsub_packet_ids[unsub_packet.packet_id] = sub.effective_filter
                try:
                    self._connection.send(unsub_packet)
                except InvalidStateError:
                    logger.debug("Connection closed, UNSUBSCRIBE not sent")
                    del self._inflight_unsub_packet_ids[unsub_packet.packet_id]
                    return

    def _get_next_sub_packet_id(self) -> int:
        """Get the next SUBSCRIBE packet identifier."""
        sub_id = self._next_sub_packet_id
        self._next_sub_packet_id += 1
        if self._next_sub_packet_id > MAX_PACKET_ID:
            self._next_sub_packet_id = 1
        return sub_id

    def unsubscribe(
        self,
        topic_filter: str,
        *,
        share_name: str | None = None,
    ) -> UnsubscribeHandle | None:
        """Unsubscribe from a topic filter.

        :return: UnsubscribeHandle if the topic was subscribed, otherwise None."""
        effective_filter = join_share(topic_filter, share_name)
        with self._cond:
            if effective_filter not in self._subscriptions:
                # Nothing to unsubscribe.
                return None
            sub = self._subscriptions[effective_filter]
            if sub.state == _SubscriptionState.UNSUBSCRIBED:
                return None
            sub.state = _SubscriptionState.UNSUBSCRIBING
            if (existing := self._unsub_handles.get(effective_filter, None)) is not None and existing.ack is None and existing.exc is None:
                existing.exc = ReconfiguredError("Topic was reconfigured")
                self._cond.notify_all()
            handle = UnsubscribeHandle(self._cond)
            self._unsub_handles[effective_filter] = handle
            self._flush_packets()
            return handle

    def _get_next_unsub_packet_id(self) -> int:
        """Get the next UNSUBSCRIBE packet identifier."""
        unsub_id = self._next_unsub_packet_id
        self._next_unsub_packet_id += 1
        if self._next_unsub_packet_id > MAX_PACKET_ID:
            self._next_unsub_packet_id = 1
        return unsub_id

    def handle_publish(self, packet: MQTTPublishPacket) -> None:
        """Handle incoming PUBLISH packets."""
        with self._cond:
            client = self._client()
            if client is None:
                raise RuntimeError("Client went out of scope")
            self._topic_alias.handle(packet)
            subs = [sub for sub in self._subscriptions.values() if match_topic_filter(sub.topic_filter, packet.topic)]
            if packet.properties.SubscriptionIdentifier is not None:
                subs = [sub for sub in subs if sub.sub_id in packet.properties.SubscriptionIdentifier]
            for sub in subs:
                try:
                    sub.callback(client, packet)
                except Exception:  # noqa: PERF203
                    logger.exception("Unhandled exception in subscription callback")

    def handle_suback(self, packet: MQTTSubAckPacket) -> None:
        """Handle incoming SUBACK packets."""
        if any(True for code in packet.reason_codes if code.is_error()):
            errs = [hex(code) for code in packet.reason_codes if code.is_error()]
            logger.error("Errors found in SUBACK return: %s", errs)
        with self._cond:
            effective_topic_filter = self._inflight_sub_packet_ids.pop(packet.packet_id, None)
            if effective_topic_filter is None:
                raise MQTTError(f"Received SUBACK for unknown packet ID: {packet.packet_id}", MQTTReasonCode.ProtocolError)
            sub = self._subscriptions.get(effective_topic_filter, None)
            if sub is not None and sub.state == _SubscriptionState.SUBSCRIBING:
                sub.state = _SubscriptionState.SUBSCRIBED
            handle = self._sub_handles.pop(effective_topic_filter, None)
            if handle is not None:
                handle.ack = packet
                self._cond.notify_all()

    def handle_unsuback(self, packet: MQTTUnsubAckPacket) -> None:
        """Handle incoming UNSUBACK packets."""
        if any(True for code in packet.reason_codes if code.is_error()):
            errs = [hex(code) for code in packet.reason_codes if code.is_error()]
            logger.error("Errors found in UNSUBACK return: %s", errs)
        with self._cond:
            effective_topic_filter = self._inflight_unsub_packet_ids.pop(packet.packet_id, None)
            if effective_topic_filter is None:
                raise MQTTError(f"Received UNSUBACK for unknown packet ID: {packet.packet_id}", MQTTReasonCode.ProtocolError)
            sub = self._subscriptions.get(effective_topic_filter, None)
            if sub is not None and sub.state == _SubscriptionState.UNSUBSCRIBING:
                sub.state = _SubscriptionState.UNSUBSCRIBED
            handle = self._unsub_handles.pop(effective_topic_filter, None)
            if handle is not None:
                handle.ack = packet
                self._cond.notify_all()

    def handle_connack(self, packet: MQTTConnAckPacket) -> None:
        """Handle incoming CONNACK packets."""
        with self._cond:
            self._next_sub_packet_id = 1
            self._next_unsub_packet_id = 1
            self._topic_alias.reset()
            self._inflight_sub_packet_ids.clear()
            self._inflight_unsub_packet_ids.clear()
            if not packet.session_present:
                for sub in self._subscriptions.values():
                    if sub.state == _SubscriptionState.SUBSCRIBED:
                        sub.state = _SubscriptionState.SUBSCRIBING
                    elif sub.state == _SubscriptionState.UNSUBSCRIBING:
                        sub.state = _SubscriptionState.UNSUBSCRIBED
            self._flush_packets()
