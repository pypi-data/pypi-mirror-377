from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from ohmqtt.connection import Connection, ConnectParams, InvalidStateError, MessageHandlers
from ohmqtt.error import MQTTError
from ohmqtt.mqtt_spec import MQTTQoS, MQTTReasonCode
from ohmqtt.packet import (
    MQTTConnAckPacket,
    MQTTPublishPacket,
    MQTTPubAckPacket,
    MQTTPubRecPacket,
    MQTTPubRelPacket,
    MQTTPubCompPacket,
)
from ohmqtt.property import MQTTConnAckProps, MQTTPublishProps
from ohmqtt.session import Session
from ohmqtt.subscriptions import Subscriptions
from ohmqtt.topic_alias import AliasPolicy


@pytest.fixture
def mock_handlers(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=MessageHandlers)  # type: ignore[no-any-return]


@pytest.fixture
def mock_connection(mocker: MockerFixture) -> Mock:
    conn = mocker.MagicMock(spec=Connection)
    conn.fsm.cond.__enter__.return_value = mocker.Mock()
    conn.fsm.lock.__enter__.return_value = mocker.Mock()
    return conn  # type: ignore[no-any-return]


@pytest.fixture
def mock_subscriptions(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=Subscriptions)  # type: ignore[no-any-return]


def test_session_publish_qos0(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    mock_connection.can_send.return_value = True

    handle = session.publish("test/topic", b"test payload")
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
    ))
    mock_connection.send.reset_mock()
    assert handle.ack is None
    with pytest.raises(ValueError, match="QoS 0 messages will not be acknowledged"):
        handle.wait_for_ack(timeout=1)


def test_session_publish_qos0_aliased(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(TopicAliasMaximum=255)))
    mock_connection.can_send.return_value = False
    mock_connection.send.side_effect = InvalidStateError("TEST")

    session.publish("test/topic", b"test payload", alias_policy=AliasPolicy.TRY)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        properties=MQTTPublishProps(TopicAlias=1),
    ))
    mock_connection.send.reset_mock()

    mock_connection.can_send.return_value = True
    mock_connection.send.side_effect = None

    session.publish("test/topic", b"test payload", alias_policy=AliasPolicy.TRY)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        properties=MQTTPublishProps(TopicAlias=1),
    ))
    mock_connection.send.reset_mock()

    for _ in range(3):
        session.publish("test/topic", b"test payload", alias_policy=AliasPolicy.TRY)
        mock_connection.send.assert_called_with(MQTTPublishPacket(
            topic="",
            payload=b"test payload",
            properties=MQTTPublishProps(TopicAlias=1),
        ))
        mock_connection.send.reset_mock()


def test_session_publish_qos0_unconnected(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    mock_connection.can_send.return_value = False
    mock_connection.send.side_effect = InvalidStateError("TEST")

    handle = session.publish("test/topic", b"test payload")
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
    ))
    mock_connection.send.reset_mock()
    assert handle.ack is None
    with pytest.raises(ValueError, match="QoS 0 messages will not be acknowledged"):
        handle.wait_for_ack(0.001)


@pytest.mark.parametrize("ack_rc", [MQTTReasonCode.Success, MQTTReasonCode.UnspecifiedError])
def test_session_publish_qos1(ack_rc: MQTTReasonCode, mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = True

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q1)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        qos=MQTTQoS.Q1,
        packet_id=1,
    ))
    mock_connection.send.reset_mock()
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    ack = MQTTPubAckPacket(packet_id=1, reason_code=ack_rc)
    session.handle_puback(ack)
    if ack_rc.is_error():
        with pytest.raises(MQTTError) as excinfo:
            handle.wait_for_ack(0.001)
        assert excinfo.value.reason_code == ack_rc
    else:
        assert handle.wait_for_ack() is ack


def test_session_publish_qos1_unconnected(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = False
    mock_connection.send.side_effect = InvalidStateError("TEST")

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q1)
    mock_connection.send.assert_not_called()
    assert handle.ack is None
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)


