from contextlib import suppress
import sqlite3
from threading import Condition
from typing import Final
import weakref

from .base import LostMessageError, Persistence, RenderedPacket
from ..error import MQTTError
from ..handles import PublishHandle
from ..logger import get_logger
from ..mqtt_spec import MAX_PACKET_ID, MQTTQoS
from ..packet import (
    MQTTPublishPacket,
    MQTTPubAckPacket,
    MQTTPubRecPacket,
    MQTTPubRelPacket,
    MQTTPubCompPacket,
)
from ..property import MQTTPublishProps
from ..topic_alias import AliasPolicy

logger: Final = get_logger("persistence.sqlite")

SCHEMA_VERSION: Final[int] = 0


class SchemaError(Exception):
    """Database schema error."""


class SQLitePersistence(Persistence):
    """SQLite persistence for MQTT messages.

    This class provides a SQLite-based persistence layer for MQTT messages.
    """
    __slots__ = ("_cond", "_conn", "_cursor", "_db_path", "_handles")
    def __init__(self, db_path: str, *, db_fast: bool = False) -> None:
        self._cond = Condition()
        self._handles: weakref.WeakValueDictionary[int, PublishHandle] = weakref.WeakValueDictionary({})
        self._db_path = db_path
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._cursor = self._conn.cursor()
        if db_fast:
            self._cursor.executescript(
                """
                PRAGMA journal_mode = WAL;
                PRAGMA synchronous = NORMAL;
                """
            )
        self._cursor.execute("PRAGMA user_version")
        current_version = self._cursor.fetchone()[0]
        if current_version != SCHEMA_VERSION:
            raise SchemaError(f"Database version {current_version} does not match library version {SCHEMA_VERSION}")
        self._create_tables()

    def __del__(self) -> None:
        # Ignore "already closed" errors while closing resources.
        with suppress(sqlite3.ProgrammingError):
            self._cursor.close()
        with suppress(sqlite3.ProgrammingError):
            self._conn.close()

    def __len__(self) -> int:
        with self._cond:
            self._cursor.execute(
                """
                SELECT COUNT(*) FROM messages
                """
            )
            row = self._cursor.fetchone()
            return int(row[0])

    def _create_tables(self) -> None:
        """Create the necessary tables in the SQLite database."""
        with self._cond:
            self._cursor.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._cursor.executescript(
                """
                BEGIN;
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    topic TEXT NOT NULL,
                    payload BLOB NOT NULL,
                    qos INTEGER NOT NULL,
                    retain INTEGER NOT NULL,
                    properties BLOB,
                    alias_policy INTEGER NOT NULL,
                    dup INTEGER DEFAULT 0,
                    received INTEGER DEFAULT 0,
                    packet_id INTEGER UNIQUE DEFAULT NULL,
                    inflight INTEGER DEFAULT 0
                ) STRICT;
                CREATE TABLE IF NOT EXISTS received (
                    packet_id INTEGER PRIMARY KEY
                ) STRICT;
                CREATE TABLE IF NOT EXISTS client_id (
                    id INTEGER PRIMARY KEY CHECK (id = 0),
                    client_id TEXT DEFAULT NULL
                ) STRICT;
                INSERT OR IGNORE INTO client_id (id) VALUES (0);
                COMMIT;
                """
            )

    def _get_client_id(self) -> str:
        """Get the client ID from the database."""
        with self._cond:
            self._cursor.execute(
                """
                SELECT client_id FROM client_id WHERE id = 0
                """
            )
            row = self._cursor.fetchone()
            return str(row[0])

    def _set_client_id(self, client_id: str) -> None:
        """Set the client ID in the database."""
        with self._cond:
            self._cursor.execute(
                """
                UPDATE client_id SET client_id = ? WHERE id = 0
                """,
                (client_id,),
            )
            self._conn.commit()

    def add(
        self,
        topic: str,
        payload: bytes,
        qos: MQTTQoS,
        retain: bool,
        properties: MQTTPublishProps,
        alias_policy: AliasPolicy,
    ) -> PublishHandle:
        if alias_policy == AliasPolicy.ALWAYS:
            raise ValueError("AliasPolicy must not be ALWAYS for retained messages.")
        with self._cond:
            properties_blob = properties.encode() if len(properties) > 0 else None
            self._cursor.execute(
                """
                INSERT INTO messages (topic, payload, qos, retain, properties, alias_policy)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (topic, payload, qos.value, int(retain), properties_blob, alias_policy.value),
            )
            self._conn.commit()
            message_id = self._cursor.lastrowid
            assert message_id is not None
            handle = PublishHandle(self._cond)
            self._handles[message_id] = handle
            return handle

    def get(self, count: int) -> list[int]:
        with self._cond:
            self._cursor.execute(
                """
                SELECT id FROM messages
                WHERE inflight = 0
                ORDER BY id ASC
                LIMIT ?
                """,
                (count,),
            )
            rows = self._cursor.fetchall()
            return [row[0] for row in rows]

    def ack(self, packet: MQTTPubAckPacket | MQTTPubRecPacket | MQTTPubCompPacket) -> None:
        packet_id = packet.packet_id
        rc = packet.reason_code
        with self._cond:
            self._cursor.execute(
                """
                SELECT id, qos, received FROM messages WHERE packet_id = ?
                """,
                (packet_id,),
            )
            row = self._cursor.fetchone()
            if row is None:
                raise ValueError(f"Unknown packet_id: {packet_id}")
            message_id, qos, received = row
            if received or qos == 1 or rc.is_error():
                # If the message is QoS 1, we need to delete it from the store.
                self._cursor.execute(
                    """
                    DELETE FROM messages WHERE id = ?
                    """,
                    (message_id,),
                )
                handle = self._handles.pop(message_id, None)
                if handle is not None:
                    handle.ack = packet
                    if rc.is_error():
                        handle.exc = MQTTError("Error code in acknowledgement packet", rc)
                    self._cond.notify_all()
            else:
                # If the message is QoS 2, we need to mark it as received.
                self._cursor.execute(
                    """
                    UPDATE messages SET inflight = 0, received = 1 WHERE id = ?
                    """,
                    (message_id,),
                )
            self._conn.commit()

    def check_rec(self, packet: MQTTPublishPacket) -> bool:
        if packet.qos != MQTTQoS.Q2:
            raise ValueError("Not a QoS 2 PUBLISH packet")
        with self._cond:
            self._cursor.execute(
                """
                SELECT packet_id FROM received WHERE packet_id = ?
                """,
                (packet.packet_id,),
            )
            row = self._cursor.fetchone()
            if row is not None:
                logger.debug("Received duplicate QoS 2 packet with ID %d", packet.packet_id)
                return False
            return True

    def set_rec(self, packet: MQTTPublishPacket) -> None:
        if packet.qos != MQTTQoS.Q2:
            raise ValueError("Not a QoS 2 PUBLISH packet")
        with self._cond:
            self._cursor.execute(
                """
                INSERT INTO received (packet_id) VALUES (?)
                """,
                (packet.packet_id,),
            )
            self._conn.commit()

    def rel(self, packet: MQTTPubRelPacket) -> None:
        with self._cond:
            self._cursor.execute(
                """
                DELETE FROM received WHERE packet_id = ?
                """,
                (packet.packet_id,),
            )
            self._conn.commit()

    def _generate_packet_id(self, message_id: int) -> int:
        """Generate a unique packet ID for the message."""
        packet_id = message_id
        while packet_id > MAX_PACKET_ID:
            packet_id -= MAX_PACKET_ID
        return packet_id

    def render(self, message_id: int) -> RenderedPacket:
        with self._cond:
            self._cursor.execute(
                """
                SELECT topic, payload, qos, retain, properties, dup, received, packet_id, alias_policy, (SELECT MIN(id) FROM messages WHERE inflight = 0)
                FROM messages
                WHERE id = ?
                """,
                (message_id,),
            )
            row = self._cursor.fetchone()
            if row is None:
                raise KeyError(f"Message ID {message_id} not found in persistence store.")
            topic, payload, qos, retain, properties_blob, dup, received, packet_id, alias_policy, min_id = row
            if message_id != min_id:
                raise ValueError(f"Message {message_id} is not next in queue.")
            if properties_blob is not None:
                properties_view = memoryview(properties_blob)
                properties, _ = MQTTPublishProps.decode(properties_view)
            else:
                properties = MQTTPublishProps()
            if packet_id is None:
                packet_id = self._generate_packet_id(message_id)
            qos = MQTTQoS(qos)
            packet: MQTTPublishPacket | MQTTPubRelPacket
            if received:
                alias_policy = AliasPolicy.NEVER
                packet = MQTTPubRelPacket(packet_id=packet_id)
            else:
                alias_policy = AliasPolicy(alias_policy)
                packet = MQTTPublishPacket(
                    topic=topic,
                    payload=payload,
                    packet_id=packet_id,
                    qos=qos,
                    retain=bool(retain),
                    properties=properties,
                    dup=dup,
                )
            self._cursor.execute(
                """
                UPDATE messages SET inflight = 1, packet_id = ? WHERE id = ?
                """,
                (packet_id, message_id),
            )
            self._conn.commit()
            return RenderedPacket(packet, alias_policy)

    def _reset_inflight(self) -> None:
        """Clear inflight status of all messages."""
        with self._cond:
            self._cursor.executescript(
                """
                BEGIN;
                UPDATE messages SET dup = 1 WHERE inflight = 1;
                UPDATE messages SET inflight = 0;
                COMMIT;
                """
            )

    def clear(self) -> None:
        with self._cond:
            self._cursor.executescript(
                """
                BEGIN;
                DELETE FROM messages;
                DELETE FROM received;
                COMMIT;
                """
            )
            if self._handles:
                for handle in self._handles.values():
                    handle.exc = LostMessageError("Message lost from persistence store")
                self._cond.notify_all()
            self._handles.clear()

    def open(self, client_id: str, clear: bool = False) -> None:
        logger.debug("Opening SQLite persistence with client ID: %s clear=%s", client_id, clear)
        with self._cond:
            if clear or client_id != self._get_client_id():
                logger.debug("Clearing SQLite persistence for client ID: %s", client_id)
                self._set_client_id(client_id)
                self.clear()
            else:
                self._reset_inflight()
