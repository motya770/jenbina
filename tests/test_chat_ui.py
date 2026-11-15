#!/usr/bin/env python3
"""Tests for the chat flow helpers in core.ui.chat: outreach message types,
inline input handling and the mood event recorded after a chat."""

import os
import sys
import json
import unittest
from contextlib import nullcontext
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.heartbeat.host import ChatTurn
from core.person.person import Person
from core.timeline import EventLog
from core.ui import chat as chat_ui
from core.ui.chat import handle_user_input
from tests.test_greeting_generation import _FakeSessionState


class TestOutreachTypes(unittest.TestCase):
    @patch("core.ui.chat.check_return_greeting", return_value="You're back!")
    @patch("core.ui.chat.st")
    def test_greeting_is_stored_with_greeting_type_under_the_persons_key(self, st, check):
        st.session_state = _FakeSessionState()
        host = MagicMock()
        user = {"id": 2, "display_name": "Bob"}
        turn = ChatTurn("Bob (2)", 2, False, {}, [], MagicMock())
        host.greeting_turn.return_value = nullcontext(turn)
        llm = MagicMock()
        chat_ui.ensure_greeting(host, user, llm)
        host.greeting_turn.assert_called_once_with(user)
        check.assert_called_once_with(host.person, llm, "Bob (2)")
        host.person.send_message.assert_called_once_with("Bob (2)", "You're back!", "greeting")

    @patch("core.ui.chat.check_return_greeting")
    @patch("core.ui.chat.st")
    def test_greeting_waits_when_the_mind_is_busy(self, st, check):
        st.session_state = _FakeSessionState()
        host = MagicMock()
        user = {"id": 2, "display_name": "Bob"}
        host.greeting_turn.return_value = nullcontext(None)
        chat_ui.ensure_greeting(host, user, None)
        check.assert_not_called()
        host.person.send_message.assert_not_called()
        self.assertNotIn("showed_return_greeting", st.session_state)

        # A later refresh retries and delivers the greeting under the lock.
        turn = ChatTurn("Bob", 2, False, {}, [], MagicMock())
        host.greeting_turn.return_value = nullcontext(turn)
        check.return_value = "Hello Bob"
        chat_ui.ensure_greeting(host, user, None)
        self.assertEqual(host.greeting_turn.call_count, 2)
        host.person.send_message.assert_called_once_with("Bob", "Hello Bob", "greeting")

    @patch("core.ui.chat.st")
    def test_a_greeting_is_not_repeated_in_the_session(self, st):
        st.session_state = _FakeSessionState()
        person = Person()
        person.init_social_cognition()
        host = MagicMock(person=person)
        host.greeting_turn.return_value = nullcontext(ChatTurn("Bob", 2, False, {}, [], MagicMock()))
        llm = MagicMock()
        llm.invoke.return_value.content = "Hello Bob"
        chat_ui.ensure_greeting(host, {"id": 2, "display_name": "Bob"}, llm)
        self.assertTrue(st.session_state.showed_return_greeting)
        self.assertEqual(person.conversations["Bob"].messages[0].message_type, "greeting")
        host.greeting_turn.reset_mock()
        chat_ui.ensure_greeting(host, {"id": 2, "display_name": "Bob"}, llm)
        host.greeting_turn.assert_not_called()
        self.assertEqual(len(person.conversations["Bob"].messages), 1)

    @patch("core.ui.chat.st")
    def test_no_greeting_is_stored_for_a_recent_visit(self, st):
        st.session_state = _FakeSessionState()
        person = Person()
        person.init_social_cognition()
        person.social_cognition.get_or_create_model("Bob").last_visit_time = datetime.now() - timedelta(minutes=10)
        host = MagicMock(person=person)
        host.greeting_turn.return_value = nullcontext(ChatTurn("Bob", 2, False, {}, [], MagicMock()))
        llm = MagicMock()
        chat_ui.ensure_greeting(host, {"id": 2, "display_name": "Bob"}, llm)
        self.assertNotIn("Bob", person.conversations)
        llm.invoke.assert_not_called()
        # Considered once: the 5-second refreshes must not take the mind lock again.
        self.assertTrue(st.session_state.showed_return_greeting)
        host.greeting_turn.reset_mock()
        chat_ui.ensure_greeting(host, {"id": 2, "display_name": "Bob"}, llm)
        host.greeting_turn.assert_not_called()



