from .action_decision_chain import create_action_decision_chain
from .meta_cognition import MetaCognitiveSystem
from typing import Dict, Any, Optional
import json
from ..environment.world_state import WorldState

def create_meta_cognitive_action_chain(llm, person, world_description, meta_cognitive_system: MetaCognitiveSystem, world_state: Optional[WorldState] = None):
    """Enhanced action decision with meta-cognitive monitoring"""
    
    # Get original decision with world state information
    action_chain = create_action_decision_chain(llm)
    original_decision = action_chain(person, world_description, llm, world_state)
    
    # Extract reasoning chain (you'll need to modify your original chain to return this)
    reasoning_chain = [
        "Analyzed current needs",
        "Evaluated available actions", 
        "Considered need priorities",
        "Analyzed world state information" if world_state else "No world state information available",
        f"Selected action: {original_decision.get('chosen_action', 'unknown')}"
    ]
    
    # Prepare input data including world state and emotions
    input_data = {
        "needs": {name: need.satisfaction for name, need in person.maslow_needs.needs.items()},
        "emotions": person.emotion_system.get_emotional_state_summary(),
        "world_description": world_description
    }
    
    # Add world state information if available
    if world_state:
        input_data["world_state"] = {
            "location": world_state.current_location_info.name if world_state.current_location_info else "Unknown location",
            "time_of_day": world_state.time_data.time_of_day if world_state.time_data else "unknown",
            "weather": world_state.weather_data.description if world_state.weather_data else "unknown",
            "nearby_locations_count": len(world_state.nearby_locations),
            "open_locations_count": len(world_state.open_locations),
            "current_events_count": len(world_state.current_events),
            "mood_factors": world_state.mood_factors
        }
    
    # Monitor the cognitive process
    cognitive_process = meta_cognitive_system.monitor_cognitive_process(
        process_type="action_decision",
        input_data=input_data,
        output_data=original_decision,
        reasoning_chain=reasoning_chain,
        confidence=original_decision.get('confidence', 0.5)
    )
    
    # Reflect on the process
    reflection = meta_cognitive_system.reflect_on_process(cognitive_process)
    
    # Get thinking strategies for improvement
    current_situation = {
        "needs": {name: need.satisfaction for name, need in person.maslow_needs.needs.items()},
        "emotions": person.emotion_system.get_emotional_state_summary(),
        "decision_context": "action_selection",
        "world_state_available": world_state is not None
    }
    
    strategies = meta_cognitive_system.suggest_thinking_strategy(current_situation)
    
    # Enhanced decision with meta-cognitive insights
    enhanced_decision = {
        **original_decision,
        "meta_cognitive_insights": {
            "reflection": reflection.description if reflection else None,
            "suggested_improvements": strategies.get("strategies", []),
            "bias_mitigation": strategies.get("bias_mitigation", ""),
            "confidence_calibration": strategies.get("confidence_calibration", ""),
            "world_state_considered": world_state is not None
        }
    }
    
    return enhanced_decision 