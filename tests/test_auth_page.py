"""Tests for the login page helpers (core/ui/auth_page.py)."""
import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
