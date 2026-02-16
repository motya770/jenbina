"""Jenbina — Environment & Debug page."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.shared_init import require_auth
from core.ui.sidebar import (
    render_environment_sidebar,
    render_location_exploration,
    render_dynamic_events,
    render_location_recommendations,
    render_debug_controls,
)

st.set_page_config(page_title="Jenbina — Environment", page_icon="🌍", layout="wide")

if not require_auth():
    st.stop()

environment_simulator = st.session_state.environment_simulator
memory_manager = st.session_state.memory_manager
debug_mode = st.session_state.get("debug_mode", False)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.page_link("app.py", label="👧 Simulation", icon="👧")
with nav2:
    st.page_link("pages/2_💬_Chat.py", label="💬 Chat", icon="💬")
with nav3:
    st.page_link("pages/3_🌍_Environment.py", label="🌍 Environment", icon="🌍")

st.title("🌍 Environment & Debug")

env_col, loc_col = st.columns(2)
with env_col:
    render_environment_sidebar(environment_simulator)
    render_location_exploration(environment_simulator)
with loc_col:
    render_dynamic_events(environment_simulator)
    render_location_recommendations(environment_simulator)

if debug_mode:
    st.markdown("---")
    render_debug_controls(memory_manager)
