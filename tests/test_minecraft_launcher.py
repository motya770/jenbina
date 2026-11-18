#!/usr/bin/env python3
"""Tests for the launcher that starts and stops her Minecraft world's
processes. Nothing here starts a real process or opens a real port."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.environment.minecraft import WorldUnavailable
from core.environment.minecraft.launcher import (
    DEFAULT_MINDSERVER_PORT, INHABITANT_CALLS_PER_HOUR, WorldLauncher, inhabitant_settings, is_local,
    server_port,
)


class FakeProcess:
    def __init__(self, command):
        self.command = command
        self.returncode = None
        self.signals = []
        self.stubborn = False
        self.stopped = []

    def poll(self):
        return self.returncode

    def terminate(self):
        self.signals.append("terminate")
        self.stopped.append(self)
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
        self.inhabitants_up = False
        self.stopped = []
        self.spawned = []
        self.installed = {"java", "node"}
        self.time = 0.0
        self.on_sleep = lambda: None

    def spawn(self, command, **kwargs):
        process = FakeProcess(command)
        process.kwargs = kwargs
        process.stopped = self.stopped
        self.spawned.append(process)
        return process

    def sleep(self, seconds):
        self.time += seconds
        self.on_sleep()

    def launcher(self, env=None):
        launcher = WorldLauncher(
            self.root, self.bridge, env=env or {},
            spawn=self.spawn, is_port_open=self.port_open,
            which=lambda name: f"/usr/bin/{name}" if name in self.installed else None,
            sleep=self.sleep, clock=lambda: self.time, watch_seconds=None,
        )
        self.addCleanup(launcher.stop)
        return launcher

    def port_open(self, host, port):
        return self.inhabitants_up if port == DEFAULT_MINDSERVER_PORT else self.server_up

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


class InhabitantsCase(LauncherCase):
    """A world that is up, with Mindcraft set up beside it."""

    ENV = {"OPENAI_API_KEY": "test-key", "PATH": "/usr/bin", "SERPAPI_API_KEY": "other-secret"}

    def setUp(self):
        super().setUp()
        self.server_up = self.bridge.alive = True
        self.mindcraft = self.root / "minecraft" / "mindcraft"
        self.profiles = self.root / "minecraft" / "inhabitants"
        self.log = self.root / "minecraft" / "logs" / "inhabitants.log"
        self.set_up_inhabitants()

    def set_up_inhabitants(self):
        (self.mindcraft / "node_modules").mkdir(parents=True)
        (self.mindcraft / "main.js").write_text("// mindcraft")
        self.profiles.mkdir(parents=True)
        for name in ("tobin", "mira"):
            (self.profiles / f"{name}.json").write_text(json.dumps({"name": name.capitalize()}))

    def inhabitants(self):
        return [p for p in self.spawned if "main.js" in p.command]

    def ready(self, env=None, launcher=None):
        launcher = launcher or self.launcher(dict(self.ENV) if env is None else env)
        launcher.ensure_ready()
        return launcher

    def say_in_log(self, text):
        with open(self.log, "ab") as handle:
            handle.write(text.encode())


class TestInhabitants(InhabitantsCase):
    def test_settings_never_allow_code_and_stay_local(self):
        settings = inhabitant_settings(25570, 3011)
        self.assertIs(settings["allow_insecure_coding"], False)
        self.assertIs(settings["allow_vision"], False)
        self.assertIs(settings["auto_open_ui"], False)
        self.assertIs(settings["narrate_behavior"], False)
        self.assertIs(settings["load_memory"], True)
        self.assertEqual((settings["host"], settings["port"], settings["auth"]), ("127.0.0.1", 25570, "offline"))
        self.assertEqual((settings["minecraft_version"], settings["base_profile"]), ("1.21.4", "survival"))
        self.assertEqual((settings["only_chat_with"], settings["init_message"]), ([], ""))
        self.assertEqual((settings["max_commands"], settings["mindserver_port"]), (3, 3011))
        for command in ("!startConversation", "!attackPlayer", "!newAction",
                        "!checkBlueprint", "!checkBlueprintLevel", "!getBlueprint", "!getBlueprintLevel"):
            self.assertIn(command, settings["blocked_actions"])

    def test_inhabitants_start_only_after_the_server_answers(self):
        self.server_up = self.bridge.alive = False
        launcher = self.launcher(dict(self.ENV))
        launcher.start()
        self.assertEqual(self.inhabitants(), [])
        self.server_up = self.bridge.alive = True
        launcher.ensure_ready()
        (process,) = self.inhabitants()
        self.assertEqual(process.command, [
            "node", "main.js", "--profiles",
            str(self.profiles / "mira.json"), str(self.profiles / "tobin.json")])
        self.assertEqual(process.kwargs["cwd"], str(self.mindcraft))
        self.assertEqual(json.loads(process.kwargs["env"]["SETTINGS_JSON"]), inhabitant_settings(25570, 3011))
        self.assertTrue(process.kwargs["start_new_session"])
        self.assertTrue(self.log.exists())

    def test_they_are_given_her_openai_key_and_no_other_secret(self):
        self.ready()
        env = self.inhabitants()[0].kwargs["env"]
        self.assertEqual(env["OPENAI_API_KEY"], "test-key")
        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertNotIn("SERPAPI_API_KEY", env)

    def test_a_world_that_is_already_up_gets_them_too(self):
        self.ready()
        self.assertEqual(len(self.spawned), 1)
        self.assertEqual(len(self.inhabitants()), 1)

    def test_looking_twice_starts_them_once(self):
        launcher = self.ready()
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 1)

    def test_not_set_up_means_she_lives_alone_and_nothing_fails(self):
        (self.mindcraft / "main.js").unlink()
        with self.assertLogs("jenbina.minecraft", level="INFO") as logs:
            launcher = self.ready()
            launcher.ensure_ready()
        self.assertEqual(self.inhabitants(), [])
        said = [line for line in logs.output if "setup_inhabitants.sh" in line]
        self.assertEqual(len(said), 1)

    def test_no_profiles_means_alone(self):
        for profile in self.profiles.glob("*.json"):
            profile.unlink()
        self.ready()
        self.assertEqual(self.inhabitants(), [])

    def test_no_key_means_alone(self):
        with self.assertLogs("jenbina.minecraft", level="INFO") as logs:
            launcher = self.ready(env={"PATH": "/usr/bin"})
            launcher.ensure_ready()
        self.assertEqual(self.inhabitants(), [])
        self.assertEqual(len([line for line in logs.output if "OPENAI_API_KEY" in line]), 1)
        self.assertNotIn("test-key", " ".join(logs.output))

    def test_switched_off_means_alone(self):
        with self.assertNoLogs("jenbina.minecraft", level="INFO"):
            self.ready(env={**self.ENV, "JENBINA_MINECRAFT_INHABITANTS": "0"})
        self.assertEqual(self.inhabitants(), [])

    def test_no_node_means_alone(self):
        self.installed = {"java"}
        self.ready()
        self.assertEqual(self.inhabitants(), [])

    def test_already_running_inhabitants_are_used_and_left_running(self):
        self.inhabitants_up = True
        launcher = self.ready()
        self.assertEqual(self.inhabitants(), [])
        launcher.stop()
        self.assertEqual(self.stopped, [])

    def test_a_crashing_inhabitants_process_is_not_restarted_in_a_loop(self):
        launcher = self.ready()
        self.inhabitants()[0].returncode = 1
        self.time = 60.0
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 1)
        self.time = 601.0
        launcher.ensure_ready()
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 2)

    def test_a_chosen_node_runs_them(self):
        self.ready(env={**self.ENV, "MINDCRAFT_NODE": "/opt/node20/bin/node"})
        self.assertEqual(self.inhabitants()[0].command[0], "/opt/node20/bin/node")

    def test_the_node_the_setup_installed_is_used_before_the_machines_own(self):
        private = self.root / "minecraft" / "mindcraft-node" / "node_modules" / "node" / "bin" / "node"
        private.parent.mkdir(parents=True)
        private.write_text("")
        self.ready()
        self.assertEqual(self.inhabitants()[0].command[0], str(private))

    def test_a_node_that_cannot_be_run_fails_nothing(self):
        def broken(command, **kwargs):
            if "main.js" in command:
                raise FileNotFoundError(command[0])
            return self.spawn(command, **kwargs)

        launcher = WorldLauncher(self.root, self.bridge, env=dict(self.ENV), spawn=broken,
                                 is_port_open=self.port_open, which=lambda name: f"/usr/bin/{name}",
                                 sleep=self.sleep, clock=lambda: self.time, watch_seconds=None)
        self.addCleanup(launcher.stop)
        launcher.ensure_ready()
        launcher.ensure_ready()
        self.assertEqual(self.inhabitants(), [])

    def test_they_are_stopped_first(self):
        self.server_up = self.bridge.alive = False
        launcher = self.launcher(dict(self.ENV))
        self.on_sleep = lambda: setattr(self, "server_up", True) or setattr(self.bridge, "alive", True)
        launcher.ensure_ready()
        self.assertEqual(self.commands(), ["run_server.sh", "bridge.js", "tobin.json"])
        launcher.stop()
        self.assertEqual([Path(p.command[-1]).name for p in self.stopped],
                         ["tobin.json", "bridge.js", "run_server.sh"])

    def test_they_come_back_with_her_after_a_stop(self):
        launcher = self.ready()
        launcher.stop()
        self.time = 5.0
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 2)

    def test_a_remote_server_gets_no_inhabitants(self):
        self.ready(env={**self.ENV, "MC_HOST": "10.0.0.5"})
        self.assertEqual(self.inhabitants(), [])


class TestInhabitantsWatch(InhabitantsCase):
    CALL = "Awaiting openai api response from model gpt-5-nano\n"

    def test_ordinary_talk_leaves_them_running(self):
        launcher = self.ready()
        self.say_in_log(self.CALL * INHABITANT_CALLS_PER_HOUR)
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, [])

    def test_too_many_llm_calls_in_an_hour_stops_them_for_good(self):
        launcher = self.ready()
        self.say_in_log(self.CALL * 40)
        launcher.check_inhabitants()
        self.time = 1800.0
        self.say_in_log(self.CALL * 21)
        with self.assertLogs("jenbina.minecraft", level="ERROR") as logs:
            launcher.check_inhabitants()
        self.assertEqual(self.stopped, self.inhabitants())
        self.assertIn("inhabitants.log", " ".join(logs.output))
        self.time = 9000.0
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 1)

    def test_calls_older_than_an_hour_are_forgotten(self):
        launcher = self.ready()
        self.say_in_log(self.CALL * 40)
        launcher.check_inhabitants()
        self.time = 3700.0
        self.say_in_log(self.CALL * 40)
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, [])

    def test_what_was_in_the_log_before_they_started_is_not_counted(self):
        self.log.parent.mkdir(parents=True)
        self.say_in_log(self.CALL * 500)
        launcher = self.ready()
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, [])

    def test_a_line_still_being_written_is_counted_once(self):
        launcher = self.ready()
        self.say_in_log(self.CALL * 60 + "Awaiting openai api")
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, [])
        self.say_in_log(" response from model gpt-5-nano\n")
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, self.inhabitants())

    def test_an_inhabitant_that_dropped_out_brings_a_restart_but_not_at_once(self):
        launcher = self.ready()
        self.say_in_log("Agent process exited too quickly and will not be restarted.\n")
        self.time = 120.0
        launcher.check_inhabitants()
        self.assertEqual(self.stopped, self.inhabitants())
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 1)
        self.time = 700.0
        launcher.ensure_ready()
        self.assertEqual(len(self.inhabitants()), 2)

    def test_checking_never_raises(self):
        launcher = self.ready()
        self.log.unlink()
        launcher.check_inhabitants()
        self.launcher().check_inhabitants()


if __name__ == "__main__":
    unittest.main()
