"""HTTP client for the Node bridge that is Jenbina's body in Minecraft.

The bridge (``minecraft/bridge/bridge.js``) listens on localhost and offers a
session, an observation and bounded actions. Every failure to reach it or to
get a usable answer is raised as ``WorldUnavailable``.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BRIDGE_URL = "http://127.0.0.1:3010"
DEFAULT_BUDGET_MS = 45000
# Logging in can take as long as the bridge's own login timeout.
SESSION_TIMEOUT_SECONDS = 30.0
REQUEST_TIMEOUT_SECONDS = 15.0
# How long past an action's budget the bridge may take to answer.
ACT_GRACE_SECONDS = 30.0


class WorldUnavailable(RuntimeError):
    """The Minecraft world cannot be reached or did not answer usefully."""


class MinecraftBridge:
    def __init__(self, base_url: str = DEFAULT_BRIDGE_URL, opener=None):
        self.base_url = base_url.rstrip("/")
        self._open = opener if opener is not None else urllib.request.urlopen

    def _call(self, method: str, path: str, body: dict | None, timeout: float) -> dict[str, Any]:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            self.base_url + path, data=data, method=method,
            headers={"content-type": "application/json"},
        )
        try:
            with self._open(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            raise WorldUnavailable(self._error_text(err)) from err
        except (urllib.error.URLError, OSError, ValueError) as err:
            raise WorldUnavailable(f"The Minecraft bridge at {self.base_url} did not answer: {err}") from err
        if not isinstance(payload, dict):
            raise WorldUnavailable("The Minecraft bridge answered with something other than an object.")
        return payload

    @staticmethod
    def _error_text(err: urllib.error.HTTPError) -> str:
        try:
            message = json.loads(err.read().decode("utf-8")).get("message", "")
        except Exception:
            message = ""
        return f"The Minecraft bridge refused ({err.code}): {message or err.reason}"

    def health(self) -> dict[str, Any]:
        return self._call("GET", "/health", None, REQUEST_TIMEOUT_SECONDS)

    def start_session(self) -> dict[str, Any]:
        """Log her in if needed and return the observation."""
        payload = self._call("POST", "/session/start", {}, SESSION_TIMEOUT_SECONDS)
        observation = payload.get("observation")
        if not isinstance(observation, dict):
            raise WorldUnavailable("The Minecraft bridge started a session without an observation.")
        return observation

    def end_session(self) -> None:
        """Log her out. Never raises: leaving must not break a beat."""
        try:
            self._call("POST", "/session/end", {}, REQUEST_TIMEOUT_SECONDS)
        except WorldUnavailable:
            pass

    def observe(self) -> dict[str, Any]:
        return self._call("GET", "/observe", None, REQUEST_TIMEOUT_SECONDS)

    def act(self, name: str, args: dict | None = None, budget_ms: int = DEFAULT_BUDGET_MS) -> dict[str, Any]:
        """Run one bounded routine and return its outcome."""
        return self._call(
            "POST", "/act", {"name": name, "args": args or {}, "budget_ms": budget_ms},
            budget_ms / 1000 + ACT_GRACE_SECONDS,
        )
