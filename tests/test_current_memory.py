#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path to allow importing core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.memory.conversation_memory import ChromaMemoryManager

def test_current_memory():
    print("🔍 Testing Current Memory State...")
    
    # Initialize memory manager
    memory_manager = ChromaMemoryManager()
    
    # Debug the collection contents
    print("\n=== CURRENT COLLECTION CONTENTS ===")
    memory_manager.debug_collection_contents()
    
    # Test storing with current chat_handler logic
    print("\n=== TESTING CURRENT CHAT HANDLER LOGIC ===")
    
    # Simulate what chat_handler does
    print("1. Storing user message with person_name='User'...")
    user_id = memory_manager.store_conversation(
        person_name="User",
        message_content="Test user message",
        message_type="user_message"
    )
    print(f"   -> Stored with ID: {user_id}")
    
    print("2. Storing Jenbina response with person_name='Jenbina'...")
    jenbina_id = memory_manager.store_conversation(
        person_name="Jenbina",
        message_content="Test Jenbina response",
        message_type="jenbina_response"
    )
    print(f"   -> Stored with ID: {jenbina_id}")
    
    # Check what's in collection now
    print("\n=== AFTER STORING WITH CURRENT LOGIC ===")
    memory_manager.debug_collection_contents()
    
    # Test retrieval for User
    print("\n=== TESTING RETRIEVAL FOR 'User' ===")
    user_context = memory_manager.retrieve_relevant_context(
        person_name="User",
        current_message="test",
        top_k=5
    )
    print(f"Found {len(user_context)} documents for 'User'")
    
    # Test retrieval for Jenbina
    print("\n=== TESTING RETRIEVAL FOR 'Jenbina' ===")
    jenbina_context = memory_manager.retrieve_relevant_context(
        person_name="Jenbina",
        current_message="test",
        top_k=5
    )
    print(f"Found {len(jenbina_context)} documents for 'Jenbina'")

if __name__ == "__main__":
    test_current_memory() 