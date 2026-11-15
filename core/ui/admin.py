"""The shared admin access check for the Admin page and heartbeat card."""

import streamlit as st

ADMIN_EMAIL = "matvei.kudelin@gmail.com"


def is_local_request() -> bool:
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


def is_admin() -> bool:
    """Return True if the current visitor is allowed to see the admin panel."""
    if is_local_request():
        return True
    user = st.session_state.get("current_user")
    if user and user.get("email") == ADMIN_EMAIL:
        return True
    return False
