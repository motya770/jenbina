#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path to allow importing core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.memory.conversation_memory import ChromaMemoryManager

def test_memory():
    print("🔍 Testing Memory System...")
    
    # Initialize memory manager
    memory_manager = ChromaMemoryManager()
    
    # Debug the collection contents
    print("\n=== DEBUGGING COLLECTION CONTENTS ===")
    memory_manager.debug_collection_contents("User")
    
    # Test storing a few messages
    print("\n=== TESTING MESSAGE STORAGE ===")
    
    # Store some test messages
    test_messages = [
        ("User", "Hi, I am matthew", "user_message"),
        ("User", "Hello Matthew! Nice to meet you. I'm Jenbina.", "jenbina_response"),
        ("User", "What is my name", "user_message"),
        ("User", "Ah, Matthew! Nice to meet you. I'm Jenbina.", "jenbina_response"),
        ("User", "Lets talk about C++", "user_message"),
    ]
    
    for person, message, msg_type in test_messages:
        print(f"Storing: {person} - {msg_type} - {message[:50]}...")
        embedding_id = memory_manager.store_conversation(
            person_name=person,
            message_content=message,
            message_type=msg_type
        )
        print(f"  -> Stored with ID: {embedding_id}")
    
    # Now check what's in the collection
    print("\n=== AFTER STORING MESSAGES ===")
    memory_manager.debug_collection_contents("User")
    
    # Test retrieval
    print("\n=== TESTING RETRIEVAL ===")
    context = memory_manager.retrieve_relevant_context(
        person_name="User",
        current_message="test",
        top_k=5
    )
    
    print(f"Retrieved {len(context)} context documents")
    for i, doc in enumerate(context):
        print(f"  {i+1}. {doc['content'][:50]}... (Type: {doc['metadata']['message_type']})")

if __name__ == "__main__":
    test_memory() 