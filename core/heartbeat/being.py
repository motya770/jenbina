"""Construct the live being without any UI or process ownership concerns."""

from core.insights.insight_system import InsightSystem
from core.person.person import Person


class BeingStateError(Exception):
    """Saved person state could not be restored; never replace it silently."""


def build_person(state_json: str | None, llm, llm_json_mode, insight_llm) -> Person:
    """Restore her state, fill missing systems, and bind the insight LLM."""
    if state_json is None:
        person = Person()
        person.update_all_needs()
    else:
        try:
            person = Person.deserialize(state_json, llm_json_mode)
        except Exception as exc:
            raise BeingStateError("Jenbina's saved person state could not be read.") from exc

    if person.learning_system is None:
        person.init_learning_system(llm_json_mode)
    if person.goal_system is None:
        person.init_goal_system(llm_json_mode)
    if person.planning_system is None:
        person.init_planning_system(llm_json_mode)
    if person.inner_monologue is None:
        person.init_inner_monologue(llm)
    if person.social_cognition is None:
        person.init_social_cognition()
    if person.self_narrative is None:
        person.init_self_narrative()
    if person.curiosity_system is None:
        person.init_curiosity_system()
    if person.social_interaction_tracker is None:
        person.init_social_interaction_tracker()
    if person.insight_system is None:
        person.init_insight_system(insight_llm)
    else:
        person.insight_system = InsightSystem.from_dict(person.insight_system.to_dict(), insight_llm)
    return person
