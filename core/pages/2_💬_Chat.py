"""Jenbina — Chat page."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.shared_init import require_auth, init_llm, save_person_state
from core.ui.chat import render_chat_interface
from core.ui.simulation import render_mood_indicator

st.set_page_config(page_title="Jenbina — Chat", page_icon="💬", layout="wide")

if not require_auth():
    st.stop()

llm, _ = init_llm()
person = st.session_state.person
memory_manager = st.session_state.memory_manager
debug_mode = st.session_state.get("debug_mode", False)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.page_link("app.py", label="👧 Simulation", icon="👧")
with nav2:
    st.page_link("pages/2_💬_Chat.py", label="💬 Chat", icon="💬")
with nav3:
    st.page_link("pages/3_🌍_Environment.py", label="🌍 Environment", icon="🌍")

st.title("💬 Chat with Jenbina")
render_mood_indicator(person)

render_chat_interface(
    person=person,
    llm=llm,
    memory_manager=memory_manager,
    debug_mode=debug_mode,
)

save_person_state()
