"""Jenbina's home screen: a private conversation beside her shared live state."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui.shared_init import require_auth, init_llm, get_host
from core.ui.admin import is_admin
from core.ui.pixel_theme import inject_pixel_css
from core.ui.chat import ensure_greeting, handle_user_input, update_system_stage
from core.ui.live import REFRESH_SECONDS, draw_guarded
from core.ui.rail import render_heartbeat_card, render_mind_card, render_status_rail
from core.ui.simulation import _get_image_path
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


def _latest_world(history):
    """World and chosen action from the host's most recent moment."""
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
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    page_icon = next(
        (path for path in (os.path.join(_root, "assets", "jenbina_nav.png"),
                           os.path.join(_root, "assets", "favicon.png")) if os.path.isfile(path)),
        None,
    )
    st.set_page_config(page_title="Jenbina", page_icon=page_icon, layout="wide")
    inject_pixel_css(wide=True)

    if not require_auth():
        return

    host = get_host()
    user = st.session_state.current_user
    person_key = host.person_key(user)
    llm, _ = init_llm()
    memory_manager = st.session_state.memory_manager
    ensure_greeting(host, user, llm)

    st.title("Jenbina")
    with st.sidebar:
        st.session_state.debug_mode = st.checkbox(
            "🔧 Debug Mode", value=True,
            help="Show debug controls on the Environment page",
        )

    left, rail_col = st.columns(COLUMN_RATIO, gap="medium")

    with left:
        @st.fragment(run_every=REFRESH_SECONDS)
        def live_timeline():
            def draw():
                # A busy or sleeping mind defers the greeting until a refresh.
                ensure_greeting(host, user, llm)
                st.markdown("**Today with Jenbina**")
                filter_name = st.radio(
                    "Show", FILTERS, horizontal=True,
                    label_visibility="collapsed", key="timeline_filter",
                )
                # host.person, not a captured copy: the host replaces the
                # object if it ever has to reload her.
                person = host.person
                with st.container(height=TIMELINE_HEIGHT):
                    items = build_timeline(
                        person.get_conversation_history(person_key, count=MESSAGE_WINDOW),
                        host.event_log.recent(TIMELINE_LIMIT),
                        person.name,
                        filter_name,
                    )
                    render_timeline(items)
                # Follow new rows, but leave the reader alone on a refresh
                # that brought nothing new.
                newest = (filter_name, len(items), items[-1].timestamp if items else None)
                if st.session_state.get("_timeline_newest") != newest:
                    st.session_state["_timeline_newest"] = newest
                    scroll_timeline_to_bottom()
            draw_guarded(draw)

        live_timeline()
        live = st.container()
        user_input = st.chat_input("Talk to Jenbina...")

    with rail_col:
        @st.fragment(run_every=REFRESH_SECONDS)
        def live_rail():
            step_clicked = False

            def draw():
                nonlocal step_clicked
                if not host.hosting:
                    st.info("Jenbina has moved to another process. Reload this page to find her.")
                    return
                person = host.person
                world_summary, doing = _latest_world(host.situation.history)
                status = host.status()
                rail = render_status_rail(person, world_summary, doing, _top_goal(person))
                rail.stage(status.stage)
                if host.situation.phase == "asleep":
                    rail.portrait(_get_image_path("jenbina_sleep.png"), caption=person.name)
                step_clicked = render_heartbeat_card(status, is_admin())
                render_mind_card(person, person_key)

            if draw_guarded(draw) and step_clicked:
                with st.spinner("Jenbina is living a moment…"):
                    host.step_once()
                st.rerun()

        live_rail()

    if user_input:
        if host.status().busy:
            update_system_stage("finishing what she was doing…")
        with host.chat_turn(user) as turn:
            with live:
                handle_user_input(host.person, llm, memory_manager, False, user_input, turn)
        st.rerun()


main()
