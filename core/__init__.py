"""
Jenbina AGI System - Core Module

This is the main core module for the Jenbina AGI system, providing access to all
submodules and components needed for artificial general intelligence.

Submodules:
- needs: Maslow's hierarchy of needs and decision making
- memory: Hybrid memory system (ChromaDB, Neo4j, SQLite)
- person: Person representation and conversation management
- cognition: Meta-cognition and decision making processes
- environment: World simulation and environment management
- interaction: Chat handling and user interaction
"""

# Import from submodules
from .needs import (
    MaslowNeedsSystem, MaslowNeed, NeedLevel, NeedCategory,
    BasicNeeds, Need, create_basic_needs_chain,
    create_maslow_decision_chain, create_maslow_action_executor,
    create_maslow_goal_setter
)

from .memory import (
    HybridMemorySystem, MemoryEvent, PersonNode, LocationNode,
    ChromaMemoryManager, ConversationMemory,
    MemoryIntegration, create_memory_integration
)

from .person import (
    Person, Message, Conversation
)

from .cognition import (
    MetaCognitiveSystem, CognitiveProcess, MetaCognitiveInsight,
    create_action_decision_chain,
    create_meta_cognitive_action_chain, create_state_analysis_system,
    create_asimov_check_system
)

from .environment import (
    EnvironmentSimulator, EnvironmentState, WeatherData, TimeData,
    WorldState, create_world_description_system,
    PaloAltoLocationSystem, Location, Neighborhood,
    DynamicEventsSystem, Event, Venue
)

from .interaction import (
    handle_chat_interaction, basic_needs_to_json, create_metadata_from_person_state
)

# Main application components - import separately to avoid circular imports
# from .app import main as run_app
# from .engine import main as run_engine

__version__ = "1.0.0"
__author__ = "Jenbina AGI Team"

__all__ = [
    # Needs system
    'MaslowNeedsSystem', 'MaslowNeed', 'NeedLevel', 'NeedCategory',
    'BasicNeeds', 'Need', 'create_basic_needs_chain',
    'create_maslow_decision_chain', 'create_maslow_action_executor',
    'create_maslow_goal_setter',
    
    # Memory system
    'HybridMemorySystem', 'MemoryEvent', 'PersonNode', 'LocationNode',
    'ChromaMemoryManager', 'ConversationMemory',
    'MemoryIntegration', 'create_memory_integration',
    
    # Person management
    'Person', 'Message', 'Conversation',
    
    # Cognition system
    'MetaCognitiveSystem', 'CognitiveProcess', 'MetaCognitiveInsight',
    'create_action_decision_chain',
    'create_meta_cognitive_action_chain', 'create_state_analysis_system',
    'create_asimov_check_system',
    
    # Environment system
    'EnvironmentSimulator', 'EnvironmentState', 'WeatherData', 'TimeData',
    'WorldState', 'create_world_description_system',
    'PaloAltoLocationSystem', 'Location', 'Neighborhood',
    'DynamicEventsSystem', 'Event', 'Venue',
    
    # Interaction system
    'handle_chat_interaction', 'basic_needs_to_json', 'create_metadata_from_person_state'
]
