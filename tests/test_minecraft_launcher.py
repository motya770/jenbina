#!/usr/bin/env python3
"""Tests for the launcher that starts and stops her Minecraft world's
processes. Nothing here starts a real process or opens a real port."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.environment.minecraft import WorldUnavailable
from core.environment.minecraft.launcher import WorldLauncher, is_local, server_port


class FakeProcess:
    def __init__(self, command):
        self.command = command
        self.returncode = None
        self.signals = []
        self.stubborn = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.signals.append("terminate")
        if not self.stubborn:
            self.returncode = 0

    def kill(self):
        self.signals.append("kill")
        self.returncode = -9

    def wait(self, timeout=None):
        if self.returncode is None:
            raise subprocess.TimeoutExpired(self.command, timeout)
        return self.returncode


class FakeBridge:
    base_url = "http://127.0.0.1:3010"

    def __init__(self):
        self.alive = False

    def health(self):
        if not self.alive:
            raise WorldUnavailable("connection refused")
        return {"ok": True}


class LauncherCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.server_dir = self.root / "minecraft" / "server"
        self.bridge_dir = self.root / "minecraft" / "bridge"
        self.server_dir.mkdir(parents=True)
        (self.bridge_dir / "node_modules").mkdir(parents=True)
        (self.server_dir / "server.jar").write_bytes(b"jar")
        (self.server_dir / "eula.txt").write_text("#Mojang\neula=true\n")
        (self.server_dir / "server.properties").write_text("server-ip=127.0.0.1\nserver-port=25570\n")
        self.bridge = FakeBridge()
        self.server_up = False
        self.spawned = []
        self.installed = {"java", "node"}
        self.time = 0.0
        self.on_sleep = lambda: None

    def spawn(self, command, **kwargs):
        process = FakeProcess(command)
        process.kwargs = kwargs
        self.spawned.append(process)
        return process

    def sleep(self, seconds):
        self.time += seconds
        self.on_sleep()

    def launcher(self, env=None):
        launcher = WorldLauncher(
            self.root, self.bridge, env=env or {},
            spawn=self.spawn, is_port_open=lambda host, port: self.server_up,
            which=lambda name: f"/usr/bin/{name}" if name in self.installed else None,
            sleep=self.sleep, clock=lambda: self.time,
        )
        self.addCleanup(launcher.stop)
        return launcher

    def commands(self):
        return [Path(p.command[-1]).name for p in self.spawned]


class TestStart(LauncherCase):
    def test_starts_the_server_and_the_bridge_when_neither_is_running(self):
        launcher = self.launcher()
        launcher.start()
        self.assertEqual(self.commands(), ["run_server.sh", "bridge.js"])
        server, bridge = self.spawned
        self.assertEqual(bridge.command[0], "node")
        # The bridge is told where the server and its own port are.
        self.assertEqual(bridge.kwargs["env"]["MC_PORT"], "25570")
        self.assertEqual(bridge.kwargs["env"]["BRIDGE_PORT"], "3010")
        for process in self.spawned:
            self.assertTrue(process.kwargs["start_new_session"])
            self.assertEqual(process.kwargs["stdin"], subprocess.DEVNULL)
        self.assertTrue((self.root / "minecraft" / "logs" / "server.log").exists())
        self.assertTrue((self.root / "minecraft" / "logs" / "bridge.log").exists())

    def test_what_is_already_running_is_left_alone(self):
        self.server_up = True
        launcher = self.launcher()
        launcher.start()
        self.assertEqual(self.commands(), ["bridge.js"])
        self.bridge.alive = True
        other = self.launcher()
        other.start()
        self.assertEqual(self.commands(), ["bridge.js"])

    def test_starting_twice_starts_nothing_twice(self):
        launcher = self.launcher()
        launcher.start()
        launcher.start()
        self.assertEqual(len(self.spawned), 2)

    def test_a_process_that_died_is_started_again(self):
        launcher = self.launcher()
        launcher.start()
        self.spawned[0].returncode = 1
        launcher.start()
        self.assertEqual(self.commands(), ["run_server.sh", "bridge.js", "run_server.sh"])

    def test_a_server_that_is_not_set_up_is_explained_and_nothing_starts(self):
        (self.server_dir / "server.jar").unlink()
        with self.assertRaises(WorldUnavailable) as raised:
            self.launcher().start()
        self.assertIn("setup_server.sh --accept-eula", str(raised.exception))
        self.assertEqual(self.spawned, [])

    def test_the_eula_is_never_accepted_here(self):
        (self.server_dir / "eula.txt").write_text("eula=false\n")
        with self.assertRaises(WorldUnavailable) as raised:
            self.launcher().start()
        self.assertIn("EULA is not accepted", str(raised.exception))
        self.assertEqual((self.server_dir / "eula.txt").read_text(), "eula=false\n")
        self.assertEqual(self.spawned, [])

    def test_missing_packages_or_programs_are_explained(self):
        (self.bridge_dir / "node_modules").rmdir()
        self.installed = set()
        with self.assertRaises(WorldUnavailable) as raised:
            self.launcher().start()
        message = str(raised.exception)
        self.assertIn("npm install", message)
        self.assertIn("Java is not installed", message)
        self.assertIn("Node is not installed", message)

    def test_a_server_on_another_machine_is_not_started_here(self):
        launcher = self.launcher({"MC_HOST": "10.0.0.5"})
        launcher.start()
        self.assertEqual(self.commands(), ["bridge.js"])


class TestEnsureReady(LauncherCase):
    def test_costs_nothing_when_everything_is_up(self):
        self.server_up = self.bridge.alive = True
        self.launcher().ensure_ready()
        self.assertEqual(self.spawned, [])
        self.assertEqual(self.time, 0.0)

    def test_waits_until_both_answer(self):
        def come_up():
            if self.time >= 3:
                self.bridge.alive = True
            if self.time >= 20:
                self.server_up = True

        self.on_sleep = come_up
        self.launcher().ensure_ready()
        self.assertEqual(self.commands(), ["run_server.sh", "bridge.js"])
        self.assertEqual(self.time, 20.0)

    def test_gives_up_when_the_world_does_not_come_up_in_time(self):
        with self.assertRaises(WorldUnavailable) as raised:
            self.launcher().ensure_ready(timeout=30)
        self.assertIn("still starting", str(raised.exception))
        self.assertGreaterEqual(self.time, 30.0)

    def test_a_server_that_exits_while_starting_is_reported_at_once(self):
        def crash():
            self.spawned[0].returncode = 1

        self.on_sleep = crash
        with self.assertRaises(WorldUnavailable) as raised:
            self.launcher().ensure_ready()
        self.assertIn("minecraft/logs/server.log", str(raised.exception))
        self.assertLess(self.time, 5.0)

    def test_a_world_that_went_down_is_started_again(self):
        launcher = self.launcher()
        self.on_sleep = lambda: setattr(self, "server_up", True) or setattr(self.bridge, "alive", True)
        launcher.ensure_ready()
        # The server crashes later.
        self.spawned[0].returncode = 1
        self.server_up = False
        launcher.ensure_ready()
        self.assertEqual(self.commands(), ["run_server.sh", "bridge.js", "run_server.sh"])


class TestStop(LauncherCase):
    def test_stops_what_it_started_bridge_first(self):
        launcher = self.launcher()
        launcher.start()
        server, bridge = self.spawned
        order = []
        server.terminate = lambda: (order.append("server"), setattr(server, "returncode", 0))
        bridge.terminate = lambda: (order.append("bridge"), setattr(bridge, "returncode", 0))
        launcher.stop()
        self.assertEqual(order, ["bridge", "server"])
        launcher.stop()
        self.assertEqual(order, ["bridge", "server"])

    def test_does_not_stop_what_it_did_not_start(self):
        self.server_up = self.bridge.alive = True
        launcher = self.launcher()
        launcher.start()
        launcher.stop()
        self.assertEqual(self.spawned, [])

    def test_a_process_that_ignores_the_request_is_killed(self):
        launcher = self.launcher()
        launcher.start()
        self.spawned[1].stubborn = True
        launcher.stop()
        self.assertEqual(self.spawned[1].signals, ["terminate", "kill"])
        self.assertEqual(self.spawned[0].signals, ["terminate"])

    def test_stop_never_raises(self):
        launcher = self.launcher()
        launcher.start()

        def explode():
            raise PermissionError("not yours")

        self.spawned[0].terminate = explode
        launcher.stop()

    def test_it_can_start_again_after_stopping(self):
        launcher = self.launcher()
        launcher.start()
        launcher.stop()
        launcher.start()
        self.assertEqual(len(self.spawned), 4)


class TestHelpers(unittest.TestCase):
    def test_local_hosts(self):
        for host in ("127.0.0.1", "localhost", " LOCALHOST ", "::1"):
            self.assertTrue(is_local(host))
        for host in ("10.0.0.5", "example.org", "", None):
            self.assertFalse(is_local(host))

    def test_server_port_comes_from_the_environment_then_the_properties(self):
        with tempfile.TemporaryDirectory() as folder:
            properties = Path(folder) / "server.properties"
            self.assertEqual(server_port(properties, {}), 25565)
            properties.write_text("motd=hi\nserver-port = 25570\n")
            self.assertEqual(server_port(properties, {}), 25570)
            self.assertEqual(server_port(properties, {"MC_PORT": "25580"}), 25580)
            self.assertEqual(server_port(properties, {"MC_PORT": "nonsense"}), 25565)


if __name__ == "__main__":
    unittest.main()
