"""The status rail beside the timeline: the Now card (stage pill, portrait,
vitals), the heartbeat card and the mind card.

``StatusRail`` bundles the ``st.empty()`` placeholders so the simulation
runner can update the screen without knowing the page layout; ``NullRail``
is the silent stand-in for headless runs and tests.
"""

from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from core.heartbeat.host import HeartStatus
from core.timeline import shorten
from core.ui.pixel_theme import stage_pill_html
from core.ui.simulation import (
    display_jenbina_image,
    get_jenbina_image_for_emotion,
    render_emotion_chips,
    render_mood_indicator,
    render_needs_bars,
)

HOME = "Jenbina's House"
PORTRAIT_RAIL_WIDTH = 192
DOING_LIMIT = 60
MIND_LIST_LIMIT = 5
IDLE_STAGE = "idle"


def env_line_html(world_summary: dict | None) -> str:
    """``Jenbina's House · Night · Clear skies, 15°C``; the bare home
    name when there is no world summary yet."""
    if not world_summary:
        return HOME
    location = (world_summary.get("location") or {}).get("name", HOME)
    time_of_day = str((world_summary.get("time") or {}).get("time_of_day", "") or "")
    weather = str((world_summary.get("weather") or {}).get("description", "") or "")
    temperature = (world_summary.get("weather") or {}).get("temperature", 0)
    parts = [html.escape(str(location))]
    if time_of_day:
        parts.append(html.escape(time_of_day.capitalize()))
    if weather:
        try:
            degrees = float(temperature or 0)
        except (TypeError, ValueError):
            degrees = 0.0
        parts.append(f"{html.escape(weather)}, {degrees:.0f}°C")
    return '<div class="px-env-line">' + " · ".join(parts) + "</div>"


class StatusRail:
    """Handles on the Now card's placeholders, plus the timeline's live slot."""

    def __init__(self, stage_slot, portrait_slot, vitals_slot, live_slot=None):
        self.stage_slot = stage_slot
        self.portrait_slot = portrait_slot
        self.vitals_slot = vitals_slot
        self.live_slot = live_slot
        self.world_summary = None
        self.doing = None
        self.goal = None

    def stage(self, text: str) -> None:
        """Show the system stage in the pill and remember it for reruns."""
        self.stage_slot.markdown(stage_pill_html(text), unsafe_allow_html=True)
        try:
            st.session_state["system_stage"] = text
        except Exception:  # noqa: BLE001 - outside a Streamlit script run
            pass

    def portrait(self, image_path_or_state: str, caption: str | None = None) -> None:
        with self.portrait_slot.container():
            display_jenbina_image(image_path_or_state, caption=caption, width=PORTRAIT_RAIL_WIDTH)

    def refresh(self, person) -> None:
        """Redraw mood, place, doing/goal lines, needs bars and emotion chips."""
        with self.vitals_slot.container():
            render_mood_indicator(person)
            st.markdown(env_line_html(self.world_summary), unsafe_allow_html=True)
            lines = []
            if self.doing:
                lines.append(f"Doing: {shorten(str(self.doing), DOING_LIMIT)}")
            if self.goal:
                lines.append(f"Goal: {self.goal}")
            if lines:
                st.markdown(
                    '<div class="px-now-lines">' + "<br>".join(html.escape(line) for line in lines) + "</div>",
                    unsafe_allow_html=True,
                )
            render_needs_bars(person)
            render_emotion_chips(person)

    def live_row(self, html_: str) -> None:
        """Append a row to the timeline's live slot (a thought or action in progress)."""
        if self.live_slot is None:
            return
        with self.live_slot:
            st.markdown(html_, unsafe_allow_html=True)


class NullRail(StatusRail):
    """A rail that draws nothing: headless runs and tests."""

    def __init__(self):
        super().__init__(None, None, None, None)

    def stage(self, text: str) -> None:
        return None

    def portrait(self, image_path_or_state: str, caption: str | None = None) -> None:
        return None

    def refresh(self, person) -> None:
        return None

    def live_row(self, html_: str) -> None:
        return None


def _card_title(text: str) -> None:
    st.markdown(f'<div class="px-card-title">{html.escape(text)}</div>', unsafe_allow_html=True)


