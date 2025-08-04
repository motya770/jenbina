#!/usr/bin/env python3
"""
Unit tests for the hybrid memory system
Tests ChromaDB, Neo4j, and SQLite integration
"""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import json

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from hybrid_memory_system import HybridMemorySystem, MemoryEvent


class TestMemoryEvent(unittest.TestCase):
    """Test MemoryEvent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.event = MemoryEvent(
            event_id="test_event_001",
            timestamp=datetime.now(),
            event_type="conversation",
            content="Test conversation content",
            people=["Alice", "Bob"],
            locations=["Coffee Shop"],
            actions=["discussed", "learned"],
            emotions=["excited", "curious"],
            needs_state={"hunger": 85.0, "sleep": 90.0},
            metadata={"topic": "AI", "duration": 30}
        )
    
    def test_memory_event_initialization(self):
        """Test memory event initialization"""
        self.assertEqual(self.event.event_id, "test_event_001")
        self.assertIsInstance(self.event.timestamp, datetime)
        self.assertEqual(self.event.event_type, "conversation")
        self.assertEqual(self.event.content, "Test conversation content")
        self.assertEqual(self.event.people, ["Alice", "Bob"])
        self.assertEqual(self.event.locations, ["Coffee Shop"])
        self.assertEqual(self.event.actions, ["discussed", "learned"])
        self.assertEqual(self.event.emotions, ["excited", "curious"])
        self.assertEqual(self.event.needs_state, {"hunger": 85.0, "sleep": 90.0})
        self.assertEqual(self.event.metadata, {"topic": "AI", "duration": 30})
    
    def test_memory_event_defaults(self):
        """Test memory event with default values"""
        event = MemoryEvent(
            event_id="test_event_002",
            timestamp=datetime.now(),
            event_type="action",
            content="Simple action"
        )
        
        self.assertEqual(event.people, [])
        self.assertEqual(event.locations, [])
        self.assertEqual(event.actions, [])
        self.assertEqual(event.emotions, [])
        self.assertEqual(event.needs_state, {})
        self.assertEqual(event.metadata, {})


class TestHybridMemorySystem(unittest.TestCase):
    """Test HybridMemorySystem functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store_path = os.path.join(self.temp_dir, "vector_store")
        self.time_series_path = os.path.join(self.temp_dir, "timeseries.db")
        
        # Initialize memory system without Neo4j for testing
        self.memory_system = HybridMemorySystem(
            embeddings_model="llama3.2:3b-instruct-fp16",
            neo4j_uri="bolt://localhost:9999",  # Invalid URI to disable Neo4j
            neo4j_user="test",
            neo4j_password="test",
            vector_store_path=self.vector_store_path,
            time_series_path=self.time_series_path
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Close connections
        self.memory_system.close()
        
        # Remove temporary directories
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.memory_system.chroma_collection)
        self.assertIsNone(self.memory_system.graph_driver)  # Should be None due to invalid URI
        self.assertIsNotNone(self.memory_system.time_series_conn)
    
    def test_store_memory(self):
        """Test storing a memory event"""
        event = MemoryEvent(
            event_id="test_event_001",
            timestamp=datetime.now(),
            event_type="conversation",
            content="Test conversation",
            people=["Alice"],
            locations=["Home"],
            actions=["talked"],
            emotions=["happy"],
            needs_state={"hunger": 80.0},
            metadata={"topic": "testing"}
        )
        
        event_id = self.memory_system.store_memory(event)
        
        self.assertIsNotNone(event_id)
        self.assertEqual(event_id, "test_event_001")
    
    def test_store_memory_auto_id(self):
        """Test storing memory with auto-generated ID"""
        event = MemoryEvent(
            event_id=None,  # Will be auto-generated
            timestamp=datetime.now(),
            event_type="action",
            content="Test action",
            people=["Bob"],
            locations=["Office"],
            actions=["worked"],
            emotions=["focused"],
            needs_state={"achievement": 70.0},
            metadata={"duration": 60}
        )
        
        event_id = self.memory_system.store_memory(event)
        
        self.assertIsNotNone(event_id)
        self.assertNotEqual(event_id, "test_event_001")  # Should be different
    
    def test_retrieve_semantic_memories(self):
        """Test semantic memory retrieval"""
        # Store some test memories
        events = [
            MemoryEvent(
                event_id=f"event_{i}",
                timestamp=datetime.now(),
                event_type="conversation",
                content=f"Conversation about AI and machine learning {i}",
                people=["Alice"],
                locations=["Coffee Shop"],
                actions=["discussed"],
                emotions=["excited"],
                needs_state={"creativity": 80.0},
                metadata={"topic": "AI"}
            )
            for i in range(3)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Retrieve memories
        memories = self.memory_system.retrieve_semantic_memories("artificial intelligence", top_k=3)
        
        self.assertGreater(len(memories), 0)
        for memory in memories:
            self.assertIn('event_id', memory)
            self.assertIn('content', memory)
            self.assertIn('event_type', memory)
            self.assertIn('timestamp', memory)
    
    def test_get_temporal_memories(self):
        """Test temporal memory retrieval"""
        # Store memories with different timestamps
        base_time = datetime.now()
        
        events = [
            MemoryEvent(
                event_id=f"temporal_event_{i}",
                timestamp=base_time - timedelta(hours=i),
                event_type="action",
                content=f"Action {i}",
                people=["Bob"],
                locations=["Office"],
                actions=["worked"],
                emotions=["focused"],
                needs_state={"achievement": 70.0},
                metadata={"hour": i}
            )
            for i in range(5)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Get memories from last 3 hours
        memories = self.memory_system.get_temporal_memories(
            start_time=base_time - timedelta(hours=3),
            end_time=base_time
        )
        
        self.assertGreater(len(memories), 0)
        self.assertLessEqual(len(memories), 4)  # Should be 4 events (0, 1, 2, 3 hours ago)
    
    def test_get_temporal_memories_with_type_filter(self):
        """Test temporal memory retrieval with event type filter"""
        # Store different types of events
        base_time = datetime.now()
        
        events = [
            MemoryEvent(
                event_id=f"conversation_{i}",
                timestamp=base_time - timedelta(hours=i),
                event_type="conversation",
                content=f"Conversation {i}",
                people=["Alice"],
                locations=["Home"],
                actions=["talked"],
                emotions=["happy"],
                needs_state={"social_connection": 80.0},
                metadata={"type": "conversation"}
            )
            for i in range(3)
        ]
        
        events.extend([
            MemoryEvent(
                event_id=f"action_{i}",
                timestamp=base_time - timedelta(hours=i),
                event_type="action",
                content=f"Action {i}",
                people=["Bob"],
                locations=["Office"],
                actions=["worked"],
                emotions=["focused"],
                needs_state={"achievement": 70.0},
                metadata={"type": "action"}
            )
            for i in range(3)
        ])
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Get only conversation events
        conversations = self.memory_system.get_temporal_memories(
            start_time=base_time - timedelta(hours=5),
            end_time=base_time,
            event_type="conversation"
        )
        
        self.assertEqual(len(conversations), 3)
        for memory in conversations:
            self.assertEqual(memory['event_type'], 'conversation')
    
    def test_get_needs_history(self):
        """Test needs history retrieval"""
        # Store events with different needs states
        base_time = datetime.now()
        
        events = [
            MemoryEvent(
                event_id=f"needs_event_{i}",
                timestamp=base_time - timedelta(hours=i),
                event_type="need_change",
                content=f"Need change {i}",
                people=[],
                locations=[],
                actions=["need_change"],
                emotions=[],
                needs_state={"hunger": 100.0 - (i * 10), "sleep": 100.0 - (i * 5)},
                metadata={"hour": i}
            )
            for i in range(5)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Get hunger history
        hunger_history = self.memory_system.get_needs_history(
            need_name="hunger",
            start_time=base_time - timedelta(hours=5),
            end_time=base_time
        )
        
        self.assertEqual(len(hunger_history), 5)
        for record in hunger_history:
            self.assertEqual(record['need_name'], 'hunger')
            self.assertIn('timestamp', record)
            self.assertIn('satisfaction_level', record)
    
    def test_get_needs_history_all_needs(self):
        """Test getting history for all needs"""
        # Store events with different needs
        base_time = datetime.now()
        
        events = [
            MemoryEvent(
                event_id=f"all_needs_event_{i}",
                timestamp=base_time - timedelta(hours=i),
                event_type="need_change",
                content=f"All needs change {i}",
                people=[],
                locations=[],
                actions=["need_change"],
                emotions=[],
                needs_state={
                    "hunger": 100.0 - (i * 10),
                    "sleep": 100.0 - (i * 5),
                    "creativity": 50.0 + (i * 5)
                },
                metadata={"hour": i}
            )
            for i in range(3)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Get all needs history
        all_history = self.memory_system.get_needs_history(
            start_time=base_time - timedelta(hours=5),
            end_time=base_time
        )
        
        self.assertEqual(len(all_history), 9)  # 3 events * 3 needs each
        
        # Check that we have all three needs
        need_names = set(record['need_name'] for record in all_history)
        self.assertIn('hunger', need_names)
        self.assertIn('sleep', need_names)
        self.assertIn('creativity', need_names)
    
    def test_get_memory_stats(self):
        """Test memory statistics"""
        # Store some test memories
        events = [
            MemoryEvent(
                event_id=f"stats_event_{i}",
                timestamp=datetime.now(),
                event_type="conversation" if i % 2 == 0 else "action",
                content=f"Test event {i}",
                people=["Alice"] if i % 2 == 0 else ["Bob"],
                locations=["Home"] if i % 2 == 0 else ["Office"],
                actions=["talked"] if i % 2 == 0 else ["worked"],
                emotions=["happy"] if i % 2 == 0 else ["focused"],
                needs_state={"hunger": 80.0, "sleep": 90.0},
                metadata={"index": i}
            )
            for i in range(5)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Get statistics
        stats = self.memory_system.get_memory_stats()
        
        self.assertIn('vector_db', stats)
        self.assertIn('graph_db', stats)
        self.assertIn('time_series_db', stats)
        
        # Check vector database stats
        self.assertIn('collection_count', stats['vector_db'])
        self.assertGreaterEqual(stats['vector_db']['collection_count'], 0)
        
        # Check time series database stats
        self.assertIn('event_count', stats['time_series_db'])
        self.assertIn('needs_records', stats['time_series_db'])
        self.assertIn('interaction_records', stats['time_series_db'])
        self.assertGreaterEqual(stats['time_series_db']['event_count'], 5)
    
    def test_person_relationships_without_neo4j(self):
        """Test person relationships when Neo4j is not available"""
        # Store some memories with people
        events = [
            MemoryEvent(
                event_id=f"person_event_{i}",
                timestamp=datetime.now(),
                event_type="conversation",
                content=f"Conversation with Alice {i}",
                people=["Alice"],
                locations=["Coffee Shop"],
                actions=["talked"],
                emotions=["happy"],
                needs_state={"social_connection": 80.0},
                metadata={"conversation_id": i}
            )
            for i in range(3)
        ]
        
        for event in events:
            self.memory_system.store_memory(event)
        
        # Try to get person relationships (should return empty dict without Neo4j)
        relationships = self.memory_system.get_person_relationships("Alice")
        
        # Should return empty dict when Neo4j is not available
        self.assertEqual(relationships, {})
    
    def test_error_handling(self):
        """Test error handling in memory operations"""
        # Test with invalid event
        invalid_event = MemoryEvent(
            event_id="invalid_event",
            timestamp=datetime.now(),
            event_type="invalid_type",
            content="",  # Empty content might cause issues
            people=[],
            locations=[],
            actions=[],
            emotions=[],
            needs_state={},
            metadata={}
        )
        
        # Should not raise an exception
        try:
            event_id = self.memory_system.store_memory(invalid_event)
            self.assertIsNotNone(event_id)
        except Exception as e:
            self.fail(f"Storing invalid event should not raise exception: {e}")
    
    def test_memory_persistence(self):
        """Test that memories persist across system restarts"""
        # Store some memories
        event = MemoryEvent(
            event_id="persistence_test",
            timestamp=datetime.now(),
            event_type="conversation",
            content="This should persist",
            people=["Alice"],
            locations=["Home"],
            actions=["talked"],
            emotions=["happy"],
            needs_state={"social_connection": 85.0},
            metadata={"test": "persistence"}
        )
        
        event_id = self.memory_system.store_memory(event)
        
        # Close the system
        self.memory_system.close()
        
        # Recreate the system with same paths
        new_memory_system = HybridMemorySystem(
            embeddings_model="llama3.2:3b-instruct-fp16",
            neo4j_uri="bolt://localhost:9999",
            neo4j_user="test",
            neo4j_password="test",
            vector_store_path=self.vector_store_path,
            time_series_path=self.time_series_path
        )
        
        # Try to retrieve the memory
        memories = new_memory_system.retrieve_semantic_memories("persist", top_k=5)
        
        # Should find the persisted memory
        found = False
        for memory in memories:
            if memory.get('event_id') == 'persistence_test':
                found = True
                break
        
        self.assertTrue(found, "Persisted memory should be retrievable")
        
        # Clean up
        new_memory_system.close()


if __name__ == '__main__':
    unittest.main() 