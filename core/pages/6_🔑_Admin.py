"""Jenbina — Admin Panel.

Access restricted to:
- Local requests (localhost / 127.0.0.1) without authentication
- Authenticated user matvei.kudelin@gmail.com
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.auth.user_db import UserDatabase

st.set_page_config(page_title="Jenbina — Admin", page_icon="🔑", layout="wide")

ADMIN_EMAIL = "matvei.kudelin@gmail.com"


def _is_local_request() -> bool:
    """Check if the request originates from localhost."""
    try:
        headers = st.context.headers
        host = headers.get("Host", "")
        origin = headers.get("Origin", "")
        for local in ("localhost", "127.0.0.1", "0.0.0.0", "[::1]"):
            if local in host or local in origin:
                return True
        return False
    except Exception:
        return False


def _is_admin() -> bool:
    """Return True if the current visitor is allowed to see the admin panel."""
    if _is_local_request():
        return True
    user = st.session_state.get("current_user")
    if user and user.get("email") == ADMIN_EMAIL:
        return True
    return False


# --- Access gate ---
if not _is_admin():
    st.error("Access denied. Admin panel is only available from localhost or for the admin account.")
    st.stop()

# --- Admin panel ---
st.title("🔑 Admin Panel")

user_db = UserDatabase()
users = user_db.get_all_users_with_message_counts()

st.metric("Registered Users", len(users))

if not users:
    st.info("No registered users yet.")
    st.stop()

# Build a table
st.subheader("Users & Message Counts")
for user in users:
    with st.expander(
        f"**{user['display_name'] or user['email']}** — {user['total_messages']} messages",
        expanded=False,
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("User Messages", user["user_messages"] or 0)
        with col2:
            st.metric("Jenbina Messages", user["jenbina_messages"] or 0)
        with col3:
            st.metric("Total", user["total_messages"] or 0)

        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Provider:** {user['provider'] or '—'}")
        st.markdown(f"**Registered:** {user['created_at']}")
        st.markdown(f"**Last Login:** {user['last_login']}")
