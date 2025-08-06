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
    
    # Store some test messages with sender/receiver information
    test_messages = [
        ("User", "Hi, I am matthew", "user_message", "User", "Jenbina"),
        ("User", "Hello Matthew! Nice to meet you. I'm Jenbina.", "jenbina_response", "Jenbina", "User"),
        ("User", "What is my name", "user_message", "User", "Jenbina"),
        ("User", "Ah, Matthew! Nice to meet you. I'm Jenbina.", "jenbina_response", "Jenbina", "User"),
        ("User", "Lets talk about C++", "user_message", "User", "Jenbina"),
    ]
    
    for person, message, msg_type, sender, receiver in test_messages:
        print(f"Storing: {person} - {msg_type} - {sender}->{receiver} - {message[:50]}...")
        embedding_id = memory_manager.store_conversation(
            person_name=person,
            message_content=message,
            message_type=msg_type,
            sender_name=sender,
            receiver_name=receiver
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
    
    # Test the new conversation between functionality
    print("\n=== TESTING CONVERSATION BETWEEN ===")
    conversation = memory_manager.get_conversation_between("User", "Jenbina", limit=10)
    print(f"Retrieved {len(conversation)} messages between User and Jenbina")
    for i, msg in enumerate(conversation):
        sender = msg['metadata'].get('sender_name', 'Unknown')
        receiver = msg['metadata'].get('receiver_name', 'Unknown')
        direction = msg.get('direction', 'unknown')
        print(f"  {i+1}. {sender}->{receiver} ({direction}): {msg['content'][:50]}...")
    
    # Test reverse direction
    print("\n=== TESTING REVERSE CONVERSATION ===")
    reverse_conversation = memory_manager.get_conversation_between("Jenbina", "User", limit=10)
    print(f"Retrieved {len(reverse_conversation)} messages between Jenbina and User")
    for i, msg in enumerate(reverse_conversation):
        sender = msg['metadata'].get('sender_name', 'Unknown')
        receiver = msg['metadata'].get('receiver_name', 'Unknown')
        direction = msg.get('direction', 'unknown')
        print(f"  {i+1}. {sender}->{receiver} ({direction}): {msg['content'][:50]}...")

if __name__ == "__main__":
    test_memory() 