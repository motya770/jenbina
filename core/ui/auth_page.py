"""Login / signup UI for Jenbina (Streamlit) — Google SSO only."""

import streamlit as st
from streamlit_google_auth import Authenticate
from core.auth.user_db import UserDatabase


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
        secret_credentials_path=".google_credentials.json",
        cookie_name="jenbina_auth",
        cookie_key="jenbina_secret_key",
        redirect_uri="http://localhost:8501",
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
