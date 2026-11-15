"""Standalone heartbeat CLI tests; no real LLMs or background threads."""

import io
import os
from pathlib import Path
import signal
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, call, patch

from core.heartbeat.host import JenbinaHost
from run_heartbeat import build_host, main


ROOT = Path(__file__).resolve().parents[1]


class TestHeartbeatMain(unittest.TestCase):
    def setUp(self):
        self.host = MagicMock(spec=JenbinaHost)
        self.host.start.return_value = True
        self.factory = MagicMock(return_value=self.host)

    def test_exits_1_when_she_lives_elsewhere(self):
        self.host.start.return_value = False
        self.host.status.return_value.holder = "other:1:zz"
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(main(["--once"], host_factory=self.factory), 1)
        self.assertEqual(stderr.getvalue(),
                         "Jenbina is already living in another process (other:1:zz).\n")
        self.host.start.assert_called_once_with(threads=False)
        self.host.step_once.assert_not_called()
        self.host.run_forever.assert_not_called()
        self.host.stop.assert_not_called()

    def test_once_beats_once_and_stops(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}), \
                patch("run_heartbeat.UserDatabase") as database, \
                patch("run_heartbeat.get_llm") as llm, \
                patch("run_heartbeat.get_json_llm") as json_llm:
            self.assertEqual(main(["--once"], host_factory=self.factory), 0)
        self.factory.assert_called_once_with(adopt_user_id=None)
        self.assertEqual(self.host.mock_calls, [
            call.start(threads=False), call.step_once(), call.stop(),
        ])
        database.assert_not_called()
        llm.assert_not_called()
        json_llm.assert_not_called()

    def test_adopt_user_id_reaches_the_host(self):
        self.assertEqual(main(["--once", "--adopt-user-id", "3"],
                              host_factory=self.factory), 0)
        self.factory.assert_called_once_with(adopt_user_id=3)

    def test_default_factory_is_used_when_none_is_injected(self):
        with patch("run_heartbeat.build_host", return_value=self.host) as factory:
            self.assertEqual(main(["--once"]), 0)
        factory.assert_called_once_with(adopt_user_id=None)

    def test_once_stops_even_when_the_step_raises(self):
        self.host.step_once.side_effect = RuntimeError("cannot save")
        with self.assertRaisesRegex(RuntimeError, "cannot save"):
            main(["--once"], host_factory=self.factory)
        self.host.stop.assert_called_once_with()

    def test_without_once_runs_forever_and_restores_signal_handlers(self):
        with patch("run_heartbeat.signal.signal", side_effect=[
            signal.default_int_handler, signal.SIG_DFL, None, None,
        ]) as register:
            self.assertEqual(main([], host_factory=self.factory), 0)
        self.assertEqual(self.host.mock_calls, [
            call.start(threads=False), call.run_forever(), call.stop(),
        ])
        self.assertEqual(register.call_args_list[0].args[0], signal.SIGINT)
        self.assertEqual(register.call_args_list[1].args[0], signal.SIGTERM)
        self.assertCountEqual(register.call_args_list[2:], [
            call(signal.SIGINT, signal.default_int_handler),
            call(signal.SIGTERM, signal.SIG_DFL),
        ])

    def test_both_shutdown_signals_stop_the_host(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum), \
                    patch("run_heartbeat.signal.signal") as register:
                self.host.reset_mock()

                def receive_signal():
                    handlers = dict(c.args for c in register.call_args_list)
                    handlers[signum](signum, None)
                    self.host.stop.assert_called_once_with()

                self.host.run_forever.side_effect = receive_signal
                self.assertEqual(main([], host_factory=self.factory), 0)

    def test_continuous_run_stops_and_restores_handlers_on_error(self):
        self.host.run_forever.side_effect = RuntimeError("loop failed")
        with patch("run_heartbeat.signal.signal", return_value=signal.SIG_DFL) as register:
            with self.assertRaisesRegex(RuntimeError, "loop failed"):
                main([], host_factory=self.factory)
        self.host.stop.assert_called_once_with()
        self.assertCountEqual(register.call_args_list[2:], [
            call(signal.SIGINT, signal.SIG_DFL), call(signal.SIGTERM, signal.SIG_DFL),
        ])

    def test_list_users_prints_the_table_without_building_a_host_or_llms(self):
        users = [
            {"id": 1, "display_name": "Ann", "email": "ann@example.com"},
            {"id": 2, "display_name": None, "email": "bob@example.com"},
        ]
        stdout = io.StringIO()
        with patch("run_heartbeat.UserDatabase") as database, \
                patch("run_heartbeat.get_llm") as llm, \
                patch("run_heartbeat.get_json_llm") as json_llm, \
                redirect_stdout(stdout):
            database.return_value.get_all_users.return_value = users
            self.assertEqual(main(["--list-users"], host_factory=self.factory), 0)
        self.assertEqual(stdout.getvalue().splitlines(), [
            f"{'ID':<6} {'Display Name':<30} {'Email':<40}",
            "-" * 76,
            f"{1:<6} {'Ann':<30} {'ann@example.com':<40}",
            f"{2:<6} {'':<30} {'bob@example.com':<40}",
        ])
        database.return_value.get_all_users.assert_called_once_with()
        self.factory.assert_not_called()
        llm.assert_not_called()
        json_llm.assert_not_called()

    def test_list_users_handles_an_empty_database(self):
        stdout = io.StringIO()
        with patch("run_heartbeat.UserDatabase") as database, redirect_stdout(stdout):
            database.return_value.get_all_users.return_value = []
            self.assertEqual(main(["--list-users"], host_factory=self.factory), 0)
        self.assertEqual(stdout.getvalue(), "No users found in database.\n")
        self.factory.assert_not_called()

    def test_scheduler_is_gone(self):
        self.assertFalse((ROOT / "run_scheduler.py").exists())
        self.assertNotIn("apscheduler", (ROOT / "requirements.txt").read_text())


class TestBuildHost(unittest.TestCase):
    def test_builds_the_host_with_shared_storage_and_the_ui_llm_configuration(self):
        for chat_model in (None, "openai"):
            with self.subTest(chat_model=chat_model), \
                    patch.dict(os.environ), \
                    patch("run_heartbeat.UserDatabase") as database, \
                    patch("run_heartbeat.BeingStore") as store, \
                    patch("run_heartbeat.get_llm") as get_llm, \
                    patch("run_heartbeat.get_json_llm") as get_json_llm, \
                    patch("run_heartbeat.JenbinaHost") as host:
                os.environ.pop("OPENAI_CHAT_MODEL", None)
                if chat_model is not None:
                    os.environ["OPENAI_CHAT_MODEL"] = chat_model
                llm, insight_llm = MagicMock(), MagicMock()
                get_llm.side_effect = [llm, insight_llm]
                database.return_value.db_path = "/tmp/heartbeat-test/users.db"

                self.assertIs(build_host(adopt_user_id=3), host.return_value)

                store.assert_called_once_with("/tmp/heartbeat-test/users.db")
                self.assertEqual(get_llm.call_args_list, [
                    call(provider=chat_model or "openai-advanced", temperature=1, max_tokens=600),
                    call(provider="openai-advanced", temperature=0.8, max_tokens=500),
                ])
                get_json_llm.assert_called_once_with(provider="openai", temperature=1)
                host.assert_called_once_with(
                    store=store.return_value, user_db=database.return_value,
                    llm=llm, llm_json_mode=get_json_llm.return_value,
                    insight_llm=insight_llm, adopt_user_id=3,
                )
