#!/usr/bin/env python3
"""Unit tests for the SQLite user database (core.auth.user_db)."""

import unittest
import tempfile
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.auth.user_db import UserDatabase


class TestUserDatabase(unittest.TestCase):
    """Test UserDatabase initialisation and table creation."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_tables_created(self):
        conn = self.db._get_conn()
        tables = [
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        conn.close()
        self.assertIn("users", tables)
        self.assertIn("conversations", tables)
        self.assertIn("user_state", tables)


class TestUserCRUD(unittest.TestCase):
    """Test user create / read / update operations."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_create_user(self):
        user = self.db.create_or_update_user(
            firebase_uid="uid_123",
            email="alice@example.com",
            display_name="Alice",
            photo_url="https://example.com/alice.jpg",
            provider="google",
        )
        self.assertEqual(user["firebase_uid"], "uid_123")
        self.assertEqual(user["email"], "alice@example.com")
        self.assertEqual(user["display_name"], "Alice")
        self.assertEqual(user["provider"], "google")
        self.assertIsNotNone(user["id"])

    def test_update_user_on_duplicate(self):
        self.db.create_or_update_user(
            firebase_uid="uid_123", email="alice@example.com", display_name="Alice"
        )
        updated = self.db.create_or_update_user(
            firebase_uid="uid_123",
            email="alice@example.com",
            display_name="Alice Updated",
        )
        self.assertEqual(updated["display_name"], "Alice Updated")

    def test_get_user_by_firebase_uid(self):
        self.db.create_or_update_user(
            firebase_uid="uid_456", email="bob@example.com", display_name="Bob"
        )
        user = self.db.get_user_by_firebase_uid("uid_456")
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "bob@example.com")

    def test_get_user_not_found(self):
        result = self.db.get_user_by_firebase_uid("nonexistent")
        self.assertIsNone(result)

    def test_coalesce_preserves_existing_on_none(self):
        """COALESCE(?, col) keeps old value when new value is None."""
        self.db.create_or_update_user(
            firebase_uid="uid_789",
            email="carol@example.com",
            display_name="Carol",
            provider="email",
        )
        updated = self.db.create_or_update_user(
            firebase_uid="uid_789",
            email="carol@example.com",
            # display_name and provider left as None — should keep old values
        )
        self.assertEqual(updated["display_name"], "Carol")
        self.assertEqual(updated["provider"], "email")


class TestMessages(unittest.TestCase):
    """Test conversation message storage and retrieval."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)
        self.user = self.db.create_or_update_user(
            firebase_uid="uid_msg", email="msg@test.com", display_name="Tester"
        )

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_store_and_retrieve_message(self):
        msg_id = self.db.store_message(
            user_id=self.user["id"],
            sender="Tester",
            content="Hello Jenbina",
            message_type="user_message",
        )
        self.assertIsInstance(msg_id, int)

        messages = self.db.get_messages(self.user["id"], limit=10)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Hello Jenbina")
        self.assertEqual(messages[0]["sender"], "Tester")

    def test_messages_oldest_first(self):
        for i in range(5):
            self.db.store_message(
                user_id=self.user["id"],
                sender="Tester",
                content=f"Message {i}",
            )
        messages = self.db.get_messages(self.user["id"], limit=10)
        contents = [m["content"] for m in messages]
        self.assertEqual(contents, [f"Message {i}" for i in range(5)])

    def test_messages_limit(self):
        for i in range(10):
            self.db.store_message(
                user_id=self.user["id"],
                sender="Tester",
                content=f"Message {i}",
            )
        messages = self.db.get_messages(self.user["id"], limit=3)
        self.assertEqual(len(messages), 3)
        # Should be the 3 most recent, oldest-first
        contents = [m["content"] for m in messages]
        self.assertEqual(contents, ["Message 7", "Message 8", "Message 9"])

    def test_metadata_json_round_trip(self):
        meta = {"emotion": "happy", "score": 0.95}
        self.db.store_message(
            user_id=self.user["id"],
            sender="Jenbina",
            content="I'm glad!",
            metadata_dict=meta,
        )
        messages = self.db.get_messages(self.user["id"], limit=1)
        self.assertEqual(messages[0]["metadata"]["emotion"], "happy")
        self.assertAlmostEqual(messages[0]["metadata"]["score"], 0.95)

    def test_metadata_none(self):
        self.db.store_message(
            user_id=self.user["id"],
            sender="Tester",
            content="No metadata",
        )
        messages = self.db.get_messages(self.user["id"], limit=1)
        self.assertIsNone(messages[0]["metadata"])


class TestPersonState(unittest.TestCase):
    """Test person state save/load."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)
        self.user = self.db.create_or_update_user(
            firebase_uid="uid_state", email="state@test.com"
        )

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_save_and_load(self):
        state = json.dumps({"name": "Jenbina", "happiness": 42})
        self.db.save_person_state(self.user["id"], state)
        loaded = self.db.load_person_state(self.user["id"])
        self.assertEqual(json.loads(loaded)["happiness"], 42)

    def test_load_nonexistent(self):
        result = self.db.load_person_state(9999)
        self.assertIsNone(result)

    def test_upsert_overwrites(self):
        self.db.save_person_state(self.user["id"], '{"v": 1}')
        self.db.save_person_state(self.user["id"], '{"v": 2}')
        loaded = self.db.load_person_state(self.user["id"])
        self.assertEqual(json.loads(loaded)["v"], 2)


class TestIsolation(unittest.TestCase):
    """Messages from one user should not leak to another."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)
        self.alice = self.db.create_or_update_user(
            firebase_uid="uid_alice", email="alice@test.com"
        )
        self.bob = self.db.create_or_update_user(
            firebase_uid="uid_bob", email="bob@test.com"
        )

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_messages_isolated(self):
        self.db.store_message(self.alice["id"], "Alice", "Alice's message")
        self.db.store_message(self.bob["id"], "Bob", "Bob's message")

        alice_msgs = self.db.get_messages(self.alice["id"])
        bob_msgs = self.db.get_messages(self.bob["id"])

        self.assertEqual(len(alice_msgs), 1)
        self.assertEqual(alice_msgs[0]["content"], "Alice's message")
        self.assertEqual(len(bob_msgs), 1)
        self.assertEqual(bob_msgs[0]["content"], "Bob's message")

    def test_person_state_isolated(self):
        self.db.save_person_state(self.alice["id"], '{"user": "alice"}')
        self.db.save_person_state(self.bob["id"], '{"user": "bob"}')

        self.assertEqual(
            json.loads(self.db.load_person_state(self.alice["id"]))["user"], "alice"
        )
        self.assertEqual(
            json.loads(self.db.load_person_state(self.bob["id"]))["user"], "bob"
        )


if __name__ == "__main__":
    unittest.main()
