"""The shared admin access check for the Admin page and heartbeat card."""

import os

import streamlit as st

LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]")

ADMIN_EMAIL = "matvei.kudelin@gmail.com"


def _hostname(value: str) -> str:
    """``localhost`` from ``localhost:8501`` or ``http://localhost:8501``."""
    value = (value or "").strip().lower()
    if "://" in value:
        value = value.split("://", 1)[1]
    value = value.split("/", 1)[0]
    if value.startswith("["):                      # [::1]:8501
        return value.split("]", 1)[0] + "]"
    return value.rsplit(":", 1)[0] if ":" in value else value


def is_local_request() -> bool:
    """Whether the request names this machine as its host.

    The Host and Origin headers come from the client, so this proves nothing
    about where the request came from; ``is_admin`` relies on it only in the
    development mode that has no login at all.
    """
    try:
        headers = st.context.headers
        return (_hostname(headers.get("Host", "")) in LOCAL_HOSTS
                or _hostname(headers.get("Origin", "")) in LOCAL_HOSTS)
    except Exception:
        return False


def is_admin() -> bool:
    """Return True if the current visitor is allowed to see the admin panel.

    With login on, only the admin account. A request that says it is local
    counts only when JENBINA_SKIP_AUTH=1, the development and test mode in
    which nothing is protected anyway: a remote client can send any Host
    header, so it must not open the admin panel on a deployed app.
    """
    if os.environ.get("JENBINA_SKIP_AUTH") == "1" and is_local_request():
        return True
    user = st.session_state.get("current_user")
    if user and user.get("email") == ADMIN_EMAIL:
        return True
    return False
