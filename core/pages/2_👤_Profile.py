"""Jenbina — Profile & Chat page."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.shared_init import require_auth, init_llm, save_person_state
from core.ui.simulation import inject_tamagotchi_css
from core.ui.profile import render_profile_page

st.set_page_config(page_title="Jenbina — Profile", page_icon="👤", layout="wide")
inject_tamagotchi_css()

if not require_auth():
    st.stop()

llm, _ = init_llm()
person = st.session_state.person
memory_manager = st.session_state.memory_manager
debug_mode = st.session_state.get("debug_mode", False)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.page_link("app.py", label="Simulation", icon="🧠")
with nav2:
    st.page_link("pages/2_👤_Profile.py", label="Profile", icon="👤")
with nav3:
    st.page_link("pages/3_🌍_Environment.py", label="Environment", icon="🌍")

st.title("Jenbina")

render_profile_page(
    person=person,
    llm=llm,
    memory_manager=memory_manager,
    debug_mode=debug_mode,
)

save_person_state()