class TestHandleUserInput(unittest.TestCase):
    @patch("core.ui.chat.analyze_emotion_impact", return_value=None)
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hi", "user_message": "hello"})
    @patch("core.ui.chat.st")
    def test_a_message_counts_as_a_visit(self, st, *_):
        st.session_state = _FakeSessionState(action_history=[])
        person = Person()
        person.init_social_cognition()
        turn = ChatTurn("Bob", 2, False, {}, [], EventLog())
        before = datetime.now()
        handle_user_input(person, None, None, False, "hello", turn)
        self.assertGreaterEqual(person.social_cognition.models["Bob"].last_visit_time, before)

    @patch("core.ui.chat.st")
    def test_empty_input_returns_none_without_chat_input(self, st):
        turn = ChatTurn("Bob", 2, False, {}, [], EventLog())
        self.assertIsNone(handle_user_input(MagicMock(), None, None, False, "", turn))
        st.chat_input.assert_not_called()

    @patch("core.ui.chat.analyze_emotion_impact", return_value={"joy": 6})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey", "user_message": "hi", "insight": "x"})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat.st")
    def test_chat_mood_event_goes_to_the_shared_log_without_names(self, st, *_):
        log = EventLog()
        stale_log = EventLog()
        st.session_state = _FakeSessionState(
            event_log=stale_log, action_history=[],
        )
        turn = ChatTurn("Bob", 2, False, {}, [], log)
        snaps = iter([{"joy": 30}, {"joy": 36}])
        person = MagicMock()
        person.get_emotions_snapshot.side_effect = lambda: next(snaps)
        person.social_cognition = None
        result = handle_user_input(person, None, None, False, "BOB-MESSAGE-TEXT", turn)
        self.assertEqual(result["assistant_response"], "hey")
        self.assertEqual([e.kind for e in log.recent()], ["mood"])
        self.assertEqual(log.recent()[0].detail["source"], "chat")
        event = log.recent()[0]
        for private in ("Bob", "BOB-MESSAGE-TEXT", "hey"):
            self.assertNotIn(private, event.title)
            self.assertNotIn(private, json.dumps(event.detail))
        self.assertEqual(stale_log.recent(), [])
        st.chat_message.assert_not_called()

    @patch("core.ui.chat.analyze_emotion_impact", return_value={})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey", "user_message": "hi"})
    @patch("core.ui.chat.st")
    def test_chat_passes_only_the_partners_state_and_the_last_beat(self, st, chat, _emotion):
        db = MagicMock()
        db.get_messages.return_value = [{"sender": "Bob", "content": "hi"}]
        st.session_state = _FakeSessionState(
            current_user={"id": 99, "display_name": "Bob"}, user_db=db, action_history=[],
            needs_response="STALE NEEDS", world_description="STALE WORLD",
            action_decision="STALE ACTION", state_response="STALE STATE",
            simulation_history=[{"action_decision": {"chosen_action": "STALE HISTORY"}}],
        )
        person = Person()
        person.init_social_cognition()
        person.social_cognition.get_or_create_model("Ann").beliefs.append("ANN-BELIEF")
        person.social_cognition.get_or_create_model("Bob (2)").beliefs.append("BOB-BELIEF")
        responses = {
            "needs_response": {"hunger": 70}, "world_description": "HOST WORLD",
            "action_decision": {"chosen_action": "Read"}, "state_response": "HOST STATE",
        }
        turn = ChatTurn("Bob (2)", 2, False, responses, [dict(RECORD)], EventLog())
        memory = MagicMock()
        handle_user_input(person, None, memory, False, "hi", turn)
        kwargs = chat.call_args.kwargs
        self.assertEqual((kwargs["conversation_partner_name"], kwargs["user_id"]), ("Bob (2)", 2))
        for key, value in responses.items():
            self.assertEqual(kwargs[key], value)
        self.assertEqual(kwargs["recent_actions"], ["Walk to Coupa Cafe"])
        self.assertEqual(kwargs["conversation_context"], "Bob: hi")
        self.assertIs(kwargs["memory_manager"], memory)
        state = json.dumps(kwargs["person_state"], default=str)
        self.assertNotIn("ANN-BELIEF", state)
        self.assertIn("BOB-BELIEF", state)
        self.assertEqual([msg.content for msg in person.conversations["Bob (2)"].messages], ["hi", "hey"])
        self.assertNotIn("Bob", person.conversations)
        db.get_messages.assert_called_once_with(2, limit=200)
        self.assertEqual(db.store_message.call_args_list[0].args, (2, "Bob", "hi", "user_message"))
        self.assertEqual(db.store_message.call_args_list[1].args, (2, "Jenbina", "hey", "jenbina_response"))

    @patch("core.ui.chat.analyze_emotion_impact", return_value={})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey"})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat.st")
    def test_chat_before_the_first_beat_uses_empty_context(self, st, _db, chat, _emotion):
        st.session_state = _FakeSessionState(action_history=[])
        person = Person()
        person.init_social_cognition()
        handle_user_input(person, None, None, False, "hi", ChatTurn("Bob", 2, False, {}, [], EventLog()))
        for key in ("needs_response", "world_description", "action_decision", "state_response"):
            self.assertIsNone(chat.call_args.kwargs[key])
        self.assertEqual(chat.call_args.kwargs["recent_actions"], [])





RECORD = {
    "action_decision": {"chosen_action": "Walk to Coupa Cafe"},
    "world_summary": {
        "location": {"name": "Jenbina's House"},
        "time": {"time_of_day": "evening"},
        "weather": {"description": "Clear skies"},
    },
}


class TestHistoryShapedContext(unittest.TestCase):

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
        turn = ChatTurn("Matt", 1, False, {}, [dict(RECORD)], EventLog())
        handle_user_input(person, None, None, False, "hi", turn)
        self.assertEqual(chat.call_args.kwargs["recent_actions"], ["Walk to Coupa Cafe"])


if __name__ == "__main__":
    unittest.main()
