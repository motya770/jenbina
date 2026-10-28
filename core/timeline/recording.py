"""Recording helpers: turn runner state into timeline events.

Both ``core/ui/simulation.py`` (Streamlit) and ``core/simulation_runner.py``
(headless) call these at the same points of an iteration, so a day simulated
by the scheduler reads the same as one run from the screen.
"""

from __future__ import annotations

from typing import Optional

from .events import (
    EventLog,
    TimelineEvent,
    make_action,
    make_goal,
    make_mood,
    make_move,
    make_plan,
    make_thought,
    mood_changes,
)

GOAL_ADVANCE_MIN = 0.01


def record_thought(log: EventLog, inner_monologue) -> Optional[TimelineEvent]:
    """The current inner thought, or ``None`` when there is none."""
    if inner_monologue is None:
        return None
    thought = inner_monologue.get_current_thought()
    if thought is None or not getattr(thought, "content", ""):
        return None
    return log.record(make_thought(str(getattr(thought, "mode", "")), thought.content))


def record_move(log: EventLog, old_location: str, new_location: Optional[str]) -> Optional[TimelineEvent]:
    """A move, only when the location actually changed."""
    if not new_location or new_location == old_location:
        return None
    return log.record(make_move(old_location, new_location))


def record_action(log: EventLog, action_response: dict, satisfaction_before: float,
                  satisfaction_after: float, world_summary: dict) -> TimelineEvent:
    """The chosen action with its reasoning, lessons and world context."""
    response = action_response if isinstance(action_response, dict) else {"chosen_action": str(action_response)}
    summary = world_summary or {}
    location = (summary.get("location") or {}).get("name", "")
    time_of_day = (summary.get("time") or {}).get("time_of_day", "")
    weather = (summary.get("weather") or {}).get("description", "")
    temperature = (summary.get("weather") or {}).get("temperature", 0)
    return log.record(make_action(
        str(response.get("chosen_action", "") or ""),
        str(response.get("reasoning", "") or ""),
        response.get("lessons_applied"),
        satisfaction_before,
        satisfaction_after,
        location,
        time_of_day,
        weather,
        temperature,
    ))


def record_mood(log: EventLog, emotions_before: dict, emotions_after: dict, source: str) -> Optional[TimelineEvent]:
    """A mood shift, or ``None`` when nothing moved by a full point."""
    return log.record(make_mood(mood_changes(emotions_before, emotions_after), source))


def snapshot_goals(goal_system) -> dict:
    """``{description: (status, progress)}`` for every goal, ``{}`` without a system."""
    if goal_system is None:
        return {}
    return {g.description: (g.status, g.progress) for g in getattr(goal_system, "goals", [])}


def record_goal_changes(log: EventLog, before: dict, after: dict) -> list:
    """Goal events for what changed between two snapshots: advanced or
    completed goals first (in their original order), then new ones."""
    events = []
    for description, (old_status, old_progress) in before.items():
        if description not in after:
            continue
        new_status, new_progress = after[description]
        if new_status == "completed" and old_status != "completed":
            events.append(log.record(make_goal("completed", description, new_progress)))
        elif new_status == "active" and (new_progress - old_progress) >= GOAL_ADVANCE_MIN:
            events.append(log.record(make_goal("advanced", description, new_progress)))
    for description, (status, progress) in after.items():
        if description not in before:
            events.append(log.record(make_goal("created", description, progress)))
    return events


def record_plan_step(log: EventLog, step_result: Optional[str], goal_description: str,
                     step_description: str) -> Optional[TimelineEvent]:
    """The outcome of evaluating the current plan step."""
    if step_result == "step_completed":
        return log.record(make_plan("step_completed", goal_description, step_description))
    if step_result == "step_overridden":
        return log.record(make_plan("overridden", goal_description, step_description))
    return None


def record_replan(log: EventLog, plan) -> Optional[TimelineEvent]:
    """A replanned goal with its new first step."""
    if plan is None:
        return None
    first_step = plan.steps[0].description if getattr(plan, "steps", None) else ""
    return log.record(make_plan("replanned", plan.goal_description, first_step))


def record_plan_finished(log: EventLog, plan) -> TimelineEvent:
    return log.record(make_plan("completed", plan.goal_description, ""))
