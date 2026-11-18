"""Start and stop the processes her Minecraft world needs.

Besides her mind, the world is a Minecraft server and the Node bridge that is
her body (see ``minecraft/README.md``). When she starts, whichever of the two
is not already running is started here; when she stops, the ones started here
are stopped, and the ones somebody else started are left alone.

A third process is optional: the inhabitants, an unmodified Mindcraft checkout
that plays the others who live in her world. It is started once the server
answers, watched while it runs, and stopped first. Without it she lives alone
and nothing else changes.

Nothing is downloaded and the Minecraft EULA is never accepted here: setting
the world up stays a step its owner takes with ``minecraft/setup_server.sh``
and ``minecraft/setup_inhabitants.sh``.
"""

from __future__ import annotations

import atexit
import json
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

# The inhabitants: Mindcraft agents, each its own child of one main process.
DEFAULT_MINDSERVER_PORT = 3011
INHABITANTS_HINT = "Run ./minecraft/setup_inhabitants.sh once (see minecraft/README.md)."
INHABITANTS_LOG = "inhabitants.log"
# Started again no sooner than this after the last start, so a crash on
# start-up cannot become a loop.
INHABITANTS_RETRY_SECONDS = 600.0
INHABITANTS_STOP_SECONDS = 10.0
# Their bill is bounded here, whatever they decide to do: more LLM calls than
# this in an hour and they are stopped until her mind is started again. A day
# of talks with her is far below it.
INHABITANT_CALLS_PER_HOUR = 60
WATCH_SECONDS = 60.0
# What Mindcraft prints for each request to its LLM, and when it gives up on
# an agent that keeps leaving the world. Both belong to the pinned commit.
LLM_CALL_MARK = b"Awaiting openai api response"
DROPPED_MARK = b"will not be restarted"
# Mindcraft's own defaults, then what an inhabitant of her world must never do:
# start talks by itself, attack her, or write code. (`!goal` cannot be blocked.)
BLOCKED_ACTIONS = (
    "!checkBlueprint", "!checkBlueprintLevel", "!getBlueprint", "!getBlueprintLevel",
    "!startConversation", "!attackPlayer", "!newAction",
)
# All that is handed to Mindcraft from her environment: it is someone else's
# code, and needs her OpenAI key and nothing else of hers.
INHABITANT_ENV = ("PATH", "HOME", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR",
                  "OPENAI_API_KEY", "OPENAI_ORG_ID")


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


def inhabitant_settings(server_port: int, mindserver_port: int) -> dict:
    """Mindcraft's settings for her world, passed to it as ``SETTINGS_JSON``.

    Everything stays on this machine, no code is ever written or run by an
    agent, and an agent speaks only when it is spoken to.
    """
    return {
        "host": "127.0.0.1",
        "port": server_port,
        "auth": "offline",
        "minecraft_version": "1.21.4",
        "base_profile": "survival",
        "allow_insecure_coding": False,
        "allow_vision": False,
        "only_chat_with": [],
        "init_message": "",
        "narrate_behavior": False,
        "load_memory": True,
        "max_commands": 3,
        "auto_open_ui": False,
        "mindserver_port": mindserver_port,
        "blocked_actions": list(BLOCKED_ACTIONS),
    }