def render_status_rail(person, world_summary: dict | None, doing: str | None, goal: str | None,
                       live_slot=None) -> StatusRail:
    """Draw the Now card and return the handles the runner updates."""
    with st.container(border=True):
        head, pill = st.columns([2, 1])
        with head:
            _card_title("Now")
        with pill:
            stage_slot = st.empty()
        portrait_slot = st.empty()
        vitals_slot = st.empty()
    st.session_state["_stage_placeholder"] = stage_slot
    rail = StatusRail(stage_slot, portrait_slot, vitals_slot, live_slot)
    rail.world_summary, rail.doing, rail.goal = world_summary, doing, goal
    rail.stage(st.session_state.get("system_stage") or IDLE_STAGE)
    rail.portrait(get_jenbina_image_for_emotion(person), caption=person.name)
    rail.refresh(person)
    return rail


def heartbeat_lines(status: HeartStatus, now: datetime) -> list[str]:
    """Describe her phase, beat timing and any pause in her rhythm."""
    lines = [f"● {status.phase} · since {status.phase_since:%H:%M}"]
    if status.busy:
        lines.append(status.stage)
    elif status.phase == "awake":
        if status.last_beat_at is None:
            timing = "no moment yet"
        else:
            minutes = max(0, int((now - status.last_beat_at).total_seconds() // 60))
            timing = f"last moment {minutes} min ago"
        if status.next_beat_at is not None:
            minutes = max(0, int((status.next_beat_at - now).total_seconds() // 60))
            timing += f" · next in {minutes} min"
        lines.append(timing)
    if status.note == "daily_cap":
        lines.append("daily limit reached · resting until tomorrow")
    elif status.note == "backoff":
        lines.append("heart is retrying after errors")
    return lines


def render_heartbeat_card(status: HeartStatus, admin: bool, now: datetime | None = None) -> bool:
    """Draw her rhythm and let admins request a moment of life."""
    with st.container(border=True):
        _card_title("Heartbeat")
        for line in heartbeat_lines(status, now or datetime.now()):
            st.write(line)
        if admin:
            return st.button(
                "Step once", type="primary", use_container_width=True,
                disabled=status.phase == "asleep" or status.note == "daily_cap",
            )
    return False


def _goal_lines(person) -> None:
    goals = []
    if getattr(person, "goal_system", None) is not None:
        goals = person.goal_system.get_goal_stats().get("goals", [])
    if not goals:
        st.write("No goals yet.")
        return
    for goal in goals[:MIND_LIST_LIMIT]:
        st.write(f"{goal['description']} · {float(goal.get('progress', 0)):.0%}")


def _plan_lines(person) -> None:
    plans = []
    if getattr(person, "planning_system", None) is not None:
        plans = person.planning_system.get_planning_stats().get("plans", [])
    if not plans:
        st.write("No plan.")
        return
    plan = plans[0]
    steps = plan.get("steps", [])
    index = int(plan.get("current_step_index", 0) or 0)
    st.write(plan.get("goal_description", ""))
    if steps and 0 <= index < len(steps):
        st.write(f"step {index + 1} of {len(steps)}: {steps[index].get('description', '')}")


def _lesson_lines(person) -> None:
    lessons = []
    if getattr(person, "learning_system", None) is not None:
        lessons = person.learning_system.get_learning_stats().get("lessons", [])
    if not lessons:
        st.write("Nothing learned yet.")
        return
    for lesson in lessons[:MIND_LIST_LIMIT]:
        st.write(f"{lesson['description']} · {float(lesson.get('confidence', 0)):.0%}")


def _about_you_lines(person, display_name: str) -> None:
    if getattr(person, "social_cognition", None) is None:
        st.write("Nothing known yet.")
        return
    # Read only: this runs outside the mind lock on every refresh, and adding
    # a model here could collide with a beat that is saving her state.
    model = person.social_cognition.models.get(display_name)
    if model is None:
        st.write("Nothing known yet.")
        return
    relationship = model.relationship
    st.write(f"Seems: {model.inferred_emotional_state}")
    st.write(
        f"Trust {relationship.trust:.0f} · closeness {relationship.closeness:.0f} · conflict {relationship.conflict:.0f}"
    )
    interests = sorted((model.interests or {}).items(), key=lambda kv: kv[1], reverse=True)[:3]
    if interests:
        st.write("Interests: " + ", ".join(topic for topic, _ in interests))


def render_mind_card(person, display_name: str) -> None:
    """Goals, plans, lessons and what she knows about the user, as four tabs."""
    with st.container(border=True):
        goals_tab, plans_tab, lessons_tab, you_tab = st.tabs(["Goals", "Plans", "Lessons", "About you"])
        with goals_tab:
            _goal_lines(person)
        with plans_tab:
            _plan_lines(person)
        with lessons_tab:
            _lesson_lines(person)
        with you_tab:
            _about_you_lines(person, display_name)
