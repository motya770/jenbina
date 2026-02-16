"""Login / signup UI for Jenbina (Streamlit) — Google SSO only."""

import os
import tempfile

import streamlit as st
from streamlit_google_auth import Authenticate
from core.auth.user_db import UserDatabase


def _get_credentials_path() -> str:
    """Return path to Google credentials file.

    Locally, reads ``.google_credentials.json`` from the project root.
    On Railway (or any host), reads the ``GOOGLE_CREDENTIALS_JSON`` env var
    and writes it to a temp file so the library can load it.
    """
    local_path = ".google_credentials.json"
    if os.path.exists(local_path):
        return local_path

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        tmp = os.path.join(tempfile.gettempdir(), "google_credentials.json")
        with open(tmp, "w") as f:
            f.write(creds_json)
        return tmp

    raise FileNotFoundError(
        "No Google credentials found. Set GOOGLE_CREDENTIALS_JSON env var "
        "or provide .google_credentials.json file."
    )


def _get_redirect_uri() -> str:
    """Return the OAuth redirect URI.

    Uses the ``REDIRECT_URI`` env var if set (for production), otherwise
    defaults to localhost for local development.
    """
    return os.environ.get("REDIRECT_URI", "http://localhost:8501")


def _get_user_db() -> UserDatabase:
    """Return a shared UserDatabase instance via session state."""
    if "user_db" not in st.session_state:
        st.session_state.user_db = UserDatabase()
    return st.session_state.user_db


def render_auth_page():
    """Show Google sign-in. Returns True once authenticated."""
    if st.session_state.get("authenticated"):
        return True

    st.title("Welcome to Jenbina")
    st.write("Sign in with Google to start chatting.")

    authenticator = Authenticate(
        secret_credentials_path=_get_credentials_path(),
        cookie_name="jenbina_auth",
        cookie_key="jenbina_secret_key",
        redirect_uri=_get_redirect_uri(),
    )
    authenticator.check_authentification()

    if st.session_state.get("connected"):
        user_info = st.session_state.get("user_info", {})
        email = user_info.get("email", "")
        name = user_info.get("name", email)
        photo = user_info.get("picture", "")

        user_db = _get_user_db()
        user = user_db.create_or_update_user(
            firebase_uid=f"google:{email}",
            email=email,
            display_name=name,
            photo_url=photo,
            provider="google",
        )
        st.session_state.authenticated = True
        st.session_state.current_user = user
        return True

    authenticator.login()
    return False


def render_user_header(user: dict):
    """Show logged-in user info and a logout button in the sidebar."""
    with st.sidebar:
        col1, col2 = st.columns([3, 1])
        with col1:
            name = user.get("display_name") or user.get("email", "User")
            st.write(f"**{name}**")
        with col2:
            if st.button("Logout"):
                for key in [
                    "authenticated",
                    "current_user",
                    "firebase_token",
                    "person",
                    "connected",
                    "user_info",
                ]:
                    st.session_state.pop(key, None)
                st.rerun()
