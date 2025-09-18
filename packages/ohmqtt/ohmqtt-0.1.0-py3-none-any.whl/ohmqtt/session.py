from __future__ import annotations

from typing import Final, TypeAlias

from .connection import Connection, ConnectParams, InvalidStateError, MessageHandlers
from .error import MQTTError
from .handles import PublishHandle
from .logger import get_logger
from .mqtt_spec import MAX_PACKET_ID, MQTTReasonCode, MQTTQoS
from .packet import (
    MQTTConnAckPacket,
    MQTTPublishPacket,
    MQTTPubAckPacket,
    MQTTPubRecPacket,
    MQTTPubRelPacket,
    MQTTPubCompPacket,
)
from .property import MQTTPublishProps
from .persistence.base import Persistence
from .persistence.in_memory import InMemoryPersistence
from .persistence.sqlite import SQLitePersistence
from .subscriptions import Subscriptions
from .topic_alias import AliasPolicy, OutboundTopicAlias

logger: Final = get_logger("session")

SessionSendablePacketT: TypeAlias = (
    MQTTPublishPacket |
    MQTTPubAckPacket |
    MQTTPubRecPacket |
    MQTTPubRelPacket |
    MQTTPubCompPacket
)


class Session:
    __slots__ = (
        "_cond",
        "connection",
        "inflight",
        "params",
        "persistence",
        "server_receive_maximum",
        "subscriptions",
        "topic_alias",
    )
    persistence: Persistence

    def __init__(
        self,
        handlers: MessageHandlers,
        subscriptions: Subscriptions,
        connection: Connection,
        *,
        db_path: str = "",
        db_fast: bool = False,
    ) -> None:
        self._cond = connection.fsm.cond
        self.topic_alias = OutboundTopicAlias()
        self.inflight = 0
        self.params = ConnectParams()
        self.subscriptions = subscriptions
        self.connection = connection
        if db_path:
            self.persistence = SQLitePersistence(db_path, db_fast=db_fast)
        else:
            self.persistence = InMemoryPersistence()
        self.server_receive_maximum = 0

        handlers.register(MQTTConnAckPacket, self.handle_connack)
        handlers.register(MQTTPublishPacket, self.handle_publish)
        handlers.register(MQTTPubAckPacket, self.handle_puback)
        handlers.register(MQTTPubRecPacket, self.handle_pubrec)
        handlers.register(MQTTPubRelPacket, self.handle_pubrel)
        handlers.register(MQTTPubCompPacket, self.handle_pubcomp)

    def set_params(self, params: ConnectParams) -> None:
        with self._cond:
            self.params = params

    def publish(
        self,
        topic: str,
        payload: bytes,
        *,
        qos: MQTTQoS = MQTTQoS.Q0,
        retain: bool = False,
        properties: MQTTPublishProps | None = None,
        alias_policy: AliasPolicy = AliasPolicy.NEVER,
    ) -> PublishHandle:
        """Publish a message to a topic."""
        properties = properties if properties is not None else MQTTPublishProps()
        if qos > MQTTQoS.Q0:
            with self._cond:
                handle = self.persistence.add(
                    topic=topic,
                    payload=payload,
                    qos=qos,
                    retain=retain,
                    properties=properties,
                    alias_policy=alias_policy,
                )
                if self.connection.can_send():
                    self._flush()
                else:
                    logger.debug("Connection is not ready to send, deferring flush")
                return handle
        else:
            packet = MQTTPublishPacket(
                topic=topic,
                payload=payload,
                qos=qos,
                retain=retain,
                properties=properties,
            )
            try:
                self._send_aliased(packet, alias_policy)
            except InvalidStateError:
                # Not being able to send a packet is not an error for QoS 0.
                logger.debug("Failed to send QoS 0 packet (invalid connection state), ignoring")
            handle = PublishHandle(self._cond)
            handle.exc = ValueError("QoS 0 messages will not be acknowledged")
            return handle

    def _send_packet(self, packet: SessionSendablePacketT) -> None:
        """Try to send a packet to the server."""
        self.connection.send(packet)

    def _send_aliased(
        self,
        packet: MQTTPublishPacket,
        alias_policy: AliasPolicy,
    ) -> None:
        """Send a potentially topic aliased PUBLISH packet to the server.

        This will handle topic aliasing if the server supports it."""
        if alias_policy == AliasPolicy.NEVER:
            # Fast path for no aliasing.
            self._send_packet(packet)
            return
        with self._cond:
            topic = packet.topic
            lookup = self.topic_alias.lookup(topic, alias_policy)
            assert lookup.alias > 0
            packet.properties.TopicAlias = lookup.alias
            if lookup.existed:
                packet.topic = ""
            try:
                self._send_packet(packet)
            except InvalidStateError:
                if not lookup.existed:
                    self.topic_alias.pop()
                raise

    def handle_connack(self, packet: MQTTConnAckPacket) -> None:
        """Handle a connection open event."""
        if packet.reason_code.is_error():
            logger.error("CONNACK error code: %s", packet.reason_code)
            raise MQTTError("Connection failed", packet.reason_code)
        with self._cond:
            self.inflight = 0
            self.topic_alias.reset()
            if packet.properties.ReceiveMaximum is not None:
                self.server_receive_maximum = packet.properties.ReceiveMaximum
            else:
                self.server_receive_maximum = MAX_PACKET_ID - 1
            if packet.properties.TopicAliasMaximum is not None:
                self.topic_alias.max_alias = packet.properties.TopicAliasMaximum
            else:
                self.topic_alias.max_alias = 0
            if packet.properties.AssignedClientIdentifier:
                client_id = packet.properties.AssignedClientIdentifier
            else:
                client_id = self.params.client_id
            if not client_id:
                raise MQTTError("No client ID provided", MQTTReasonCode.ProtocolError)
            clear_persistence = not packet.session_present
            self.persistence.open(client_id, clear=clear_persistence)
            self.subscriptions.handle_connack(packet)
            self._flush()

    def handle_publish(self, packet: MQTTPublishPacket) -> None:
        """Handle a PUBLISH packet from the server."""
        if packet.qos == MQTTQoS.Q2 and not self.persistence.check_rec(packet):
            logger.debug("Received duplicate QoS 2 packet with ID %d", packet.packet_id)
        else:
            self.subscriptions.handle_publish(packet)

        if packet.qos == MQTTQoS.Q1:
            ack_packet = MQTTPubAckPacket(packet_id=packet.packet_id)
            self._send_packet(ack_packet)
        elif packet.qos == MQTTQoS.Q2:
            self.persistence.set_rec(packet)
            rec_packet = MQTTPubRecPacket(packet_id=packet.packet_id)
            self._send_packet(rec_packet)

    def handle_puback(self, packet: MQTTPubAckPacket) -> None:
        """Handle a PUBACK packet from the server."""
        if packet.reason_code.is_error():
            logger.error("Received PUBACK with error code: %s", packet.reason_code)
        with self._cond:
            self.persistence.ack(packet)
            self.inflight -= 1
            self._flush()

    def handle_pubrec(self, packet: MQTTPubRecPacket) -> None:
        """Handle a PUBREC packet from the server."""
        with self._cond:
            if packet.reason_code.is_error():
                logger.error("Received PUBREC with error code: %s", packet.reason_code)
            self.persistence.ack(packet)
            self.inflight -= 1
            self._flush()

    def handle_pubrel(self, packet: MQTTPubRelPacket) -> None:
        """Handle a PUBREL packet from the server."""
        if packet.reason_code.is_error():
            logger.error("Received PUBREL with error code: %s", packet.reason_code)
        self.persistence.rel(packet)
        comp_packet = MQTTPubCompPacket(packet_id=packet.packet_id)
        self._send_packet(comp_packet)

    def handle_pubcomp(self, packet: MQTTPubCompPacket) -> None:
        """Handle a PUBCOMP packet from the server."""
        if packet.reason_code.is_error():
            logger.error("Received PUBCOMP with error code: %s", packet.reason_code)
        with self._cond:
            self.persistence.ack(packet)
            self.inflight -= 1
            self._flush()

    def _flush(self) -> None:
        """Send queued packets up to the server's receive maximum."""
        with self._cond:
            allowed_count = self.server_receive_maximum - self.inflight
            pending_message_ids = self.persistence.get(allowed_count)
            for message_id in pending_message_ids:
                packet, alias_policy = self.persistence.render(message_id)
                self.inflight += 1
                try:
                    if type(packet) is MQTTPublishPacket:
                        self._send_aliased(packet, alias_policy)
                    else:
                        self._send_packet(packet)
                except InvalidStateError:
                    # A race during transition out of ConnectedState can cause this.
                    # The rest of the machinery should be able to handle it.
                    logger.debug("Failed to send reliable packet (invalid connection state), ignoring")
