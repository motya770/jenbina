#!/usr/bin/env python3
"""
Script to clear ChromaDB database and reset collections
Use this if you encounter collection conflicts or want to start fresh
"""

import os
import shutil
import chromadb
from chromadb.config import Settings

def clear_chromadb():
    """Clear the ChromaDB database and reset collections"""
    
    # Path to the ChromaDB database
    db_path = "jenbina_memory"
    
    print("🧹 Clearing ChromaDB database...")
    
    try:
        # Try to connect to existing database
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # List all collections
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        
        for collection in collections:
            print(f"  - {collection.name}")
        
        # Delete all collections
        for collection in collections:
            try:
                client.delete_collection(collection.name)
                print(f"✅ Deleted collection: {collection.name}")
            except Exception as e:
                print(f"❌ Failed to delete collection {collection.name}: {e}")
        
        print("✅ All collections deleted successfully")
        
    except Exception as e:
        print(f"⚠️  Error connecting to database: {e}")
        print("Attempting to delete database directory...")
    
    # Delete the entire database directory
    if os.path.exists(db_path):
        try:
            shutil.rmtree(db_path)
            print(f"✅ Deleted database directory: {db_path}")
        except Exception as e:
            print(f"❌ Failed to delete database directory: {e}")
    else:
        print(f"ℹ️  Database directory does not exist: {db_path}")
    
    # Create fresh database
    try:
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create a new collection
        collection = client.create_collection("jenbina_conversations")
        print("✅ Created fresh collection: jenbina_conversations")
        
        print("🎉 ChromaDB database cleared and reset successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create fresh database: {e}")

def check_chromadb_status():
    """Check the current status of ChromaDB"""
    
    db_path = "jenbina_memory"
    
    print("🔍 Checking ChromaDB status...")
    
    if not os.path.exists(db_path):
        print("ℹ️  Database directory does not exist")
        return
    
    try:
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        collections = client.list_collections()
        print(f"📊 Found {len(collections)} collections:")
        
        for collection in collections:
            count = collection.count()
            print(f"  - {collection.name}: {count} documents")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_chromadb_status()
    else:
        print("This script will clear the ChromaDB database and reset all collections.")
        print("This will delete all stored conversation data!")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            clear_chromadb()
        else:
            print("Operation cancelled.")
            print("Use 'python clear_chromadb.py check' to check database status without clearing.")
