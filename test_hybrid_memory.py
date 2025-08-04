#!/usr/bin/env python3
"""
Test script for the hybrid memory system
Demonstrates storing and retrieving memories across all three databases
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from datetime import datetime, timedelta
from hybrid_memory_system import HybridMemorySystem, MemoryEvent
import json

def test_hybrid_memory_system():
    """Test the hybrid memory system with sample data"""
    
    print("🧠 Initializing Hybrid Memory System...")
    
    # Initialize the hybrid memory system
    # Note: Neo4j will be disabled if not available, but other features will work
    memory_system = HybridMemorySystem(
        embeddings_model="llama3.2:3b-instruct-fp16",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j", 
        neo4j_password="password"
    )
    
    print("✅ Memory system initialized")
    
    # Create sample memory events
    print("\n📝 Creating sample memory events...")
    
    events = [
        MemoryEvent(
            event_id="event_001",
            timestamp=datetime.now() - timedelta(hours=2),
            event_type="conversation",
            content="Had a great conversation with Alice about artificial intelligence and the future of technology. She seemed very knowledgeable and enthusiastic about the topic.",
            people=["Alice"],
            locations=["Coffee Shop"],
            actions=["discussed", "learned"],
            emotions=["excited", "curious"],
            needs_state={"hunger": 85.0, "sleep": 90.0, "safety": 95.0},
            metadata={"topic": "AI", "duration_minutes": 45}
        ),
        
        MemoryEvent(
            event_id="event_002", 
            timestamp=datetime.now() - timedelta(hours=1),
            event_type="action",
            content="Went for a walk in the park and enjoyed the beautiful weather. Saw some children playing and felt happy.",
            people=[],
            locations=["Central Park"],
            actions=["walked", "observed"],
            emotions=["happy", "peaceful"],
            needs_state={"hunger": 70.0, "sleep": 85.0, "safety": 90.0},
            metadata={"weather": "sunny", "duration_minutes": 30}
        ),
        
        MemoryEvent(
            event_id="event_003",
            timestamp=datetime.now() - timedelta(minutes=30),
            event_type="conversation", 
            content="Met Bob at the library. He was reading a book about psychology and we briefly discussed human behavior patterns.",
            people=["Bob"],
            locations=["Library"],
            actions=["met", "discussed"],
            emotions=["interested", "friendly"],
            needs_state={"hunger": 60.0, "sleep": 80.0, "safety": 85.0},
            metadata={"topic": "psychology", "duration_minutes": 15}
        )
    ]
    
    # Store all events
    for event in events:
        event_id = memory_system.store_memory(event)
        print(f"✅ Stored event: {event_id} - {event.event_type}")
    
    print(f"\n📊 Memory Statistics:")
    stats = memory_system.get_memory_stats()
    print(json.dumps(stats, indent=2))
    
    # Test semantic memory retrieval
    print(f"\n🔍 Testing semantic memory retrieval...")
    semantic_results = memory_system.retrieve_semantic_memories("artificial intelligence", top_k=3)
    print(f"Found {len(semantic_results)} semantic matches:")
    for i, memory in enumerate(semantic_results, 1):
        print(f"  {i}. {memory['content'][:100]}...")
    
    # Test temporal memory retrieval
    print(f"\n⏰ Testing temporal memory retrieval...")
    temporal_results = memory_system.get_temporal_memories(
        start_time=datetime.now() - timedelta(hours=3),
        end_time=datetime.now()
    )
    print(f"Found {len(temporal_results)} temporal matches:")
    for i, memory in enumerate(temporal_results, 1):
        print(f"  {i}. {memory['event_type']}: {memory['content'][:80]}...")
    
    # Test person relationship retrieval (if Neo4j is available)
    if memory_system.graph_driver:
        print(f"\n👥 Testing person relationship retrieval...")
        alice_relationships = memory_system.get_person_relationships("Alice")
        print(f"Alice's relationships: {json.dumps(alice_relationships, indent=2, default=str)}")
    else:
        print(f"\n⚠️  Neo4j not available - skipping relationship tests")
    
    # Test needs history
    print(f"\n📈 Testing needs history...")
    needs_history = memory_system.get_needs_history(
        need_name="hunger",
        start_time=datetime.now() - timedelta(hours=3)
    )
    print(f"Hunger history: {len(needs_history)} records")
    for record in needs_history[:3]:  # Show first 3 records
        print(f"  {record['timestamp']}: {record['satisfaction_level']}%")
    
    # Clean up
    memory_system.close()
    print(f"\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_hybrid_memory_system() 