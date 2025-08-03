#!/usr/bin/env python3

import sys
import os
sys.path.append('core')

from conversation_memory import ChromaMemoryManager

def clear_memory():
    print("🗑️ Clearing memory collection...")
    
    # Initialize memory manager
    memory_manager = ChromaMemoryManager()
    
    # Clear all memory
    memory_manager.clear_memory()
    
    print("✅ Memory cleared successfully!")

if __name__ == "__main__":
    clear_memory() 