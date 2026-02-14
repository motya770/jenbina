"""Shared fixtures for Playwright E2E tests."""

import os
import subprocess
import sys
import time
import socket
import signal

import pytest


def _free_port() -> int:
    """Return an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 120) -> None:
    """Block until Streamlit is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", port), timeout=2):
                return
        except OSError:
            time.sleep(1)
    raise RuntimeError(f"Streamlit did not start within {timeout}s on port {port}")


@pytest.fixture(scope="session")
def streamlit_server():
    """Launch Streamlit for the test session and tear it down afterwards.

    Yields the base URL, e.g. ``http://localhost:8503``.
    """
    port = _free_port()
    env = os.environ.copy()
    env["JENBINA_SKIP_AUTH"] = "1"
    # Disable Streamlit's browser auto-open and telemetry
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            "core/app.py",
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        _wait_for_server(port)
        yield f"http://localhost:{port}"
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
