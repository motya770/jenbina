"""Who may see the admin panel and the "Step once" button."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui import admin
from core.ui.admin import ADMIN_EMAIL, is_admin, is_local_request


def _streamlit(host="", origin="", email=None):
    st = MagicMock()
    st.context.headers = {"Host": host, "Origin": origin}
    st.session_state = {"current_user": {"email": email}} if email else {}
    return st


class TestLocalRequest(unittest.TestCase):
    def test_exact_local_hosts_only(self):
        for host in ("localhost:8501", "127.0.0.1:8501", "[::1]:8501", "localhost"):
            with self.subTest(host=host), patch.object(admin, "st", _streamlit(host=host)):
                self.assertTrue(is_local_request())
        for host in ("localhost.example.com", "notlocalhost:8501", "example.com", ""):
            with self.subTest(host=host), patch.object(admin, "st", _streamlit(host=host)):
                self.assertFalse(is_local_request())
        with patch.object(admin, "st", _streamlit(host="example.com", origin="http://localhost:8501")):
            self.assertTrue(is_local_request())


class TestAdmin(unittest.TestCase):
    def test_with_login_on_a_local_looking_request_is_not_admin(self):
        with patch.dict(os.environ, {"JENBINA_SKIP_AUTH": "0"}), \
                patch.object(admin, "st", _streamlit(host="localhost:8501", email="someone@example.com")):
            self.assertFalse(is_admin())

    def test_with_login_on_the_admin_account_is_admin_from_anywhere(self):
        with patch.dict(os.environ, {"JENBINA_SKIP_AUTH": "0"}), \
                patch.object(admin, "st", _streamlit(host="jenbina.example.com", email=ADMIN_EMAIL)):
            self.assertTrue(is_admin())

    def test_development_mode_trusts_this_machine(self):
        with patch.dict(os.environ, {"JENBINA_SKIP_AUTH": "1"}):
            with patch.object(admin, "st", _streamlit(host="localhost:8501")):
                self.assertTrue(is_admin())
            with patch.object(admin, "st", _streamlit(host="jenbina.example.com")):
                self.assertFalse(is_admin())


if __name__ == "__main__":
    unittest.main()
