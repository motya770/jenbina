"""Start and stop the two processes her Minecraft world needs.

Besides her mind, the world is a Minecraft server and the Node bridge that is
her body (see ``minecraft/README.md``). When she starts, whichever of the two
is not already running is started here; when she stops, the ones started here
are stopped, and the ones somebody else started are left alone.

Nothing is downloaded and the Minecraft EULA is never accepted here: setting
the world up stays a step its owner takes with ``minecraft/setup_server.sh``.
"""

from __future__ import annotations

import atexit
import logging
import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Mapping
from urllib.parse import urlsplit

from .bridge_client import MinecraftBridge, WorldUnavailable

logger = logging.getLogger("jenbina.minecraft")

LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")
DEFAULT_SERVER_PORT = 25565
DEFAULT_BRIDGE_PORT = 3010
# A server that has to make a new world can take a minute or two to listen.
READY_TIMEOUT_SECONDS = 150.0
POLL_SECONDS = 1.0
# The server saves the world on the way out; the bridge only logs her out.
SERVER_STOP_SECONDS = 30.0
BRIDGE_STOP_SECONDS = 5.0
SETUP_HINT = "Run ./minecraft/setup_server.sh --accept-eula once (see minecraft/README.md)."
BRIDGE_HINT = "Run `npm install` in minecraft/bridge once (see minecraft/README.md)."


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def is_local(host: str | None) -> bool:
    return (host or "").strip().lower() in LOCAL_HOSTS