class WorldLauncher:
    """Owns the server, bridge and inhabitants processes this process started."""

    def __init__(
        self, root: Path, bridge: MinecraftBridge, *,
        env: Mapping[str, str] | None = None,
        spawn: Callable[..., subprocess.Popen] = subprocess.Popen,
        is_port_open: Callable[[str, int], bool] = port_open,
        which: Callable[[str], str | None] = shutil.which,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        watch_seconds: float | None = WATCH_SECONDS,
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
        self._inhabitants: subprocess.Popen | None = None
        self._inhabitants_started: float | None = None
        self._inhabitants_stopped_for_good = False
        self._log_offset = 0
        self._llm_calls: list[float] = []
        self._said: set[str] = set()
        # How often the inhabitants are checked between beats; ``None`` leaves
        # the checking to ``ensure_ready``.
        self._watch_seconds = watch_seconds
        self._watch_stop = threading.Event()
        self._watcher: threading.Thread | None = None
        self._logs: list = []
        self._atexit = False
        self.server_dir = self.root / "minecraft" / "server"
        self.bridge_dir = self.root / "minecraft" / "bridge"
        self.log_dir = self.root / "minecraft" / "logs"
        self.server_host = self.env.get("MC_HOST") or "127.0.0.1"
        self.server_port = server_port(self.server_dir / "server.properties", self.env)
        self.bridge_port = urlsplit(bridge.base_url).port or DEFAULT_BRIDGE_PORT
        self.mindcraft_dir = self.root / "minecraft" / "mindcraft"
        self.profiles_dir = self.root / "minecraft" / "inhabitants"
        # The Node that setup_inhabitants.sh installs when the machine's own does not suit.
        self.private_node = self.root / "minecraft" / "mindcraft-node" / "node_modules" / "node" / "bin" / "node"
        self.mindserver_port = DEFAULT_MINDSERVER_PORT

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

    def _launch(self, command: list[str], log_name: str, env: dict,
                cwd: Path | None = None) -> subprocess.Popen:
        if not self._atexit:
            # A crash on the way out must not leave a server running for nobody.
            atexit.register(self.stop)
            self._atexit = True
        return self._spawn(
            command, cwd=str(cwd or self.root), env=env, stdin=subprocess.DEVNULL,
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
            self._look_after_inhabitants()
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
                # They are not waited for: she can look at once, and sees them when they arrive.
                self._look_after_inhabitants()
                return
            if self._clock() >= deadline:
                raise WorldUnavailable("Her Minecraft world is still starting.")
            self._sleep(POLL_SECONDS)

    # -- the inhabitants ----------------------------------------------------

    def inhabitants_set_up(self) -> bool:
        """Mindcraft is installed and there is at least one character to play."""
        return ((self.mindcraft_dir / "main.js").is_file()
                and (self.mindcraft_dir / "node_modules").is_dir()
                and any(self.profiles_dir.glob("*.json")))

    def inhabitants_running(self) -> bool:
        """Something answers on Mindcraft's own port (it binds ``localhost`` only)."""
        return self._is_port_open("localhost", self.mindserver_port)

    def _say_once(self, key: str, message: str) -> None:
        if key not in self._said:
            self._said.add(key)
            logger.info(message)

    def _inhabitant_node(self) -> str | None:
        if self.env.get("MINDCRAFT_NODE"):
            return self.env["MINDCRAFT_NODE"]
        if self.private_node.is_file():
            return str(self.private_node)
        return "node" if self._which("node") is not None else None

    def start_inhabitants(self) -> bool:
        """Start the others who live in her world, if they can be. Never raises.

        Returns whether they were launched now. When something they need is
        missing she simply lives alone; what is missing is logged once.
        """
        try:
            with self._lock:
                return self._start_inhabitants()
        except Exception:
            logger.exception("Could not start the inhabitants of her Minecraft world.")
            return False

    def _start_inhabitants(self) -> bool:
        if self.env.get("JENBINA_MINECRAFT_INHABITANTS", "1") == "0":
            return False
        if self._inhabitants_stopped_for_good or not is_local(self.server_host):
            return False
        if self._inhabitants is not None:
            if self._inhabitants.poll() is None:
                return False
            self._inhabitants = None
            logger.warning("The inhabitants of her world stopped; see minecraft/logs/%s.", INHABITANTS_LOG)
        if not self.server_running():
            return False
        if not self.inhabitants_set_up():
            self._say_once("setup", f"She lives alone in her world: Mindcraft is not set up. {INHABITANTS_HINT}")
            return False
        if not self.env.get("OPENAI_API_KEY"):
            self._say_once("key", "She lives alone in her world: the inhabitants need OPENAI_API_KEY "
                                  "in the environment her mind is started with.")
            return False
        node = self._inhabitant_node()
        if node is None:
            self._say_once("node", "She lives alone in her world: Node is not installed.")
            return False
        if self.inhabitants_running():
            return False        # somebody else's; used and left running
        now = self._clock()
        if self._inhabitants_started is not None and now - self._inhabitants_started < INHABITANTS_RETRY_SECONDS:
            return False
        self._inhabitants_started = now
        env = {key: self.env[key] for key in INHABITANT_ENV if self.env.get(key)}
        env["SETTINGS_JSON"] = json.dumps(inhabitant_settings(self.server_port, self.mindserver_port))
        profiles = sorted(str(path) for path in self.profiles_dir.glob("*.json"))
        log = self.log_dir / INHABITANTS_LOG
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Only what they print from now on is counted against them.
        self._log_offset = log.stat().st_size if log.exists() else 0
        self._llm_calls = []
        logger.info("Starting the inhabitants of her world (%s).",
                    ", ".join(Path(profile).stem for profile in profiles))
        self._inhabitants = self._launch(
            [node, "main.js", "--profiles", *profiles], INHABITANTS_LOG, env, cwd=self.mindcraft_dir)
        self._watch()
        return True

    def _watch(self) -> None:
        if self._watch_seconds is None or (self._watcher is not None and self._watcher.is_alive()):
            return
        self._watch_stop = stop = threading.Event()

        def watch() -> None:
            while not stop.wait(self._watch_seconds):
                self.check_inhabitants()

        self._watcher = threading.Thread(target=watch, name="jenbina-inhabitants-watch", daemon=True)
        self._watcher.start()

    def _new_log_lines(self) -> bytes:
        """What the inhabitants printed since the last check, whole lines only."""
        try:
            with open(self.log_dir / INHABITANTS_LOG, "rb") as handle:
                handle.seek(self._log_offset)
                data = handle.read()
        except OSError:
            return b""
        data = data[:data.rfind(b"\n") + 1]
        self._log_offset += len(data)
        return data

    def check_inhabitants(self) -> None:
        """Stop the inhabitants when they cost too much or one has dropped out.

        Called every minute while they run, and before each look at the world.
        Never raises.
        """
        try:
            with self._lock:
                process = self._inhabitants
                if process is None or process.poll() is not None:
                    return
                printed = self._new_log_lines()
                now = self._clock()
                self._llm_calls = [at for at in self._llm_calls if now - at < 3600.0]
                self._llm_calls.extend([now] * printed.count(LLM_CALL_MARK))
                too_many = len(self._llm_calls) > INHABITANT_CALLS_PER_HOUR
                dropped = DROPPED_MARK in printed
                if not (too_many or dropped):
                    return
                self._inhabitants = None
                self._inhabitants_stopped_for_good = too_many
            if too_many:
                logger.error(
                    "The inhabitants of her world made more than %s LLM calls in an hour and were stopped. "
                    "They stay stopped until her mind is started again; see minecraft/logs/%s.",
                    INHABITANT_CALLS_PER_HOUR, INHABITANTS_LOG)
            else:
                logger.warning("An inhabitant dropped out of her world; they will all be started again.")
            self._end(process, INHABITANTS_STOP_SECONDS)
        except Exception:
            logger.exception("Could not check on the inhabitants of her Minecraft world.")

    def _look_after_inhabitants(self) -> None:
        self.check_inhabitants()
        self.start_inhabitants()

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
            bridge, server, inhabitants = self._bridge, self._server, self._inhabitants
            self._bridge = self._server = self._inhabitants = None
            # A stop that was asked for is not a crash: they may start again at once.
            self._inhabitants_started = None
            logs, self._logs = self._logs, []
            self._watch_stop.set()
        if bridge is not None or server is not None or inhabitants is not None:
            logger.info("Stopping her Minecraft world.")
        # The inhabitants first, then the bridge, so everyone has left before
        # the world closes.
        self._end(inhabitants, INHABITANTS_STOP_SECONDS)
        self._end(bridge, BRIDGE_STOP_SECONDS)
        self._end(server, SERVER_STOP_SECONDS)
        for handle in logs:
            try:
                handle.close()
            except Exception:
                pass
