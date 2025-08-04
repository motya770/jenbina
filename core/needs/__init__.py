"""
Needs Management Submodule

This submodule handles all aspects of the AI's needs system, including:
- Maslow's Hierarchy of Needs implementation
- Need satisfaction and decay
- Growth stage progression
- Decision making based on needs
"""

from .maslow_needs import (
    MaslowNeedsSystem, 
    MaslowNeed, 
    NeedLevel, 
    NeedCategory,
    BasicNeeds, 
    Need, 
    create_basic_needs_chain
)

from .maslow_decision_chain import (
    create_maslow_decision_chain,
    create_maslow_action_executor,
    create_maslow_goal_setter
)

__all__ = [
    # Core needs classes
    'MaslowNeedsSystem',
    'MaslowNeed', 
    'NeedLevel',
    'NeedCategory',
    
    # Backward compatibility
    'BasicNeeds',
    'Need',
    'create_basic_needs_chain',
    
    # Decision making
    'create_maslow_decision_chain',
    'create_maslow_action_executor',
    'create_maslow_goal_setter'
] 