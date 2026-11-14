"""Tests for the admin panel access gate (core/auth/admin_access.py)."""
import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth.admin_access import ADMIN_EMAIL, is_admin, is_dev_mode


class TestAdminAccess(unittest.TestCase):
    def test_anonymous_visitor_is_denied(self):
        self.assertFalse(is_admin(None, env={}))

    def test_other_signed_in_user_is_denied(self):
        self.assertFalse(is_admin({"email": "someone@example.com"}, env={}))

    def test_user_without_email_is_denied(self):
        self.assertFalse(is_admin({"display_name": "No Email"}, env={}))

    def test_admin_account_is_allowed(self):
        self.assertTrue(is_admin({"email": ADMIN_EMAIL}, env={}))

    def test_dev_mode_allows_without_sign_in(self):
        self.assertTrue(is_admin(None, env={"JENBINA_SKIP_AUTH": "1"}))

    def test_dev_mode_requires_the_exact_flag(self):
        for value in ("", "0", "true", "yes"):
            self.assertFalse(is_dev_mode({"JENBINA_SKIP_AUTH": value}), value)
        self.assertFalse(is_admin(None, env={"JENBINA_SKIP_AUTH": "0"}))

    def test_reads_the_process_environment_by_default(self):
        with patch.dict(os.environ, {"JENBINA_SKIP_AUTH": "1"}):
            self.assertTrue(is_admin(None))
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(is_admin(None))

    def test_gate_takes_no_request_headers(self):
        """A spoofed Host/Origin cannot matter: the gate never sees the request."""
        import inspect
        self.assertEqual(list(inspect.signature(is_admin).parameters), ["user", "env"])


class TestCredentialsTempFile(unittest.TestCase):
    def test_credentials_file_is_owner_only(self):
        from core.ui import auth_page

        with tempfile.TemporaryDirectory() as tmp_dir, tempfile.TemporaryDirectory() as cwd:
            stale = os.path.join(tmp_dir, "google_credentials.json")
            with open(stale, "w") as f:
                f.write("old")
            os.chmod(stale, 0o644)
            old_cwd = os.getcwd()
            os.chdir(cwd)  # no local .google_credentials.json here
            try:
                with patch.dict(os.environ, {"GOOGLE_CREDENTIALS_JSON": '{"web": {}}'}), \
                        patch.object(auth_page.tempfile, "gettempdir", return_value=tmp_dir):
                    path = auth_page._get_credentials_path()
            finally:
                os.chdir(old_cwd)
            self.assertEqual(path, stale)
            self.assertEqual(open(path).read(), '{"web": {}}')
            self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
