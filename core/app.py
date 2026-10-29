"""
Jenbina - AGI Simulation Streamlit App

Main entry point — the home screen: the conversation with Jenbina as one
timeline (messages and her life events), beside a live status rail.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui.shared_init import require_auth, init_llm, save_person_state
from core.ui.pixel_theme import inject_pixel_css
from core.ui.chat import _get_user_display_name, ensure_outreach, get_event_log, handle_user_input
from core.ui.rail import render_mind_card, render_run_controls, render_status_rail
from core.ui.simulation import run_simulation_loop
from core.ui.timeline import (
    FILTERS,
    TIMELINE_HEIGHT,
    TIMELINE_LIMIT,
    build_timeline,
    render_timeline,
    scroll_timeline_to_bottom,
)

MESSAGE_WINDOW = 100
COLUMN_RATIO = [1.55, 1]


def _latest_world(session):
    """``(world_summary, chosen_action)`` of the last iteration this session, or ``(None, None)``."""
    history = session.get("simulation_history") or []
    if not history:
        return None, None
    last = history[-1]
    decision = last.get("action_decision") or {}
    doing = decision.get("chosen_action") if isinstance(decision, dict) else None
    return last.get("world_summary"), doing


def _top_goal(person):
    if getattr(person, "goal_system", None) is None:
        return None
    goals = person.goal_system.get_goal_stats().get("goals", [])
    return goals[0]["description"] if goals else None


def main():
    # Use custom favicon if present, otherwise emoji
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _icon = os.path.join(_root, "assets", "favicon.png")
    page_icon = _icon if os.path.isfile(_icon) else "👧"
    st.set_page_config(page_title="Jenbina", page_icon=page_icon, layout="wide")
    inject_pixel_css(wide=True)

    if not require_auth():
        return

    llm, llm_json_mode = init_llm()
    person = st.session_state.person
    meta_cognitive_system = st.session_state.meta_cognitive_system
    memory_manager = st.session_state.memory_manager

    st.title("👧 Jenbina")

    with st.sidebar:
        st.session_state.debug_mode = st.checkbox(
            "🔧 Debug Mode", value=True,
            help="Show debug controls on the Environment page",
        )

    event_log = get_event_log()
    display_name = _get_user_display_name()
    ensure_outreach(person, llm)
    world_summary, doing = _latest_world(st.session_state)
    goal = _top_goal(person)

    left, rail_col = st.columns(COLUMN_RATIO, gap="medium")

    # ── Left: the timeline ────────────────────────────────────────────────
    with left:
        st.markdown("**Today with Jenbina**")
        filter_name = st.radio("Show", FILTERS, horizontal=True, label_visibility="collapsed", key="timeline_filter")
        timeline = st.container(height=TIMELINE_HEIGHT)
        with timeline:
            items = build_timeline(
                person.get_conversation_history(display_name, count=MESSAGE_WINDOW),
                event_log.recent(TIMELINE_LIMIT),
                person.name,
                filter_name,
            )
            render_timeline(items)
            live_slot = st.container()
        user_input = st.chat_input("Talk to Jenbina...")
        scroll_timeline_to_bottom()

    # ── Right: the status rail ────────────────────────────────────────────
    with rail_col:
        rail = render_status_rail(person, world_summary, doing, goal, live_slot=live_slot)
        controls = render_run_controls()
        render_mind_card(person, display_name)

    # ── A message from the user ───────────────────────────────────────────
    if user_input:
        with timeline:
            handle_user_input(person, llm, memory_manager, False, user_input)
        save_person_state()
        st.rerun()

    # ── Let her live ──────────────────────────────────────────────────────
    auto_start = False
    if "simulation_auto_started" not in st.session_state:
        st.session_state.simulation_auto_started = True
        auto_start = True

    if controls["run_loop"] or controls["single_run"] or auto_start:
        iterations = controls["num_iterations"] if controls["run_loop"] else 1
        results = run_simulation_loop(
            person=person,
            llm_json_mode=llm_json_mode,
            meta_cognitive_system=meta_cognitive_system,
            iterations=iterations,
            delay_seconds=controls["delay_seconds"],
            rail=rail,
            event_log=event_log,
        )
        st.session_state.simulation_completed = True
        save_person_state()
        st.rerun()

    save_person_state()


if __name__ == "__main__":
    main()
else:
    main()
