"""Jenbina — Admin Panel.

Access restricted to:
- Local requests (localhost / 127.0.0.1) without authentication
- Authenticated user matvei.kudelin@gmail.com
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.admin import ADMIN_EMAIL, is_admin, is_local_request
from core.ui.pixel_theme import inject_pixel_css
from core.auth.user_db import UserDatabase

st.set_page_config(page_title="Jenbina — Admin", page_icon="🔑", layout="wide")
inject_pixel_css()

# --- Access gate ---
if not is_admin():
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
