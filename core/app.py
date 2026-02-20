"""
Jenbina - AGI Simulation Streamlit App

Main entry point — Simulation page.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui.shared_init import require_auth, init_llm, save_person_state
from core.ui.simulation import (
    inject_tamagotchi_css,
    render_simulation_controls,
    run_simulation_loop,
    display_simulation_summary,
    render_environment_ribbon,
    render_needs_bars,
    render_emotion_chips,
    render_mood_indicator,
    display_jenbina_image,
    get_jenbina_image_for_emotion,
)
from core.ui.chat import render_chat_simple


def main():
    st.set_page_config(page_title="Jenbina — Simulation", page_icon="👧", layout="wide")
    inject_tamagotchi_css()

    if not require_auth():
        return

    llm, llm_json_mode = init_llm()
    person = st.session_state.person
    meta_cognitive_system = st.session_state.meta_cognitive_system

    st.title("👧 Jenbina")
    render_mood_indicator(person)

    # ── Sidebar: Simulation Controls & Debug ─────────────────────────────
    with st.sidebar:
        debug_mode = st.checkbox("🔧 Debug Mode", value=True, help="Show detailed debugging information")
        st.session_state.debug_mode = debug_mode
        controls = render_simulation_controls()

    # Show Jenbina's current state — image left, status right
    idle_placeholder = st.empty()
    with idle_placeholder.container():
        img_col, status_col = st.columns([1, 2])
        with img_col:
            idle_image = get_jenbina_image_for_emotion(person)
            display_jenbina_image(idle_image, caption=f"{person.name}")
        with status_col:
            render_needs_bars(person)
            render_emotion_chips(person)

    # ── Chat ─────────────────────────────────────────────────────────────
    memory_manager = st.session_state.memory_manager
    render_chat_simple(
        person=person,
        llm=llm,
        memory_manager=memory_manager,
        debug_mode=st.session_state.get("debug_mode", False),
    )

    # Auto-start a single simulation iteration on first load after auth
    auto_start = False
    if "simulation_auto_started" not in st.session_state:
        st.session_state.simulation_auto_started = True
        auto_start = True

    if controls["run_loop"] or controls["single_run"] or auto_start:
        idle_placeholder.empty()
        iterations = controls["num_iterations"] if controls["run_loop"] else 1

        results = run_simulation_loop(
            person=person,
            llm_json_mode=llm_json_mode,
            meta_cognitive_system=meta_cognitive_system,
            iterations=iterations,
            delay_seconds=controls["delay_seconds"],
        )

        # History is already updated inside run_simulation_loop per iteration
        # so that each iteration can see the previous one's action.

        if results:
            last = results[-1]
            st.session_state.action_decision = last.get("action_decision")
            st.session_state.needs_response = last.get("needs_state")

        display_simulation_summary(
            st.session_state.simulation_history, iterations, person=person
        )
        st.session_state.simulation_completed = True

    save_person_state()


if __name__ == "__main__":
    main()
else:
    main()
