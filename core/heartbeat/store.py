"""SQLite storage for the single being, separate from private account data."""

from __future__ import annotations

import json
import os
import socket
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator
from uuid import uuid4

from core.auth.user_db import UserDatabase


# Person keys that start like this are never given to an account: they name
# the inhabitants of her Minecraft world (core/environment/minecraft/conversation.py).
RESERVED_KEY_PREFIX = "minecraft:"


@dataclass
class Lease:
    acquired: bool
    holder: str
    previous_renewed_at: datetime | None


def _pid_namespace() -> str:
    """Identify the local PID namespace where the platform exposes it."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except OSError:
        return ""


def make_owner_id() -> str:
    """Identify this host process and this particular attempt to host her."""
    return f"{socket.gethostname()}|{_pid_namespace()}:{os.getpid()}:{uuid4().hex[:8]}"


def owner_is_dead(owner: str) -> bool:
    """Only a missing PID in this machine's namespace proves an owner is dead."""
    try:
        machine, pid_text, _ = owner.rsplit(":", 2)
        pid = int(pid_text)
    except ValueError:
        return False
    if machine != f"{socket.gethostname()}|{_pid_namespace()}" or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except (OSError, OverflowError):
        # PermissionError means the process exists; other errors prove nothing.
        return False
    return False


class BeingStore:
    """Her state, life events, process lease, and stable account identities.

    The existing per-user state, events, and conversations remain untouched.
    All timestamps use the host machine's local clock, like UserDatabase.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path is not None else UserDatabase().db_path
        directory = os.path.dirname(self.db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS being_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    person_state_json TEXT NOT NULL,
                    situation_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS being_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail_json TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_being_events_created_at
                    ON being_events(created_at);

                CREATE TABLE IF NOT EXISTS being_lease (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    owner TEXT NOT NULL,
                    renewed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS being_people (
                    user_id INTEGER PRIMARY KEY,
                    person_key TEXT UNIQUE NOT NULL
                );
            """)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def load_state(self) -> tuple[str, dict] | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT person_state_json, situation_json FROM being_state WHERE id = 1"
            ).fetchone()
        if row is None:
            return None
        try:
            situation = json.loads(row["situation_json"])
        except (TypeError, ValueError):
            situation = {}
        if not isinstance(situation, dict):
            situation = {}
        return row["person_state_json"], situation

    def save_state(self, person_state_json: str, situation: dict, owner: str | None = None) -> bool:
        """Save only for the current lease holder when an owner is supplied."""
        with self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if owner is not None:
                lease = conn.execute("SELECT owner FROM being_lease WHERE id = 1").fetchone()
                if lease is None or lease["owner"] != owner:
                    return False
            conn.execute(
                """INSERT INTO being_state (id, person_state_json, situation_json, updated_at)
                   VALUES (1, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE
                   SET person_state_json = excluded.person_state_json,
                       situation_json = excluded.situation_json,
                       updated_at = excluded.updated_at""",
                (person_state_json, json.dumps(situation), datetime.now().isoformat()),
            )
        return True

    def store_event(self, kind: str, title: str, detail: dict | None = None,
                    created_at: datetime | None = None) -> int:
        with self._connection() as conn:
            cursor = conn.execute(
                """INSERT INTO being_events (kind, title, detail_json, created_at)
                   VALUES (?, ?, ?, ?)""",
                (kind, title, json.dumps(detail) if detail else None,
                 (created_at or datetime.now()).isoformat()),
            )
            return cursor.lastrowid

    def get_events(self, limit: int = 200) -> list[dict]:
        """The newest events, oldest first, in UserDatabase.get_events format."""
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT id, kind, title, detail_json, created_at FROM being_events
                   ORDER BY created_at DESC, id DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        events = []
        for row in reversed(rows):
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except (TypeError, ValueError):
                continue
            try:
                detail = json.loads(row["detail_json"]) if row["detail_json"] else {}
                if not isinstance(detail, dict):
                    detail = {}
            except (TypeError, ValueError):
                detail = {}
            events.append({
                "id": row["id"], "kind": row["kind"], "title": row["title"],
                "detail": detail, "created_at": created_at,
            })
        return events

    def import_events(self, rows: list[dict]) -> int:
        """Copy a user's event rows, keeping their timestamps and content."""
        with self._connection() as conn:
            conn.executemany(
                """INSERT INTO being_events (kind, title, detail_json, created_at)
                   VALUES (?, ?, ?, ?)""",
                [(row["kind"], row["title"],
                  json.dumps(row["detail"]) if row.get("detail") else None,
                  row["created_at"].isoformat()) for row in rows],
            )
        return len(rows)

    def acquire_lease(self, owner: str, now: datetime, stale_after: timedelta) -> Lease:
        """Check and claim ownership while holding SQLite's writer lock."""
        with self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT owner, renewed_at FROM being_lease WHERE id = 1").fetchone()
            previous = datetime.fromisoformat(row["renewed_at"]) if row else None
            if (row is None or not row["owner"] or row["owner"] == owner
                    or now - previous > stale_after or owner_is_dead(row["owner"])):
                conn.execute(
                    """INSERT INTO being_lease (id, owner, renewed_at) VALUES (1, ?, ?)
                       ON CONFLICT(id) DO UPDATE
                       SET owner = excluded.owner, renewed_at = excluded.renewed_at""",
                    (owner, now.isoformat()),
                )
                return Lease(True, owner, previous)
            return Lease(False, row["owner"], previous)

    def renew_lease(self, owner: str, now: datetime) -> bool:
        with self._connection() as conn:
            cursor = conn.execute(
                "UPDATE being_lease SET renewed_at = ? WHERE id = 1 AND owner = ?",
                (now.isoformat(), owner),
            )
            return cursor.rowcount == 1

    def release_lease(self, owner: str) -> None:
        with self._connection() as conn:
            conn.execute("UPDATE being_lease SET owner = '' WHERE id = 1 AND owner = ?", (owner,))

    def person_key(self, user_id: int, display_name: str | None) -> str:
        """An account's first key is permanent, even when its name changes."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT person_key FROM being_people WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row is not None:
                return row["person_key"]
            conn.execute("BEGIN IMMEDIATE")
            # Another connection may have registered this account after our read.
            row = conn.execute(
                "SELECT person_key FROM being_people WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row is not None:
                return row["person_key"]
            base = (display_name or "").strip() or f"User {user_id}"
            if base.lower().startswith(RESERVED_KEY_PREFIX):
                # That name space belongs to the inhabitants of her Minecraft
                # world; an account must never share a person model with one.
                base = f"User {user_id}"
            used = {row["person_key"] for row in conn.execute("SELECT person_key FROM being_people")}
            key = base
            suffix = 2
            while key in used:
                key = f"{base} ({suffix})"
                suffix += 1
            conn.execute("INSERT INTO being_people (user_id, person_key) VALUES (?, ?)", (user_id, key))
            return key

    def people(self) -> dict[int, str]:
        with self._connection() as conn:
            rows = conn.execute("SELECT user_id, person_key FROM being_people ORDER BY user_id").fetchall()
        return {row["user_id"]: row["person_key"] for row in rows}
