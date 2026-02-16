"""Capture stdout/stderr to session state while preserving console output."""
import sys
import io
from datetime import datetime

# Module-level list shared across all sessions in this process.
# StreamCapture always writes here; install_capture() syncs it into session state.
_global_logs: list = []


class StreamCapture(io.TextIOBase):
    """Tee-style stream wrapper that captures output and forwards to original stream."""

    def __init__(self, original_stream, stream_name: str = "stdout"):
        super().__init__()
        self._original = original_stream
        self._stream_name = stream_name

    def write(self, text):
        if text and text.strip():
            _global_logs.append({
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "stream": self._stream_name,
                "message": text.rstrip("\n"),
            })
        return self._original.write(text)

    def flush(self):
        self._original.flush()

    def fileno(self):
        return self._original.fileno()

    def isatty(self):
        return self._original.isatty()


# Only wrap streams once per process
if not isinstance(sys.stdout, StreamCapture):
    sys.stdout = StreamCapture(sys.stdout, "stdout")
if not isinstance(sys.stderr, StreamCapture):
    sys.stderr = StreamCapture(sys.stderr, "stderr")


def install_capture():
    """Sync the global log buffer into session state. Call on every page load."""
    import streamlit as st
    # Point session state at the shared list so the Console page can read it
    st.session_state.console_logs = _global_logs
