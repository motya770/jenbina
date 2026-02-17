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
            rows = conn.execute(
                """SELECT * FROM conversations
                    WHERE user_id = ?
                    ORDER BY created_at DESC
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
