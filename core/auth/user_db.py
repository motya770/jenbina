"""SQLite user database for authentication and conversation persistence."""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


class UserDatabase:
    """SQLite-backed storage for users, conversations, and person state."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.environ.get("JENBINA_DATA_DIR", os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "jenbina_memory",
            ))
            db_path = os.path.join(data_dir, "users.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firebase_uid TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    display_name TEXT,
                    photo_url TEXT,
                    provider TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    last_login TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    metadata_json TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_user
                    ON conversations(user_id, created_at);

                CREATE TABLE IF NOT EXISTS user_state (
                    user_id INTEGER PRIMARY KEY,
                    person_state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE INDEX IF NOT EXISTS idx_events_user
                    ON events(user_id, created_at);
            """)
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    def create_or_update_user(
        self,
        firebase_uid: str,
        email: str,
        display_name: str = None,
        photo_url: str = None,
        provider: str = None,
    ) -> dict:
        """Create a new user or update last_login for an existing one.

        Returns the user row as a dict.
        """
        conn = self._get_conn()
        try:
            existing = conn.execute(
                "SELECT * FROM users WHERE firebase_uid = ?", (firebase_uid,)
            ).fetchone()

            if existing:
                conn.execute(
                    """UPDATE users
                       SET last_login = datetime('now'),
                           display_name = COALESCE(?, display_name),
                           photo_url = COALESCE(?, photo_url),
                           provider = COALESCE(?, provider)
                     WHERE firebase_uid = ?""",
                    (display_name, photo_url, provider, firebase_uid),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM users WHERE firebase_uid = ?", (firebase_uid,)
                ).fetchone()
            else:
                conn.execute(
                    """INSERT INTO users (firebase_uid, email, display_name, photo_url, provider)
                       VALUES (?, ?, ?, ?, ?)""",
                    (firebase_uid, email, display_name, photo_url, provider),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM users WHERE firebase_uid = ?", (firebase_uid,)
                ).fetchone()

            return dict(row)
        finally:
            conn.close()

    def get_user_by_firebase_uid(self, uid: str) -> Optional[dict]:
        """Lookup a user by Firebase UID. Returns dict or None."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE firebase_uid = ?", (uid,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Lookup a user by their integer primary key. Returns dict or None."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_users(self) -> list:
        """Return all users as a list of dicts."""
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


    # ------------------------------------------------------------------
    # Conversation / message storage
    # ------------------------------------------------------------------

    def store_message(
        self,
        user_id: int,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata_dict: dict = None,
    ) -> int:
        """Store a chat message. Returns the new row id."""
        metadata_json = json.dumps(metadata_dict) if metadata_dict else None
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """INSERT INTO conversations (user_id, sender, content, message_type, metadata_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, sender, content, message_type, metadata_json),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_messages(self, user_id: int, limit: int = 50) -> list:
        """Retrieve the most recent messages for a user, oldest-first."""
        conn = self._get_conn()
        try:
            # Tie-break by id (autoincrement) so same-second writes stay in insertion order.
            # datetime('now') only has 1-second resolution, and chat writes user + assistant
            # messages back-to-back, which would otherwise scramble the speaker sequence.
            rows = conn.execute(
                """SELECT * FROM conversations
                    WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT ?""",
                (user_id, limit),
            ).fetchall()
            messages = [dict(r) for r in rows]
            # Parse metadata_json back to dict
            for msg in messages:
                if msg["metadata_json"]:
                    msg["metadata"] = json.loads(msg["metadata_json"])
                else:
                    msg["metadata"] = None
            # Return oldest-first
            messages.reverse()
            return messages
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Admin queries
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Life events (Jenbina's timeline)
    # ------------------------------------------------------------------
    def store_event(
        self,
        user_id: int,
        kind: str,
        title: str,
        detail: dict = None,
        created_at: datetime = None,
    ) -> int:
        """Store one life event. ``created_at`` is written by Python (local,
        naive ISO 8601 with microseconds) so events sort with chat messages."""
        when = (created_at or datetime.now()).isoformat()
        conn = self._get_conn()
        try:
            cur = conn.execute(
                """INSERT INTO events (user_id, kind, title, detail_json, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, kind, title, json.dumps(detail) if detail else None, when),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_events(self, user_id: int, limit: int = 200) -> list:
        """The most recent ``limit`` events for a user, oldest first."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """SELECT id, kind, title, detail_json, created_at FROM events
                    WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        finally:
            conn.close()
        events = []
        for row in reversed(rows):
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except (TypeError, ValueError):
                continue  # a row whose timestamp cannot be read is left out
            try:
                detail = json.loads(row["detail_json"]) if row["detail_json"] else {}
                if not isinstance(detail, dict):
                    detail = {}
            except (TypeError, ValueError):
                detail = {}
            events.append({
                "id": row["id"],
                "kind": row["kind"],
                "title": row["title"],
                "detail": detail,
                "created_at": created_at,
            })
        return events

    def get_all_users_with_message_counts(self) -> list:
        """Return all users with their total and per-sender message counts."""
        conn = self._get_conn()
        try:
            # Split by message_type (stable enum: 'user_message' | 'jenbina_response' | 'proactive_message'),
            # not sender — sender stores display names or "Jenbina" (capital J), which don't match the
            # lowercase constants the query used previously and silently produced zeros.
            rows = conn.execute(
                """SELECT u.id, u.email, u.display_name, u.photo_url,
                          u.provider, u.created_at, u.last_login,
                          COUNT(c.id) AS total_messages,
                          SUM(CASE WHEN c.message_type = 'user_message' THEN 1 ELSE 0 END) AS user_messages,
                          SUM(CASE WHEN c.message_type IN ('jenbina_response', 'proactive_message') THEN 1 ELSE 0 END) AS jenbina_messages
                   FROM users u
                   LEFT JOIN conversations c ON c.user_id = u.id
                   GROUP BY u.id
                   ORDER BY u.last_login DESC"""
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Person state persistence
    # ------------------------------------------------------------------

    def save_person_state(self, user_id: int, state_json: str):
        """Upsert the serialized Person state for a user."""
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO user_state (user_id, person_state_json, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(user_id) DO UPDATE
                   SET person_state_json = excluded.person_state_json,
                       updated_at = datetime('now')""",
                (user_id, state_json),
            )
            conn.commit()
        finally:
            conn.close()

    def load_person_state(self, user_id: int) -> Optional[str]:
        """Load the serialized Person state. Returns JSON string or None."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT person_state_json FROM user_state WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return row["person_state_json"] if row else None
        finally:
            conn.close()