def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """True when something accepts connections there."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def server_port(properties: Path, env: Mapping[str, str]) -> int:
    """The port the server listens on: ``MC_PORT``, else ``server.properties``."""
    try:
        if env.get("MC_PORT"):
            return int(env["MC_PORT"])
        for line in properties.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "server-port" and value.strip():
                return int(value.strip())
    except (OSError, ValueError):
        pass
    return DEFAULT_SERVER_PORT


class WorldLauncher:
    """Owns the server and bridge processes this process started."""

    def __init__(
        self, root: Path, bridge: MinecraftBridge, *,
        env: Mapping[str, str] | None = None,
        spawn: Callable[..., subprocess.Popen] = subprocess.Popen,
        is_port_open: Callable[[str, int], bool] = port_open,
        which: Callable[[str], str | None] = shutil.which,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.root = Path(root)
        self.bridge = bridge
        self.env = dict(os.environ if env is None else env)
        self._spawn = spawn
        self._is_port_open = is_port_open
        self._which = which
        self._sleep = sleep
        self._clock = clock
        self._lock = threading.Lock()
        self._server: subprocess.Popen | None = None
        self._bridge: subprocess.Popen | None = None
        self._logs: list = []
        self._atexit = False
        self.server_dir = self.root / "minecraft" / "server"
        self.bridge_dir = self.root / "minecraft" / "bridge"
        self.log_dir = self.root / "minecraft" / "logs"
        self.server_host = self.env.get("MC_HOST") or "127.0.0.1"
        self.server_port = server_port(self.server_dir / "server.properties", self.env)
        self.bridge_port = urlsplit(bridge.base_url).port or DEFAULT_BRIDGE_PORT

    # -- what is running ----------------------------------------------------

    def server_running(self) -> bool:
        return self._is_port_open(self.server_host, self.server_port)

    def bridge_running(self) -> bool:
        try:
            self.bridge.health()
            return True
        except WorldUnavailable:
            return False

    def _server_problems(self) -> list[str]:
        problems = []
        if not (self.server_dir / "server.jar").is_file():
            problems.append(f"Her Minecraft server is not set up. {SETUP_HINT}")
        else:
            try:
                eula = (self.server_dir / "eula.txt").read_text(encoding="utf-8")
            except OSError:
                eula = ""
            if not any(line.strip() == "eula=true" for line in eula.splitlines()):
                problems.append(f"The Minecraft EULA is not accepted yet. {SETUP_HINT}")
        if self._which("java") is None:
            problems.append("Java is not installed; the Minecraft server needs Java 21 or newer.")
        return problems

    def _bridge_problems(self) -> list[str]:
        problems = []
        if not (self.bridge_dir / "node_modules").is_dir():
            problems.append(f"The bridge's packages are not installed. {BRIDGE_HINT}")
        if self._which("node") is None:
            problems.append("Node is not installed; the bridge needs Node 18 or newer.")
        return problems

    # -- starting -----------------------------------------------------------

    def _open_log(self, name: str):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        handle = open(self.log_dir / name, "ab")
        self._logs.append(handle)
        return handle

    def _launch(self, command: list[str], log_name: str, env: dict) -> subprocess.Popen:
        if not self._atexit:
            # A crash on the way out must not leave a server running for nobody.
            atexit.register(self.stop)
            self._atexit = True
        return self._spawn(
            command, cwd=str(self.root), env=env, stdin=subprocess.DEVNULL,
            stdout=self._open_log(log_name), stderr=subprocess.STDOUT,
            # Its own session: Ctrl-C reaches her mind first, which logs her
            # out and then stops these in order.
            start_new_session=True,
        )

    @staticmethod
    def _exited(process: subprocess.Popen | None) -> bool:
        return process is not None and process.poll() is not None

    def start(self) -> None:
        """Start whichever of the server and the bridge is not running.

        Returns as soon as they are launched, not when they are ready; see
        ``ensure_ready``. Raises ``WorldUnavailable`` when something they need
        is missing, with what to do about it.
        """
        with self._lock:
            if self._exited(self._server):
                self._server = None
            if self._exited(self._bridge):
                self._bridge = None
            need_server = (self._server is None and is_local(self.server_host)
                           and not self.server_running())
            need_bridge = self._bridge is None and not self.bridge_running()
            problems = (self._server_problems() if need_server else []) + \
                       (self._bridge_problems() if need_bridge else [])
            if problems:
                raise WorldUnavailable(" ".join(problems))
            if need_server:
                logger.info("Starting her Minecraft server on port %s.", self.server_port)
                self._server = self._launch(
                    [str(self.root / "minecraft" / "run_server.sh")], "server.log", dict(self.env))
            if need_bridge:
                logger.info("Starting the bridge on port %s.", self.bridge_port)
                env = dict(self.env)
                env.setdefault("MC_PORT", str(self.server_port))
                env["BRIDGE_PORT"] = str(self.bridge_port)
                self._bridge = self._launch(
                    ["node", str(self.bridge_dir / "bridge.js")], "bridge.log", env)

    def ensure_ready(self, timeout: float = READY_TIMEOUT_SECONDS) -> None:
        """Start what is missing and wait until the world can be joined.

        Costs two quick local checks when everything is already up. Raises
        ``WorldUnavailable`` if the world is not ready within ``timeout``.
        """
        if self.bridge_running() and (not is_local(self.server_host) or self.server_running()):
            return
        self.start()
        deadline = self._clock() + timeout
        while True:
            if self._exited(self._server):
                raise WorldUnavailable(
                    "Her Minecraft server stopped while starting; see minecraft/logs/server.log.")
            if self._exited(self._bridge):
                raise WorldUnavailable(
                    "The bridge stopped while starting; see minecraft/logs/bridge.log.")
            if (not is_local(self.server_host) or self.server_running()) and self.bridge_running():
                return
            if self._clock() >= deadline:
                raise WorldUnavailable("Her Minecraft world is still starting.")
            self._sleep(POLL_SECONDS)

    # -- stopping -----------------------------------------------------------

    @staticmethod
    def _end(process: subprocess.Popen | None, patience: float) -> None:
        if process is None or process.poll() is not None:
            return
        try:
            process.terminate()
            try:
                process.wait(timeout=patience)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        except Exception:
            logger.exception("Could not stop a process of her Minecraft world.")

    def stop(self) -> None:
        """Stop the processes started here. Never raises; safe to call twice."""
        with self._lock:
            bridge, server = self._bridge, self._server
            self._bridge = self._server = None
            logs, self._logs = self._logs, []
        if bridge is not None or server is not None:
            logger.info("Stopping her Minecraft world.")
        # The bridge first, so she is logged out before the world closes.
        self._end(bridge, BRIDGE_STOP_SECONDS)
        self._end(server, SERVER_STOP_SECONDS)
        for handle in logs:
            try:
                handle.close()
            except Exception:
                pass
