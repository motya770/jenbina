#!/usr/bin/env python3
"""
Unit tests for the Person class
Tests person functionality including needs, conversations, and state management
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
import json

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from core.person.person import Person, Message, Conversation


class TestMessage(unittest.TestCase):
    """Test Message functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.message = Message(
            timestamp=datetime.now(),
            sender="person",
            content="Hello, how are you?",
            message_type="text"
        )
    
    def test_message_initialization(self):
        """Test message initialization"""
        self.assertIsInstance(self.message.timestamp, datetime)
        self.assertEqual(self.message.sender, "person")
        self.assertEqual(self.message.content, "Hello, how are you?")
        self.assertEqual(self.message.message_type, "text")
    
    def test_message_defaults(self):
        """Test message with default values"""
        message = Message(
            timestamp=datetime.now(),
            sender="outsider",
            content="Hi there!"
        )
        self.assertEqual(message.message_type, "text")


class TestConversation(unittest.TestCase):
    """Test Conversation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.conversation = Conversation("Alice")
    
    def test_conversation_initialization(self):
        """Test conversation initialization"""
        self.assertEqual(self.conversation.outsider_name, "Alice")
        self.assertEqual(len(self.conversation.messages), 0)
        self.assertIsInstance(self.conversation.last_interaction, datetime)
    
    def test_add_message(self):
        """Test adding messages to conversation"""
        initial_count = len(self.conversation.messages)
        
        self.conversation.add_message("person", "Hello Alice!")
        self.assertEqual(len(self.conversation.messages), initial_count + 1)
        
        message = self.conversation.messages[-1]
        self.assertEqual(message.sender, "person")
        self.assertEqual(message.content, "Hello Alice!")
        self.assertEqual(message.message_type, "text")
    
    def test_add_message_with_type(self):
        """Test adding message with specific type"""
        self.conversation.add_message("outsider", "Hi there!", "greeting")
        
        message = self.conversation.messages[-1]
        self.assertEqual(message.message_type, "greeting")
    
    def test_get_recent_messages(self):
        """Test getting recent messages"""
        # Add several messages
        for i in range(15):
            self.conversation.add_message("person", f"Message {i}")
        
        recent = self.conversation.get_recent_messages(10)
        self.assertEqual(len(recent), 10)
        self.assertEqual(recent[-1].content, "Message 14")
    
    def test_get_messages_by_type(self):
        """Test getting messages by type"""
        self.conversation.add_message("person", "Hello", "greeting")
        self.conversation.add_message("outsider", "Hi", "greeting")
        self.conversation.add_message("person", "How are you?", "question")
        
        greeting_messages = self.conversation.get_messages_by_type("greeting")
        self.assertEqual(len(greeting_messages), 2)
        
        question_messages = self.conversation.get_messages_by_type("question")
        self.assertEqual(len(question_messages), 1)
    
    def test_last_interaction_update(self):
        """Test that last_interaction updates when adding messages"""
        old_time = self.conversation.last_interaction
        
        # Wait a moment
        import time
        time.sleep(0.1)
        
        self.conversation.add_message("person", "New message")
        
        self.assertGreater(self.conversation.last_interaction, old_time)


class TestPerson(unittest.TestCase):
    """Test Person functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.person = Person("TestPerson")
    
    def test_person_initialization(self):
        """Test person initialization"""
        self.assertEqual(self.person.name, "TestPerson")
        self.assertIsNotNone(self.person.maslow_needs)
        self.assertEqual(len(self.person.conversations), 0)
    
    def test_person_default_name(self):
        """Test person with default name"""
        person = Person()
        self.assertEqual(person.name, "Jenbina")
    
    def test_update_all_needs(self):
        """Test updating all needs"""
        initial_satisfaction = self.person.maslow_needs.get_overall_satisfaction()
        
        # Simulate time passing
        self.person.maslow_needs.update_all_needs(timedelta(hours=1))
        
        new_satisfaction = self.person.maslow_needs.get_overall_satisfaction()
        self.assertNotEqual(initial_satisfaction, new_satisfaction)
    
    def test_add_conversation(self):
        """Test adding a new conversation"""
        conversation = self.person.add_conversation("Bob")
        
        self.assertIsInstance(conversation, Conversation)
        self.assertEqual(conversation.outsider_name, "Bob")
        self.assertIn("Bob", self.person.conversations)
    
    def test_add_existing_conversation(self):
        """Test adding conversation with existing person"""
        conversation1 = self.person.add_conversation("Charlie")
        conversation2 = self.person.add_conversation("Charlie")
        
        self.assertIs(conversation1, conversation2)  # Should return same object
    
    def test_receive_message(self):
        """Test receiving a message from outsider"""
        self.person.receive_message("David", "Hello there!")
        
        self.assertIn("David", self.person.conversations)
        conversation = self.person.conversations["David"]
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].content, "Hello there!")
        self.assertEqual(conversation.messages[0].sender, "outsider")
    
    def test_send_message(self):
        """Test sending a message to outsider"""
        self.person.send_message("Eve", "Hi Eve!")
        
        self.assertIn("Eve", self.person.conversations)
        conversation = self.person.conversations["Eve"]
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].content, "Hi Eve!")
        self.assertEqual(conversation.messages[0].sender, "person")
    
    def test_get_conversation_history(self):
        """Test getting conversation history"""
        # Add some messages
        self.person.receive_message("Frank", "Hello")
        self.person.send_message("Frank", "Hi there")
        self.person.receive_message("Frank", "How are you?")
        
        history = self.person.get_conversation_history("Frank")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].content, "Hello")
        self.assertEqual(history[1].content, "Hi there")
        self.assertEqual(history[2].content, "How are you?")
    
    def test_get_conversation_history_with_limit(self):
        """Test getting limited conversation history"""
        # Add many messages
        for i in range(20):
            self.person.receive_message("Grace", f"Message {i}")
        
        history = self.person.get_conversation_history("Grace", count=10)
        self.assertEqual(len(history), 10)
        self.assertEqual(history[-1].content, "Message 19")
    
    def test_get_conversation_history_nonexistent(self):
        """Test getting history for nonexistent conversation"""
        history = self.person.get_conversation_history("Nonexistent")
        self.assertEqual(len(history), 0)
    
    def test_get_all_conversations(self):
        """Test getting all conversations"""
        self.person.add_conversation("Alice")
        self.person.add_conversation("Bob")
        
        conversations = self.person.get_all_conversations()
        self.assertEqual(len(conversations), 2)
        self.assertIn("Alice", conversations)
        self.assertIn("Bob", conversations)
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        # Add some messages
        self.person.receive_message("Henry", "Hello")
        self.person.send_message("Henry", "Hi")
        self.person.receive_message("Henry", "How are you?")
        
        summary = self.person.get_conversation_summary("Henry")
        
        self.assertEqual(summary["outsider_name"], "Henry")
        self.assertEqual(summary["message_count"], 3)
        self.assertIsInstance(summary["last_interaction"], datetime)
    
    def test_get_conversation_summary_nonexistent(self):
        """Test getting summary for nonexistent conversation"""
        summary = self.person.get_conversation_summary("Nonexistent")
        
        self.assertEqual(summary["outsider_name"], "Nonexistent")
        self.assertEqual(summary["message_count"], 0)
        self.assertIsNone(summary["last_interaction"])
    
    def test_get_communication_stats(self):
        """Test getting communication statistics"""
        # Add conversations with different message counts
        self.person.receive_message("Alice", "Hi")
        self.person.send_message("Alice", "Hello")
        
        self.person.receive_message("Bob", "Hey")
        self.person.send_message("Bob", "Hi")
        self.person.receive_message("Bob", "How are you?")
        
        stats = self.person.get_communication_stats()
        
        self.assertEqual(stats["total_conversations"], 2)
        self.assertEqual(stats["total_messages"], 5)
        self.assertEqual(len(stats["most_active_conversations"]), 2)
        
        # Bob should be more active (3 messages vs 2)
        self.assertEqual(stats["most_active_conversations"][0]["outsider"], "Bob")
        self.assertEqual(stats["most_active_conversations"][0]["message_count"], 3)
    
    def test_get_current_state(self):
        """Test getting current state"""
        state = self.person.get_current_state()
        
        self.assertEqual(state["name"], "TestPerson")
        self.assertIn("maslow_needs", state)
        self.assertIn("communication", state)
        
        # Check maslow_needs structure
        maslow_state = state["maslow_needs"]
        self.assertIn("overall_satisfaction", maslow_state)
        self.assertIn("growth_stage", maslow_state)
        self.assertIn("stage_name", maslow_state)
        
        # Check communication structure
        comm_state = state["communication"]
        self.assertIn("total_conversations", comm_state)
        self.assertIn("total_messages", comm_state)
    
    def test_string_representation(self):
        """Test string representation of person"""
        person_str = str(self.person)
        
        self.assertIn("TestPerson", person_str)
        self.assertIn("maslow_stage", person_str)
        self.assertIn("conversations", person_str)
        self.assertIn("messages", person_str)
    
    def test_complex_conversation_scenario(self):
        """Test a complex conversation scenario"""
        # Simulate a conversation with multiple exchanges
        self.person.receive_message("Alice", "Hello! How are you today?")
        self.person.send_message("Alice", "I'm doing well, thank you! How about you?")
        self.person.receive_message("Alice", "I'm great! What have you been up to?")
        self.person.send_message("Alice", "I've been working on some interesting projects.")
        self.person.receive_message("Alice", "That sounds fascinating! Tell me more.")
        
        # Check conversation state
        conversation = self.person.conversations["Alice"]
        self.assertEqual(len(conversation.messages), 5)
        
        # Check message order and content
        messages = conversation.messages
        self.assertEqual(messages[0].sender, "outsider")
        self.assertEqual(messages[0].content, "Hello! How are you today?")
        self.assertEqual(messages[1].sender, "person")
        self.assertEqual(messages[1].content, "I'm doing well, thank you! How about you?")
        
        # Check statistics
        stats = self.person.get_communication_stats()
        self.assertEqual(stats["total_conversations"], 1)
        self.assertEqual(stats["total_messages"], 5)
        self.assertEqual(stats["most_active_conversations"][0]["outsider"], "Alice")
        self.assertEqual(stats["most_active_conversations"][0]["message_count"], 5)


if __name__ == '__main__':
    unittest.main() 