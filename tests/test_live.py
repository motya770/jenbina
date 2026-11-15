"""Live drawing and shared-host session integration without external services."""

import unittest
import runpy
import sys
from contextlib import ExitStack, nullcontext
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.heartbeat.host import _PROCESS_HOST, ChatTurn, NotHostingError
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
    def setUp(self):
        # The process host is kept on sys so it survives reloads; tests start clean.
        saved = sys.__dict__.pop(_PROCESS_HOST, None)
        self.addCleanup(lambda: sys.__dict__.pop(_PROCESS_HOST, None) if saved is None
                        else sys.__dict__.__setitem__(_PROCESS_HOST, saved))

    def test_a_cache_clear_or_reload_never_builds_a_second_host(self):
        first = MagicMock(hosting=True)
        with patch.object(shared_init, "_build_host", return_value=first) as build:
            self.assertIs(shared_init.get_host(), first)
            # What a hot reload or "Clear cache" amounts to: the module's own
            # references are gone, the process and the first host are not.
            self.assertIs(shared_init.get_host(), first)
            self.assertEqual(build.call_count, 1)
        with patch.object(shared_init, "_build_host", return_value=MagicMock()) as rebuilt:
            self.assertIs(shared_init.get_host(), first)
            rebuilt.assert_not_called()

    def test_adoption_override_comes_from_the_environment(self):
        with patch.dict("os.environ", {"JENBINA_ADOPT_USER_ID": "3"}):
            self.assertEqual(shared_init._adopt_user_id(), 3)
        with patch.dict("os.environ", {"JENBINA_ADOPT_USER_ID": "three"}):
            self.assertIsNone(shared_init._adopt_user_id())
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(shared_init._adopt_user_id())

    def test_cached_host_retries_start_after_a_refused_lease(self):
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
        factory.assert_called_once_with(store.return_value, db.return_value, "chat", "json", "insight",
                                        adopt_user_id=None)

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
    def run_home(self, *, message=None, clicked=False, chat_error=None):
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
        # The beat's summary names where it started; she has walked on since.
        host.situation.history = [{"world_summary": {"location": {"name": "Jenbina's House", "type": "home"}},
                                   "action_decision": {"chosen_action": "Read"}}]
        host.situation.location = "Coupa Cafe"
        world = {"location": {"name": "Coupa Cafe", "type": "home"}}
        turn = ChatTurn("Bob (2)", 2, False, {}, [], host.event_log)
        host.chat_turn.return_value = nullcontext(turn)
        if chat_error is not None:
            host.chat_turn.side_effect = chat_error
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

    def test_a_message_sent_mid_beat_says_it_is_waiting(self):
        st, _, _, _, _, _ = self.run_home(message="hello")
        waiting = st.empty.return_value
        waiting.info.assert_called_once_with(
            "Jenbina is finishing what she was doing. Your message is waiting for her.")
        waiting.empty.assert_called_once()

    def test_the_place_line_shows_where_she_is_now(self):
        _, host, mocks, _, _, _ = self.run_home()
        shown = mocks["core.ui.rail.render_status_rail"].call_args.args[1]
        self.assertEqual(shown["location"]["name"], "Coupa Cafe")
        self.assertEqual(host.situation.history[0]["world_summary"]["location"]["name"], "Jenbina's House")

    def test_a_message_after_she_moved_away_gets_a_plain_notice(self):
        st, _, mocks, _, _, _ = self.run_home(message="hello", chat_error=NotHostingError("gone"))
        mocks["core.ui.chat.handle_user_input"].assert_not_called()
        self.assertIn("moved to another process", st.info.call_args.args[0])
        st.rerun.assert_not_called()

    def test_step_once_uses_the_host_and_reruns_the_app(self):
        st, host, _, _, _, _ = self.run_home(clicked=True)
        host.request_step.assert_called_once_with()
        host.step_once.assert_not_called()                     # never block the page for a beat
        st.rerun.assert_called_once()
