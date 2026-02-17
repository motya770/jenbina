"""Jenbina — Console Log page."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.shared_init import require_auth
from core.log_capture import install_capture

st.set_page_config(page_title="Jenbina — Console", page_icon="📋", layout="wide")

if not require_auth():
    st.stop()

install_capture()

nav1, nav2, nav3, nav4, nav5 = st.columns(5)
with nav1:
    st.page_link("app.py", label="👧 Simulation", icon="👧")
with nav2:
    st.page_link("pages/2_💬_Chat.py", label="💬 Chat", icon="💬")
with nav3:
    st.page_link("pages/3_🌍_Environment.py", label="🌍 Environment", icon="🌍")
with nav4:
    st.page_link("pages/4_📋_Console.py", label="📋 Console", icon="📋")
with nav5:
    st.page_link("pages/5_🔧_Debug_Info.py", label="🔧 Debug Info", icon="🔧")

st.title("📋 Console Logs")

logs = st.session_state.get("console_logs", [])

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("Total Logs", len(logs))
with col2:
    stdout_count = sum(1 for l in logs if l["stream"] == "stdout")
    st.metric("stdout", stdout_count)
with col3:
    stderr_count = sum(1 for l in logs if l["stream"] == "stderr")
    st.metric("stderr", stderr_count)

filter_col, action_col = st.columns([2, 1])
with filter_col:
    stream_filter = st.selectbox("Filter by stream", ["all", "stdout", "stderr"])
with action_col:
    if st.button("Clear Logs"):
        st.session_state.console_logs = []
        st.rerun()

auto_scroll = st.checkbox("Show newest first", value=True)

filtered = logs
if stream_filter != "all":
    filtered = [l for l in logs if l["stream"] == stream_filter]

if auto_scroll:
    filtered = list(reversed(filtered))

if not filtered:
    st.info("No console output captured yet. Run a simulation or chat to see logs here.")
else:
    log_lines = []
    for entry in filtered:
        stream_badge = "🔴" if entry["stream"] == "stderr" else "⚪"
        log_lines.append(f"{entry['timestamp']} {stream_badge} {entry['message']}")
    st.code("\n".join(log_lines), language=None)
