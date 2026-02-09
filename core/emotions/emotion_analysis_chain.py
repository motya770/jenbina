import json
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from typing import Dict, Any, Optional
from ..fix_llm_json import fix_llm_json


EMOTION_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["situation", "current_emotions", "current_needs"],
    template="""You are analyzing how a situation affects someone's emotions.

Current Emotional State:
{current_emotions}

Current Needs (Maslow):
{current_needs}

Situation that just occurred:
{situation}

Based on this situation, determine how each emotion should change.
Return ONLY a JSON object with emotion adjustments (positive to increase, negative to decrease).
Only include emotions that should change. Values should be between -30 and +30.

Available emotions: joy, sadness, anger, fear, surprise, disgust, trust, anticipation

Example: {{"joy": 15, "fear": -10, "surprise": 5}}

Return the JSON object:"""
)


def analyze_emotion_impact(llm, situation: str, emotion_system, maslow_needs=None) -> Dict[str, float]:
    """
    Analyze a situation and return emotion adjustments.

    Args:
        llm: Language model instance
        situation: Description of what happened (action taken, message received, etc.)
        emotion_system: Current EmotionSystem
        maslow_needs: Optional MaslowNeedsSystem for context

    Returns:
        Dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}
    """
    # Format current emotions
    emotion_state = emotion_system.get_emotional_state_summary()
    current_emotions_str = ", ".join(
        f"{name}: {val}" for name, val in emotion_state["emotions"].items()
    )

    # Format current needs
    if maslow_needs:
        needs_str = f"Overall satisfaction: {maslow_needs.get_overall_satisfaction():.1f}%"
        critical = maslow_needs.get_critical_needs()
        if critical:
            needs_str += f", Critical needs: {', '.join(critical)}"
    else:
        needs_str = "No needs data available"

    prompt_text = EMOTION_ANALYSIS_PROMPT.format(
        situation=situation,
        current_emotions=current_emotions_str,
        current_needs=needs_str,
    )

    response = llm.invoke([HumanMessage(content=prompt_text)])
    response_text = response.content if hasattr(response, "content") else str(response)

    # Parse the JSON response
    adjustments = fix_llm_json(broken_json=response_text, llm_json_mode=llm)

    # Validate: only keep known emotion keys with numeric values
    valid_emotions = {"joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"}
    validated = {}
    for key, val in adjustments.items():
        if key in valid_emotions:
            try:
                validated[key] = max(-30.0, min(30.0, float(val)))
            except (ValueError, TypeError):
                continue

    return validated
