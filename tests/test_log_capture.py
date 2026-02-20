"""Tests for core/log_capture.py — StreamCapture and global log buffer."""

import unittest
from unittest.mock import MagicMock
from io import StringIO

from core.log_capture import StreamCapture, _global_logs, install_capture


class TestStreamCapture(unittest.TestCase):
    """Tests for the StreamCapture tee-style stream wrapper."""

    def setUp(self):
        # Snapshot the length so we can detect new entries added by our tests
        self._log_start = len(_global_logs)

    def _new_logs(self):
        return _global_logs[self._log_start:]

    # ------------------------------------------------------------------
    # Basic write behaviour (lines 19-26)
    # ------------------------------------------------------------------
    def test_write_forwards_to_original(self):
        original = StringIO()
        capture = StreamCapture(original, "test_stream")
        capture.write("hello world")
        self.assertEqual(original.getvalue(), "hello world")

    def test_write_appends_to_global_logs(self):
        original = StringIO()
        capture = StreamCapture(original, "test_stream")
        capture.write("test message")
        new = self._new_logs()
        self.assertTrue(len(new) >= 1)
        last = new[-1]
        self.assertEqual(last["stream"], "test_stream")
        self.assertEqual(last["message"], "test message")
        self.assertIn("timestamp", last)

    def test_whitespace_only_not_logged(self):
        original = StringIO()
        capture = StreamCapture(original, "test_stream")
        before = len(_global_logs)
        capture.write("   \n  ")
        self.assertEqual(len(_global_logs), before)

    def test_empty_string_not_logged(self):
        original = StringIO()
        capture = StreamCapture(original, "test_stream")
        before = len(_global_logs)
        capture.write("")
        self.assertEqual(len(_global_logs), before)

    def test_newline_stripped_from_message(self):
        original = StringIO()
        capture = StreamCapture(original, "test_stream")
        capture.write("with trailing newline\n")
        new = self._new_logs()
        self.assertEqual(new[-1]["message"], "with trailing newline")

    # ------------------------------------------------------------------
    # flush / fileno / isatty delegation (lines 28-35)
    # ------------------------------------------------------------------
    def test_flush_delegates_to_original(self):
        original = MagicMock()
        capture = StreamCapture(original, "stdout")
        capture.flush()
        original.flush.assert_called_once()

    def test_fileno_delegates_to_original(self):
        original = MagicMock()
        original.fileno.return_value = 42
        capture = StreamCapture(original, "stdout")
        self.assertEqual(capture.fileno(), 42)

    def test_isatty_delegates_to_original(self):
        original = MagicMock()
        original.isatty.return_value = False
        capture = StreamCapture(original, "stdout")
        self.assertFalse(capture.isatty())

    # ------------------------------------------------------------------
    # Stream name stored correctly
    # ------------------------------------------------------------------
    def test_stream_name_stdout(self):
        original = StringIO()
        capture = StreamCapture(original, "stdout")
        capture.write("msg")
        new = self._new_logs()
        self.assertEqual(new[-1]["stream"], "stdout")

    def test_stream_name_stderr(self):
        original = StringIO()
        capture = StreamCapture(original, "stderr")
        capture.write("err")
        new = self._new_logs()
        self.assertEqual(new[-1]["stream"], "stderr")

    # ------------------------------------------------------------------
    # Timestamp format (HH:MM:SS.mmm)
    # ------------------------------------------------------------------
    def test_timestamp_format(self):
        import re
        original = StringIO()
        capture = StreamCapture(original, "test")
        capture.write("timestamped msg")
        new = self._new_logs()
        ts = new[-1]["timestamp"]
        self.assertRegex(ts, r"\d{2}:\d{2}:\d{2}\.\d{3}")


class TestInstallCapture(unittest.TestCase):
    """Tests for install_capture() function."""

    def test_install_capture_is_callable(self):
        self.assertTrue(callable(install_capture))


if __name__ == "__main__":
    unittest.main()