@pytest.mark.parametrize("comp_rc", [MQTTReasonCode.Success, MQTTReasonCode.MessageRateTooHigh])
def test_session_publish_qos2(comp_rc: MQTTReasonCode, mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = True

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q2)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        qos=MQTTQoS.Q2,
        packet_id=1,
    ))
    mock_connection.send.reset_mock()
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    session.handle_pubrec(MQTTPubRecPacket(packet_id=1))
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    mock_connection.send.assert_called_with(MQTTPubRelPacket(packet_id=1))
    mock_connection.send.reset_mock()

    ack = MQTTPubCompPacket(packet_id=1, reason_code=comp_rc)
    session.handle_pubcomp(ack)
    if comp_rc.is_error():
        with pytest.raises(MQTTError) as excinfo:
            handle.wait_for_ack(0.001)
        assert excinfo.value.reason_code == comp_rc
    else:
        assert handle.wait_for_ack(0.001) is ack


def test_session_publish_qos2_rec_error(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = True

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q2)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        qos=MQTTQoS.Q2,
        packet_id=1,
    ))
    mock_connection.send.reset_mock()
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    session.handle_pubrec(MQTTPubRecPacket(reason_code=MQTTReasonCode.UnspecifiedError, packet_id=1))
    with pytest.raises(MQTTError) as excinfo:
        handle.wait_for_ack(0.001)
    assert excinfo.value.reason_code == MQTTReasonCode.UnspecifiedError

    mock_connection.send.assert_not_called()


def test_session_publish_qos2_disconnect_race(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = True

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q2)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        qos=MQTTQoS.Q2,
        packet_id=1,
    ))
    mock_connection.send.reset_mock()
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    mock_connection.can_send.return_value = True
    mock_connection.send.side_effect = InvalidStateError("TEST")

    session.handle_pubrec(MQTTPubRecPacket(packet_id=1))
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)

    mock_connection.send.assert_called_with(MQTTPubRelPacket(packet_id=1))
    mock_connection.send.reset_mock()


def test_session_publish_qos2_unconnected(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(ReceiveMaximum=255)))
    mock_connection.can_send.return_value = False
    mock_connection.send.side_effect = InvalidStateError("TEST")

    handle = session.publish("test/topic", b"test payload", qos=MQTTQoS.Q2)
    mock_connection.send.assert_not_called()
    with pytest.raises(TimeoutError):
        handle.wait_for_ack(0.001)


@pytest.mark.parametrize("db_path", [":memory:", ""])
@pytest.mark.parametrize("qos", [MQTTQoS.Q0, MQTTQoS.Q1, MQTTQoS.Q2])
def test_session_publish_alias(db_path: str, qos: MQTTQoS, mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection, db_path=db_path)
    session.set_params(ConnectParams(client_id="test_client", clean_start=True))
    mock_connection.can_send.return_value = True

    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(TopicAliasMaximum=255)))

    session.publish("test/topic1", b"test payload", qos=qos, alias_policy=AliasPolicy.NEVER)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic1",
        payload=b"test payload",
        qos=qos,
        packet_id=1 if qos > 0 else 0,
    ))
    mock_connection.send.reset_mock()

    # A failed write before an alias is established should not increment the topic alias.
    mock_connection.send.side_effect = InvalidStateError("TEST")
    session.publish("test/topic2", b"test payload", qos=qos, alias_policy=AliasPolicy.TRY)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic2",
        payload=b"test payload",
        qos=qos,
        packet_id=2 if qos > 0 else 0,
        properties=MQTTPublishProps(TopicAlias=1),
    ))
    mock_connection.send.reset_mock()

    mock_connection.send.side_effect = None
    session.publish("test/topic3", b"test payload", qos=qos, alias_policy=AliasPolicy.TRY)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="test/topic3",
        payload=b"test payload",
        qos=qos,
        packet_id=3 if qos > 0 else 0,
        properties=MQTTPublishProps(TopicAlias=1),
    ))
    mock_connection.send.reset_mock()

    # A failed write after an alias is established should not affect aliases.
    mock_connection.send.side_effect = InvalidStateError("TEST")
    session.publish("test/topic3", b"test payload", qos=qos, alias_policy=AliasPolicy.TRY)
    mock_connection.send.assert_called_with(MQTTPublishPacket(
        topic="",
        payload=b"test payload",
        qos=qos,
        packet_id=4 if qos > 0 else 0,
        properties=MQTTPublishProps(TopicAlias=1),
    ))
    mock_connection.send.reset_mock()

    if qos > 0:
        with pytest.raises(ValueError):
            session.publish("test/topic4", b"test payload", qos=qos, alias_policy=AliasPolicy.ALWAYS)
    else:
        session.publish("test/topic4", b"test payload", qos=qos, alias_policy=AliasPolicy.ALWAYS)
        mock_connection.send.assert_called_with(MQTTPublishPacket(
            topic="test/topic4",
            payload=b"test payload",
            qos=qos,
            properties=MQTTPublishProps(TopicAlias=2),
        ))
        mock_connection.send.reset_mock()


