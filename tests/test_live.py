"""Live drawing and shared-host session integration without external services."""

import unittest
import runpy
import sys
from contextlib import ExitStack, nullcontext
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.heartbeat.host import ChatTurn
from core.ui.live import draw_guarded
from core.ui import shared_init
from tests.test_greeting_generation import _FakeSessionState


class TestLiveDrawing(unittest.TestCase):
    def test_a_failing_draw_shows_no_traceback(self):
        with patch("core.ui.live.st") as st, patch("builtins.print") as log:
            self.assertFalse(draw_guarded(lambda: {}["missing"]))
            st.caption.assert_called_once()
            st.exception.assert_not_called()
            log.assert_called_once()
            self.assertTrue(draw_guarded(lambda: None))


class TestSharedHost(unittest.TestCase):
    def test_cached_host_retries_start_after_a_refused_lease(self):
        shared_init._cached_host.clear()
        self.addCleanup(shared_init._cached_host.clear)
        host = MagicMock(hosting=False)
        def start():
            host.hosting = host.start.call_count > 1
            return host.hosting
        host.start.side_effect = start
        with patch.object(shared_init, "JenbinaHost", return_value=host) as factory, \
                patch.object(shared_init, "BeingStore") as store, \
                patch.object(shared_init, "UserDatabase") as db, \
                patch.object(shared_init, "init_llm", return_value=("chat", "json")), \
                patch.object(shared_init, "get_llm", return_value="insight"):
            self.assertIs(shared_init.get_host(), host)
            self.assertFalse(host.hosting)
            self.assertIs(shared_init.get_host(), host)
            self.assertTrue(host.hosting)
            self.assertIs(shared_init.get_host(), host)
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(host.start.call_count, 2)
        factory.assert_called_once_with(store.return_value, db.return_value, "chat", "json", "insight")

    def test_auth_replaces_session_copies_with_host_references_on_every_run(self):
        host = MagicMock(hosting=True)
        with patch.object(shared_init, "st") as st, \
                patch.dict("os.environ", {"JENBINA_SKIP_AUTH": "0"}), \
                patch.object(shared_init, "get_host", return_value=host), \
                patch.object(shared_init, "render_auth_page", return_value=True), \
                patch.object(shared_init, "render_user_header"), \
                patch.object(shared_init, "init_session_state"):
            st.session_state = _FakeSessionState(current_user={"id": 1}, person=object())
            self.assertTrue(shared_init.require_auth())
            self.assertIs(st.session_state.person, host.person)
            self.assertIs(st.session_state.meta_cognitive_system, host.meta_cognitive_system)
            host.person = object()
            self.assertTrue(shared_init.require_auth())
            self.assertIs(st.session_state.person, host.person)

    def test_auth_refuses_another_process_without_initializing_a_private_person(self):
        with patch.object(shared_init, "st") as st, \
                patch.dict("os.environ", {"JENBINA_SKIP_AUTH": "0"}), \
                patch.object(shared_init, "get_host", return_value=MagicMock(hosting=False)), \
                patch.object(shared_init, "render_auth_page", return_value=True), \
                patch.object(shared_init, "render_user_header"), \
                patch.object(shared_init, "init_session_state") as init:
            st.session_state = _FakeSessionState(current_user={"id": 1})
            self.assertFalse(shared_init.require_auth())
            init.assert_not_called()
            self.assertNotIn("person", st.session_state)
            st.info.assert_called_once_with(
                "Jenbina is already living in another process. This window cannot reach her until that one stops."
            )


