from .action_decision_chain import create_action_decision_chain
from .meta_cognition import MetaCognitiveSystem
from typing import Dict, Any
import json

def create_meta_cognitive_action_chain(llm, person, world_description, meta_cognitive_system: MetaCognitiveSystem):
    """Enhanced action decision with meta-cognitive monitoring"""
    
    # Get original decision
    original_decision = create_action_decision_chain(llm, person, world_description)
    
    # Extract reasoning chain (you'll need to modify your original chain to return this)
    reasoning_chain = [
        "Analyzed current needs",
        "Evaluated available actions", 
        "Considered need priorities",
        f"Selected action: {original_decision.get('chosen_action', 'unknown')}"
    ]
    
    # Monitor the cognitive process
    cognitive_process = meta_cognitive_system.monitor_cognitive_process(
        process_type="action_decision",
        input_data={
            "needs": {name: need.satisfaction for name, need in person.needs[0].needs.items()},
            "world_description": world_description
        },
        output_data=original_decision,
        reasoning_chain=reasoning_chain,
        confidence=original_decision.get('confidence', 0.5)
    )
    
    # Reflect on the process
    reflection = meta_cognitive_system.reflect_on_process(cognitive_process)
    
    # Get thinking strategies for improvement
    current_situation = {
        "needs": {name: need.satisfaction for name, need in person.needs[0].needs.items()},
        "decision_context": "action_selection"
    }
    
    strategies = meta_cognitive_system.suggest_thinking_strategy(current_situation)
    
    # Enhanced decision with meta-cognitive insights
    enhanced_decision = {
        **original_decision,
        "meta_cognitive_insights": {
            "reflection": reflection.description if reflection else None,
            "suggested_improvements": strategies.get("strategies", []),
            "bias_mitigation": strategies.get("bias_mitigation", ""),
            "confidence_calibration": strategies.get("confidence_calibration", "")
        }
    }
    
    return enhanced_decision 