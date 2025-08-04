"""
Memory Management Submodule

This submodule handles all aspects of the AI's memory system, including:
- Hybrid memory system (ChromaDB, Neo4j, SQLite)
- Conversation memory management
- Memory integration and retrieval
- Semantic and temporal memory queries
"""

from .hybrid_memory_system import (
    HybridMemorySystem,
    MemoryEvent,
    PersonNode,
    LocationNode
)

from .conversation_memory import (
    ChromaMemoryManager,
    ConversationMemory
)

from .memory_integration import (
    MemoryIntegration,
    create_memory_integration
)

__all__ = [
    # Hybrid memory system
    'HybridMemorySystem',
    'MemoryEvent',
    'PersonNode',
    'LocationNode',
    
    # Conversation memory (legacy)
    'ChromaMemoryManager',
    'ConversationMemory',
    
    # Memory integration
    'MemoryIntegration',
    'create_memory_integration'
] 