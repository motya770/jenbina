"""Login / signup UI for Jenbina (Streamlit)."""

import streamlit as st
from core.auth.user_db import UserDatabase


def _get_user_db() -> UserDatabase:
    """Return a shared UserDatabase instance via session state."""
    if "user_db" not in st.session_state:
        st.session_state.user_db = UserDatabase()
    return st.session_state.user_db


def _handle_google_login():
    """Attempt Google OAuth via streamlit-google-auth.

    If the library is not installed or the credentials are missing the
    section is silently skipped so that the email/password form still works.
    """
    try:
        from streamlit_google_auth import Authenticate

        authenticator = Authenticate(
            secret_credentials_path=".google_credentials.json",
            cookie_name="jenbina_auth",
            cookie_key="jenbina_secret_key",
            redirect_uri="http://localhost:8501",
        )
        authenticator.check_authentification()

        if st.session_state.get("connected"):
            user_db = _get_user_db()
            email = st.session_state.get("user_info", {}).get("email", "")
            name = st.session_state.get("user_info", {}).get("name", email)
            photo = st.session_state.get("user_info", {}).get("picture", "")
            # Use email as a stable firebase_uid stand-in for Google OAuth
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
    except Exception:
        # streamlit-google-auth not configured — fall through to email form
        return False


def _handle_email_login():
    """Render email/password login and sign-up forms."""
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted and email and password:
            try:
                from core.auth.firebase_auth import FirebaseAuth

                auth = FirebaseAuth()
                result = auth.sign_in_with_email(email, password)
                uid = result["localId"]
                display_name = result.get("displayName", email.split("@")[0])

                user_db = _get_user_db()
                user = user_db.create_or_update_user(
                    firebase_uid=uid,
                    email=email,
                    display_name=display_name,
                    provider="email",
                )
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.firebase_token = result["idToken"]
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pw")
            new_name = st.text_input("Display Name", key="signup_name")
            submitted_signup = st.form_submit_button("Create Account")

        if submitted_signup and new_email and new_password:
            try:
                from core.auth.firebase_auth import FirebaseAuth

                auth = FirebaseAuth()
                result = auth.sign_up_with_email(new_email, new_password)
                uid = result["localId"]
                display_name = new_name or new_email.split("@")[0]

                user_db = _get_user_db()
                user = user_db.create_or_update_user(
                    firebase_uid=uid,
                    email=new_email,
                    display_name=display_name,
                    provider="email",
                )
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.firebase_token = result["idToken"]
                st.rerun()
            except Exception as e:
                st.error(f"Sign-up failed: {e}")


def render_auth_page():
    """Show the full login/signup page. Returns True once authenticated."""
    if st.session_state.get("authenticated"):
        return True

    st.title("Welcome to Jenbina")
    st.write("Sign in to start chatting.")

    # Try Google OAuth first
    if _handle_google_login():
        return True

    st.divider()

    # Email / password fallback
    _handle_email_login()

    return st.session_state.get("authenticated", False)


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
                ]:
                    st.session_state.pop(key, None)
                st.rerun()