def test_session_handle_publish_qos0(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    mock_connection.can_send.return_value = True

    packet = MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
    )
    session.handle_publish(packet)
    mock_subscriptions.handle_publish.assert_called_once_with(packet)


def test_session_handle_publish_qos1(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    mock_connection.can_send.return_value = True

    packet = MQTTPublishPacket(
        topic="test/topic",
        payload=b"test payload",
        packet_id=3,
        qos=MQTTQoS.Q1,
    )
    session.handle_publish(packet)
    mock_subscriptions.handle_publish.assert_called_once_with(packet)
    mock_connection.send.assert_called_once_with(MQTTPubAckPacket(packet_id=3))


@pytest.mark.parametrize("ack_rc", [MQTTReasonCode.Success, MQTTReasonCode.MessageRateTooHigh])
def test_session_handle_publish_qos2(ack_rc: MQTTReasonCode, mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
     session = Session(mock_handlers, mock_subscriptions, mock_connection)
     mock_connection.can_send.return_value = True

     packet = MQTTPublishPacket(
         topic="test/topic",
         payload=b"test payload",
         packet_id=3,
         qos=MQTTQoS.Q2,
     )
     session.handle_publish(packet)
     mock_subscriptions.handle_publish.assert_called_once_with(packet)
     mock_subscriptions.handle_publish.reset_mock()
     mock_connection.send.assert_called_once_with(MQTTPubRecPacket(packet_id=3))
     mock_connection.send.reset_mock()

     # Filter duplicates.
     session.handle_publish(packet)
     mock_subscriptions.handle_publish.assert_not_called()
     mock_connection.send.assert_called_once_with(MQTTPubRecPacket(packet_id=3))
     mock_connection.send.reset_mock()

     session.handle_pubrel(MQTTPubRelPacket(reason_code=ack_rc, packet_id=3))
     mock_connection.send.assert_called_once_with(MQTTPubCompPacket(packet_id=3))
     mock_connection.send.reset_mock()
     # After PUBREL, message with same packet_id should be treated as a new application message.
     session.handle_publish(packet)
     mock_subscriptions.handle_publish.assert_called_once_with(packet)
     mock_connection.send.assert_called_once_with(MQTTPubRecPacket(packet_id=3))


def test_session_handle_connack_client_id(mocker: MockerFixture, mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    session.set_params(ConnectParams(clean_start=True))
    mock_persistence = mocker.Mock()
    session.persistence = mock_persistence
    mock_persistence.get.return_value = []
    session.handle_connack(MQTTConnAckPacket(properties=MQTTConnAckProps(AssignedClientIdentifier="foo")))
    assert mock_persistence.open.call_args[0][0] == "foo"


def test_session_handle_connack_error(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    with pytest.raises(MQTTError) as excinfo:
        session.handle_connack(MQTTConnAckPacket(reason_code=MQTTReasonCode.Banned))
    assert excinfo.value.reason_code == MQTTReasonCode.Banned


def test_session_handle_connack_no_client_id(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    with pytest.raises(MQTTError) as excinfo:
        session.handle_connack(MQTTConnAckPacket())
    assert excinfo.value.reason_code == MQTTReasonCode.ProtocolError


def test_session_slots(mock_handlers: Mock, mock_subscriptions: Mock, mock_connection: Mock) -> None:
    session = Session(mock_handlers, mock_subscriptions, mock_connection)
    assert not hasattr(session, "__dict__")
    assert all(hasattr(session, attr) for attr in session.__slots__), \
        [attr for attr in session.__slots__ if not hasattr(session, attr)]
