"""
Cognition and Decision Making Submodule

This submodule handles all aspects of the AI's cognitive processes, including:
- Meta-cognition and self-reflection
- Action decision making
- State analysis and reasoning
- Asimov's laws compliance checking
"""

from .meta_cognition import (
    MetaCognitiveSystem,
    CognitiveProcess,
    MetaCognitiveInsight
)

from .action_decision_chain import (
    create_action_decision_chain
)

from .enhanced_action_decision_chain import (
    create_meta_cognitive_action_chain
)

from .state_analysis_chain import (
    create_state_analysis_system
)

from .asimov_check_chain import (
    create_asimov_check_system
)

__all__ = [
    # Meta-cognition
    'MetaCognitiveSystem',
    'CognitiveProcess',
    'MetaCognitiveInsight',
    
    # Action decision making
    'create_action_decision_chain',
    'create_meta_cognitive_action_chain',
    
    # State analysis
    'create_state_analysis_system',
    
    # Safety and compliance
    'create_asimov_check_system'
] 