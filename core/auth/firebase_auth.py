"""Firebase authentication wrapper using pyrebase4."""

import os
from typing import Optional


class FirebaseAuth:
    """Wraps Pyrebase auth for email/password and OAuth sign-in.

    Usage::

        config = {
            "apiKey": "...",
            "authDomain": "...",
            "projectId": "...",
            "storageBucket": "...",
            "messagingSenderId": "...",
            "appId": "...",
            "databaseURL": "",  # required by pyrebase even if unused
        }
        auth = FirebaseAuth(config)
    """

    def __init__(self, config: dict = None):
        import pyrebase

        if config is None:
            config = self._config_from_env()
        # Pyrebase requires databaseURL even if you don't use Realtime DB
        config.setdefault("databaseURL", "")
        firebase = pyrebase.initialize_app(config)
        self._auth = firebase.auth()

    @staticmethod
    def _config_from_env() -> dict:
        """Build config dict from environment variables."""
        return {
            "apiKey": os.environ["FIREBASE_API_KEY"],
            "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
            "projectId": os.environ["FIREBASE_PROJECT_ID"],
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": os.environ.get("FIREBASE_APP_ID", ""),
            "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", ""),
        }

    def sign_in_with_email(self, email: str, password: str) -> dict:
        """Sign in with email and password. Returns Pyrebase user dict."""
        return self._auth.sign_in_with_email_and_password(email, password)

    def sign_up_with_email(self, email: str, password: str) -> dict:
        """Create a new account. Returns Pyrebase user dict."""
        return self._auth.create_user_with_email_and_password(email, password)

    def get_account_info(self, id_token: str) -> dict:
        """Retrieve account info from a Firebase ID token."""
        return self._auth.get_account_info(id_token)

    def sign_in_with_google(self):
        """Placeholder — Google OAuth handled by streamlit-google-auth.

        In the Streamlit UI we use ``streamlit-google-auth`` which manages the
        browser redirect flow.  After the redirect the UI receives the user's
        email / name / photo and calls ``user_db.create_or_update_user`` directly.
        """
        raise NotImplementedError(
            "Google sign-in is handled via streamlit-google-auth in the UI layer."
        )
