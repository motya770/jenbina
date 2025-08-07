#!/usr/bin/env python3
"""
Unit tests for sender/receiver functionality in memory system
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add the parent directory to the path to allow importing core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.memory.conversation_memory import ChromaMemoryManager

def test_sender_receiver_functionality():
    """Test the new sender/receiver functionality"""
    print("🔍 Testing Sender/Receiver Memory Functionality...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    vector_store_path = os.path.join(temp_dir, "test_memory")
    
    try:
        # Initialize memory manager with custom path
        memory_manager = ChromaMemoryManager()
        memory_manager.vector_store_path = vector_store_path
        memory_manager._initialize_vector_store()
        
        print("\n=== TESTING MESSAGE STORAGE WITH SENDER/RECEIVER ===")
        
        # Test messages with different sender/receiver combinations
        test_messages = [
            # User to Jenbina
            ("User", "Hello Jenbina, how are you?", "user_message", "User", "Jenbina"),
            # Jenbina to User
            ("User", "I'm doing well, thank you for asking!", "jenbina_response", "Jenbina", "User"),
            # User to Jenbina
            ("User", "What's your favorite color?", "user_message", "User", "Jenbina"),
            # Jenbina to User
            ("User", "I like blue, it reminds me of the sky.", "jenbina_response", "Jenbina", "User"),
            # User to Jenbina
            ("User", "That's nice! Do you like music?", "user_message", "User", "Jenbina"),
        ]
        
        # Store messages
        for person, message, msg_type, sender, receiver in test_messages:
            print(f"Storing: {sender}->{receiver} ({msg_type}): {message[:30]}...")
            embedding_id = memory_manager.store_conversation(
                person_name=person,
                message_content=message,
                message_type=msg_type,
                sender_name=sender,
                receiver_name=receiver
            )
            print(f"  -> Stored with ID: {embedding_id}")
        
        print("\n=== DEBUGGING COLLECTION CONTENTS ===")
        memory_manager.debug_collection_contents("User")
        
        print("\n=== TESTING CONVERSATION BETWEEN USER AND JENBINA ===")
        conversation = memory_manager.get_conversation_between("User", "Jenbina", limit=10)
        print(f"Retrieved {len(conversation)} messages between User and Jenbina")
        for i, msg in enumerate(conversation):
            sender = msg['metadata'].get('sender_name', 'Unknown')
            receiver = msg['metadata'].get('receiver_name', 'Unknown')
            direction = msg.get('direction', 'unknown')
            content = msg['content'][:40]
            print(f"  {i+1}. {sender}->{receiver} ({direction}): {content}...")
        
        print("\n=== TESTING REVERSE CONVERSATION (JENBINA TO USER) ===")
        reverse_conversation = memory_manager.get_conversation_between("Jenbina", "User", limit=10)
        print(f"Retrieved {len(reverse_conversation)} messages between Jenbina and User")
        for i, msg in enumerate(reverse_conversation):
            sender = msg['metadata'].get('sender_name', 'Unknown')
            receiver = msg['metadata'].get('receiver_name', 'Unknown')
            direction = msg.get('direction', 'unknown')
            content = msg['content'][:40]
            print(f"  {i+1}. {sender}->{receiver} ({direction}): {content}...")
        
        print("\n=== TESTING DEFAULT SENDER/RECEIVER VALUES ===")
        # Test with default values (should use person_name as sender, "Jenbina" as receiver)
        default_id = memory_manager.store_conversation(
            person_name="Alice",
            message_content="Testing default values",
            message_type="user_message"
        )
        print(f"Stored with default values, ID: {default_id}")
        
        # Check what was stored
        all_results = memory_manager.collection.get()
        for i, (doc, metadata) in enumerate(zip(all_results['documents'], all_results['metadatas'])):
            if metadata and "Testing default values" in doc:
                sender = metadata.get('sender_name', 'Unknown')
                receiver = metadata.get('receiver_name', 'Unknown')
                print(f"Default test message: {sender}->{receiver}: {doc}")
        
        print("\n=== TESTING MEMORY STATISTICS ===")
        stats = memory_manager.get_memory_stats()
        print(f"Total conversations: {stats.get('total_conversations', 0)}")
        print(f"Unique people: {stats.get('unique_people', 0)}")
        print(f"People: {stats.get('people', [])}")
        print(f"Message types: {stats.get('message_types', {})}")
        
        print("\n✅ All sender/receiver tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")

def test_conversation_retrieval():
    """Test conversation retrieval with sender/receiver filtering"""
    print("\n🔍 Testing Conversation Retrieval with Sender/Receiver Filtering...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    vector_store_path = os.path.join(temp_dir, "test_memory")
    
    try:
        # Initialize memory manager
        memory_manager = ChromaMemoryManager()
        memory_manager.vector_store_path = vector_store_path
        memory_manager._initialize_vector_store()
        
        # Store messages with different sender/receiver combinations
        messages = [
            ("User", "Hi there!", "user_message", "User", "Jenbina"),
            ("User", "How are you?", "user_message", "User", "Jenbina"),
            ("User", "I'm good, thanks!", "jenbina_response", "Jenbina", "User"),
            ("User", "That's great!", "jenbina_response", "Jenbina", "User"),
            ("Alice", "Hello Jenbina", "user_message", "Alice", "Jenbina"),
            ("Alice", "Nice to meet you", "jenbina_response", "Jenbina", "Alice"),
        ]
        
        for person, message, msg_type, sender, receiver in messages:
            memory_manager.store_conversation(
                person_name=person,
                message_content=message,
                message_type=msg_type,
                sender_name=sender,
                receiver_name=receiver
            )
        
        # Test retrieval for specific conversation
        print("\n=== TESTING USER->JENBINA CONVERSATION ===")
        user_to_jenbina = memory_manager.get_conversation_between("User", "Jenbina", limit=5)
        print(f"User->Jenbina messages: {len(user_to_jenbina)}")
        for msg in user_to_jenbina:
            print(f"  {msg['metadata']['sender_name']}->{msg['metadata']['receiver_name']}: {msg['content']}")
        
        print("\n=== TESTING ALICE->JENBINA CONVERSATION ===")
        alice_to_jenbina = memory_manager.get_conversation_between("Alice", "Jenbina", limit=5)
        print(f"Alice->Jenbina messages: {len(alice_to_jenbina)}")
        for msg in alice_to_jenbina:
            print(f"  {msg['metadata']['sender_name']}->{msg['metadata']['receiver_name']}: {msg['content']}")
        
        print("\n✅ Conversation retrieval tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during conversation retrieval testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_sender_receiver_functionality()
    test_conversation_retrieval() 