#!/usr/bin/env python3
"""Tests for the chat flow helpers in core.ui.chat: outreach message types,
inline input handling and the mood event recorded after a chat."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.timeline import EventLog
from core.ui.chat import ensure_outreach, get_event_log, handle_user_input, send_proactive_message
from tests.test_greeting_generation import _FakeSessionState


class TestOutreachTypes(unittest.TestCase):
    @patch("core.ui.chat.send_proactive_message", return_value=None)
    @patch("core.ui.chat.check_return_greeting", return_value="You're back!")
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_greeting_is_stored_with_greeting_type(self, st, *_):
        st.session_state = _FakeSessionState(proactive_checked=True)
        person = MagicMock()
        ensure_outreach(person, None)
        person.send_message.assert_called_once_with("Matt", "You're back!", "greeting")

    @patch("core.ui.chat.generate_proactive_message", return_value="Still there?")
    @patch("core.ui.chat.check_proactive_message", return_value={"low_social": {}})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_proactive_is_stored_with_proactive_type(self, st, *_):
        st.session_state = _FakeSessionState()
        person = MagicMock()
        send_proactive_message(person, None)
        person.send_message.assert_called_once_with("Matt", "Still there?", "proactive")


class TestHandleUserInput(unittest.TestCase):
    @patch("core.ui.chat.st")
    def test_empty_input_returns_none_without_chat_input(self, st):
        self.assertIsNone(handle_user_input(MagicMock(), None, None, False, ""))
        st.chat_input.assert_not_called()

    @patch("core.ui.chat.analyze_emotion_impact", return_value={"joy": 6})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey", "user_message": "hi", "insight": "x"})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_chat_records_mood_event_and_no_insight_bubble(self, st, *_):
        log = EventLog()
        st.session_state = _FakeSessionState(
            event_log=log, action_history=[], needs_response=None, world_description=None,
            action_decision=None, state_response=None, simulation_history=[],
        )
        snaps = iter([{"joy": 30}, {"joy": 36}])
        person = MagicMock()
        person.get_emotions_snapshot.side_effect = lambda: next(snaps)
        person.social_cognition = None
        result = handle_user_input(person, None, None, False, "hi")
        self.assertEqual(result["assistant_response"], "hey")
        self.assertEqual([e.kind for e in log.recent()], ["mood"])
        self.assertEqual(log.recent()[0].detail["source"], "chat")
        st.chat_message.assert_not_called()


class TestEventLogPerUser(unittest.TestCase):
    @patch("core.ui.chat._get_user_db_and_id", return_value=(MagicMock(), 2))
    @patch("core.ui.chat.st")
    def test_event_log_follows_the_logged_in_user(self, st, _):
        stale = EventLog(MagicMock(), 1)
        st.session_state = _FakeSessionState(event_log=stale)
        log = get_event_log()
        self.assertEqual(log.user_id, 2)
        self.assertIs(st.session_state["event_log"], log)



RECORD = {
    "action_decision": {"chosen_action": "Walk to Coupa Cafe"},
    "world_summary": {
        "location": {"name": "Jenbina's House"},
        "time": {"time_of_day": "evening"},
        "weather": {"description": "Clear skies"},
    },
}


class TestHistoryShapedContext(unittest.TestCase):
    @patch("core.ui.chat.generate_proactive_message", return_value="Still there?")
    @patch("core.ui.chat.check_proactive_message", return_value={"low_social": {}})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_proactive_message_reads_runner_history_records(self, st, _name, _db, _check, gen):
        st.session_state = _FakeSessionState(simulation_history=[dict(RECORD)])
        person = MagicMock()
        self.assertEqual(send_proactive_message(person, None), "Still there?")
        self.assertEqual(gen.call_args.kwargs["recent_actions"], ["Walk to Coupa Cafe"])
        self.assertEqual(gen.call_args.kwargs["world_context"], "Jenbina's House, evening, Clear skies")

    @patch("core.ui.chat.analyze_emotion_impact", return_value={})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey", "user_message": "hi"})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_chat_reply_sees_recent_actions(self, st, _name, _db, chat, _emotion):
        st.session_state = _FakeSessionState(
            event_log=EventLog(), action_history=[], needs_response=None, world_description=None,
            action_decision=None, state_response=None, simulation_history=[dict(RECORD)],
        )
        person = MagicMock()
        person.social_cognition = None
        handle_user_input(person, None, None, False, "hi")
        self.assertEqual(chat.call_args.kwargs["recent_actions"], ["Walk to Coupa Cafe"])


if __name__ == "__main__":
    unittest.main()