class TestHomeScreen(unittest.TestCase):
    def run_home(self, *, message=None, clicked=False):
        stack = ExitStack()
        self.addCleanup(stack.close)
        st = MagicMock()
        st.session_state = _FakeSessionState(current_user={"id": 2, "display_name": "Bob"}, memory_manager=object())
        st.columns.return_value = [MagicMock(), MagicMock()]
        st.radio.return_value = "All"
        st.chat_input.return_value = message
        fragments = []
        in_fragment = []

        def fragment(**kwargs):
            self.assertEqual(kwargs, {"run_every": 5})
            def decorate(draw):
                def refresh():
                    in_fragment.append(True)
                    try:
                        return draw()
                    finally:
                        in_fragment.pop()
                fragments.append(refresh)
                return refresh
            return decorate

        st.fragment.side_effect = fragment
        st.chat_input.side_effect = lambda *a, **kw: self.assertFalse(in_fragment) or message
        host = MagicMock()
        host.person_key.return_value = "Bob (2)"
        host.person.name = "Jenbina"
        host.status.return_value.busy = bool(message)
        host.status.return_value.stage = "thinking…"
        host.situation.phase = "asleep"
        world = {"location": {"name": "Coupa Cafe"}}
        host.situation.history = [{"world_summary": world, "action_decision": {"chosen_action": "Read"}}]
        turn = ChatTurn("Bob (2)", 2, False, {}, [], host.event_log)
        host.chat_turn.return_value = nullcontext(turn)
        replacements = {
            "core.ui.shared_init.require_auth": True,
            "core.ui.shared_init.get_host": host,
            "core.ui.shared_init.init_llm": ("chat llm", "json llm"),
            "core.ui.pixel_theme.inject_pixel_css": None,
            "core.ui.chat.ensure_greeting": None,
            "core.ui.chat.handle_user_input": None,
            "core.ui.chat.update_system_stage": None,
            "core.ui.rail.render_status_rail": MagicMock(),
            "core.ui.rail.render_heartbeat_card": clicked,
            "core.ui.rail.render_mind_card": None,
            "core.ui.timeline.build_timeline": [],
            "core.ui.timeline.render_timeline": None,
            "core.ui.timeline.scroll_timeline_to_bottom": None,
        }
        mocks = {name: stack.enter_context(patch(name, return_value=value)) for name, value in replacements.items()}
        # Imported here so the pre-implementation failure reports the missing module.
        stack.enter_context(patch("core.ui.admin.is_admin", return_value=True))
        stack.enter_context(patch.dict(sys.modules, {"streamlit": st}))
        runpy.run_path(str(Path(__file__).resolve().parents[1] / "core" / "app.py"))
        return st, host, mocks, fragments, turn, world

    def test_refreshes_shared_life_and_partner_history_without_starting_a_beat(self):
        st, host, mocks, fragments, _, world = self.run_home()
        self.assertEqual(len(fragments), 2)
        host.step_once.assert_not_called()
        host.chat_turn.assert_not_called()
        host.person.get_conversation_history.assert_called_with("Bob (2)", count=100)
        build = mocks["core.ui.timeline.build_timeline"]
        self.assertEqual(build.call_args.args[:3], (
            host.person.get_conversation_history.return_value, host.event_log.recent.return_value, "Jenbina",
        ))
        rail = mocks["core.ui.rail.render_status_rail"]
        self.assertEqual(rail.call_args.args[:3], (host.person, world, "Read"))
        rail.return_value.stage.assert_called_with("thinking…")
        self.assertTrue(rail.return_value.portrait.call_args.args[0].endswith("jenbina_sleep.png"))
        mocks["core.ui.rail.render_mind_card"].assert_called_with(host.person, "Bob (2)")
        greeting = mocks["core.ui.chat.ensure_greeting"]
        before = greeting.call_count
        fragments[0]()
        self.assertGreater(greeting.call_count, before)
        self.assertEqual(st.chat_input.call_count, 1)

    def test_submitted_chat_uses_a_host_turn_and_shows_the_waiting_stage(self):
        st, host, mocks, _, turn, _ = self.run_home(message="hello")
        mocks["core.ui.chat.update_system_stage"].assert_called_with("finishing what she was doing…")
        host.chat_turn.assert_called_once_with(st.session_state.current_user)
        mocks["core.ui.chat.handle_user_input"].assert_called_once_with(
            host.person, "chat llm", st.session_state.memory_manager, False, "hello", turn,
        )
        st.rerun.assert_called_once()

    def test_step_once_uses_the_host_and_reruns_the_app(self):
        st, host, _, _, _, _ = self.run_home(clicked=True)
        host.step_once.assert_called_once_with()
        st.spinner.assert_called_once_with("Jenbina is living a moment…")
        st.rerun.assert_called_once()
