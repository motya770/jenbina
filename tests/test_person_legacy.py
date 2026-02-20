"""Tests for core/person.py — legacy Person, Message, and Conversation classes."""

import unittest
from datetime import datetime

from core.person import Person, Message, Conversation


class TestMessage(unittest.TestCase):
    """Tests for the Message dataclass."""

    def test_message_defaults(self):
        msg = Message(timestamp=datetime.now(), sender="person", content="Hi")
        self.assertEqual(msg.sender, "person")
        self.assertEqual(msg.content, "Hi")
        self.assertEqual(msg.message_type, "text")

    def test_message_custom_type(self):
        msg = Message(
            timestamp=datetime.now(),
            sender="outsider",
            content="*waves*",
            message_type="action",
        )
        self.assertEqual(msg.message_type, "action")


class TestConversation(unittest.TestCase):
    """Tests for the Conversation dataclass."""

    def test_add_message(self):
        conv = Conversation(outsider_name="Alice")
        conv.add_message("outsider", "Hello!")
        self.assertEqual(len(conv.messages), 1)
        self.assertEqual(conv.messages[0].sender, "outsider")
        self.assertEqual(conv.messages[0].content, "Hello!")

    def test_get_recent_messages_empty(self):
        conv = Conversation(outsider_name="Alice")
        self.assertEqual(conv.get_recent_messages(), [])

    def test_get_recent_messages_limited(self):
        conv = Conversation(outsider_name="Alice")
        for i in range(15):
            conv.add_message("outsider", f"msg {i}")
        recent = conv.get_recent_messages(5)
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[0].content, "msg 10")

    def test_get_messages_by_type(self):
        conv = Conversation(outsider_name="Bob")
        conv.add_message("outsider", "Hey", "text")
        conv.add_message("person", "*nods*", "action")
        conv.add_message("outsider", "What's up?", "text")
        actions = conv.get_messages_by_type("action")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].content, "*nods*")

    def test_str_representation(self):
        conv = Conversation(outsider_name="Charlie")
        conv.add_message("outsider", "Hi")
        s = str(conv)
        self.assertIn("Charlie", s)
        self.assertIn("1 messages", s)


class TestLegacyPerson(unittest.TestCase):
    """Tests for the legacy Person class in core/person.py."""

    def test_default_name(self):
        p = Person()
        self.assertEqual(p.name, "Jenbina")

    def test_maslow_needs_auto_initialized(self):
        p = Person()
        self.assertIsNotNone(p.maslow_needs)

    def test_add_conversation(self):
        p = Person()
        conv = p.add_conversation("Alice")
        self.assertIsInstance(conv, Conversation)
        self.assertIn("Alice", p.conversations)

    def test_add_conversation_idempotent(self):
        p = Person()
        conv1 = p.add_conversation("Alice")
        conv2 = p.add_conversation("Alice")
        self.assertIs(conv1, conv2)

    def test_receive_message(self):
        p = Person()
        p.receive_message("Alice", "Hello Jenbina!")
        history = p.get_conversation_history("Alice")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].sender, "outsider")

    def test_send_message(self):
        p = Person()
        p.send_message("Alice", "Hi Alice!")
        history = p.get_conversation_history("Alice")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].sender, "person")

    def test_get_conversation_history_unknown_person(self):
        p = Person()
        history = p.get_conversation_history("Unknown")
        self.assertEqual(history, [])

    def test_get_conversation_history_with_count(self):
        p = Person()
        for i in range(10):
            p.receive_message("Alice", f"msg {i}")
        recent = p.get_conversation_history("Alice", count=3)
        self.assertEqual(len(recent), 3)

    def test_get_all_conversations(self):
        p = Person()
        p.add_conversation("Alice")
        p.add_conversation("Bob")
        all_convs = p.get_all_conversations()
        self.assertEqual(len(all_convs), 2)
        self.assertIn("Alice", all_convs)
        self.assertIn("Bob", all_convs)

    def test_get_conversation_summary_no_conversation(self):
        p = Person()
        summary = p.get_conversation_summary("Unknown")
        self.assertEqual(summary["message_count"], 0)
        self.assertIsNone(summary["last_interaction"])

    def test_get_conversation_summary_with_messages(self):
        p = Person()
        p.receive_message("Alice", "Hello")
        p.send_message("Alice", "Hi back!")
        summary = p.get_conversation_summary("Alice")
        self.assertEqual(summary["outsider_name"], "Alice")
        self.assertEqual(summary["message_count"], 2)
        self.assertIsNotNone(summary["last_interaction"])
        self.assertIn("recent_messages", summary)

    def test_get_communication_stats(self):
        p = Person()
        p.receive_message("Alice", "Hello")
        p.receive_message("Bob", "Hey")
        p.receive_message("Bob", "How are you?")
        stats = p.get_communication_stats()
        self.assertEqual(stats["total_conversations"], 2)
        self.assertEqual(stats["total_messages"], 3)
        self.assertIsInstance(stats["most_active_conversations"], list)
        # Bob has 2 messages, should be first
        self.assertEqual(stats["most_active_conversations"][0]["outsider"], "Bob")

    def test_get_current_state(self):
        p = Person()
        state = p.get_current_state()
        self.assertEqual(state["name"], "Jenbina")
        self.assertIn("maslow_needs", state)
        self.assertIn("communication", state)

    def test_str_representation(self):
        p = Person()
        s = str(p)
        self.assertIn("Jenbina", s)
        self.assertIn("Person", s)

    def test_update_all_needs(self):
        p = Person()
        # Should not raise
        p.update_all_needs()


if __name__ == "__main__":
    unittest.main()
