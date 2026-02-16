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
    display_jenbina_image,
    get_jenbina_image_for_emotion,
)


def main():
    st.set_page_config(page_title="Jenbina — Simulation", page_icon="🧠", layout="wide")
    inject_tamagotchi_css()

    if not require_auth():
        return

    llm, llm_json_mode = init_llm()
    person = st.session_state.person
    meta_cognitive_system = st.session_state.meta_cognitive_system

    # ── Navigation ──────────────────────────────────────────────────────
    st.title("🧠 Jenbina")

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        st.page_link("app.py", label="Simulation", icon="🧠")
    with nav2:
        st.page_link("pages/2_💬_Chat.py", label="Chat", icon="💬")
    with nav3:
        st.page_link("pages/3_🌍_Environment.py", label="Environment", icon="🌍")

    st.markdown("---")

    debug_mode = st.checkbox("🔧 Debug Mode", value=True, help="Show detailed debugging information")
    st.session_state.debug_mode = debug_mode

    controls = render_simulation_controls()

    # Show Jenbina's current state (idle view) — cleared when simulation runs
    idle_placeholder = st.empty()
    with idle_placeholder.container():
        _, idle_center, _ = st.columns([1, 2, 1])
        with idle_center:
            idle_image = get_jenbina_image_for_emotion(person)
            display_jenbina_image(idle_image, caption=f"{person.name}")
            render_needs_bars(person)
            render_emotion_chips(person)

    if controls["run_loop"] or controls["single_run"]:
        idle_placeholder.empty()
        iterations = controls["num_iterations"] if controls["run_loop"] else 1

        results = run_simulation_loop(
            person=person,
            llm_json_mode=llm_json_mode,
            meta_cognitive_system=meta_cognitive_system,
            iterations=iterations,
            delay_seconds=controls["delay_seconds"],
        )

        st.session_state.simulation_history.extend(results)

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
