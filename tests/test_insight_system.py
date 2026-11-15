import json
import time
import pytest
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from core.insights.insight_system import InsightSystem


def _make_mock_llm(response_content: str = ""):
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content=response_content)
    return mock


class TestPerPersonInsights(unittest.TestCase):
    def _state_for_rebuild(self):
        system = InsightSystem(_make_mock_llm("You hide it well."), max_per_day=3, min_messages=4)
        day = date(2026, 11, 15)
        system.generate_first_impression({"job": "x"}, "hi", person_key="Ann")
        for _ in range(3):
            system.generate_insight({}, [], {}, "", person_key="Ann", today=day)
        system.generate_insight({}, [], {}, "", person_key="Bob", today=day)
        system.legacy_first_impression_delivered = True
        return system, day

    def _assert_rebuilt_state(self, rebuilt, system, llm, day):
        self.assertIs(rebuilt.llm, llm)
        self.assertEqual(rebuilt.to_dict(), system.to_dict())
        self.assertFalse(rebuilt.should_generate_first_impression({"x": 1}, person_key="Ann"))
        self.assertTrue(rebuilt.should_generate_first_impression({"x": 1}, person_key="Bob"))
        self.assertFalse(rebuilt.should_generate_insight(5, person_key="Ann", today=day))
        self.assertTrue(rebuilt.should_generate_insight(5, person_key="Bob", today=day))

    def test_rebuilding_on_another_llm_keeps_every_persons_state(self):
        system, day = self._state_for_rebuild()
        other_llm = _make_mock_llm()
        rebuilt = InsightSystem.from_dict(system.to_dict(), other_llm)
        self._assert_rebuilt_state(rebuilt, system, other_llm, day)

    def test_session_load_rebuilds_insights_without_losing_any_persons_state(self):
        from core.person.person import Person
        from core.ui.shared_init import _load_or_create_person

        system, day = self._state_for_rebuild()
        person = Person()
        person.insight_system = system
        user_db = MagicMock()
        user_db.load_person_state.return_value = person.serialize()
        other_llm = _make_mock_llm()
        with patch("core.ui.shared_init.init_llm", return_value=(_make_mock_llm(), _make_mock_llm())), \
                patch("core.ui.shared_init.get_llm", return_value=other_llm):
            restored = _load_or_create_person(user_db, 7)
        user_db.load_person_state.assert_called_once_with(7)
        self._assert_rebuilt_state(restored.insight_system, system, other_llm, day)

    def test_session_load_initializes_insights_when_none_were_saved(self):
        from core.person.person import Person
        from core.ui.shared_init import _load_or_create_person

        user_db = MagicMock()
        user_db.load_person_state.return_value = Person().serialize()
        other_llm = _make_mock_llm()
        with patch("core.ui.shared_init.init_llm", return_value=(_make_mock_llm(), _make_mock_llm())), \
                patch("core.ui.shared_init.get_llm", return_value=other_llm):
            restored = _load_or_create_person(user_db, 7)
        self.assertIs(restored.insight_system.llm, other_llm)
        self.assertEqual(restored.insight_system.people, {})

    def test_first_impression_and_daily_limit_are_per_person(self):
        llm = _make_mock_llm("You hide it well.")
        system = InsightSystem(llm)
        self.assertFalse(system.should_generate_first_impression({}))
        system.generate_first_impression({"job": "x"}, "hi", person_key="Ann")
        self.assertFalse(system.should_generate_first_impression({"job": "x"}, person_key="Ann"))
        self.assertTrue(system.should_generate_first_impression({"job": "x"}, person_key="Bob"))
        day = date(2026, 11, 15)
        for _ in range(3):
            self.assertIsNotNone(system.generate_insight({}, [], {}, "", person_key="Ann", today=day))
        self.assertFalse(system.should_generate_insight(5, person_key="Ann", today=day))
        self.assertTrue(system.should_generate_insight(5, person_key="Bob", today=day))
        self.assertTrue(system.should_generate_insight(5, person_key="Ann", today=day + timedelta(days=1)))
        restored = InsightSystem.from_dict(system.to_dict(), llm=None)
        self.assertFalse(restored.should_generate_first_impression({"job": "x"}, person_key="Ann"))
        self.assertFalse(restored.should_generate_insight(5, person_key="Ann", today=day))
        self.assertTrue(restored.should_generate_insight(5, person_key="Bob", today=day))

    def test_daily_count_resets_on_generation_and_refuses_a_fourth_call(self):
        llm = _make_mock_llm("An observation.")
        system = InsightSystem(llm)
        day = date(2026, 11, 15)
        for _ in range(3):
            system.generate_insight({}, [], {}, "", person_key="Ann", today=day)
        self.assertIsNone(system.generate_insight({}, [], {}, "", person_key="Ann", today=day))
        self.assertEqual(llm.invoke.call_count, 3)
        system.generate_insight({}, [], {}, "", person_key="Ann", today=day + timedelta(days=1))
        self.assertEqual(system.people["Ann"]["count"], 1)
        self.assertEqual(system.people["Ann"]["day"], "2026-11-16")
        self.assertEqual(llm.invoke.call_count, 4)

    def test_legacy_first_impression_is_retained_without_marking_any_person(self):
        system = InsightSystem.from_dict({"first_impression_delivered": True}, llm=None)
        self.assertTrue(system.legacy_first_impression_delivered)
        self.assertTrue(InsightSystem.from_dict(system.to_dict(), llm=None).legacy_first_impression_delivered)
        self.assertEqual(system.people, {})
        for name in ("User", "Ann", "Bob"):
            self.assertTrue(system.should_generate_first_impression({"job": "x"}, person_key=name))

    def test_failed_first_impression_does_not_mark_the_person(self):
        llm = _make_mock_llm("")
        system = InsightSystem(llm)
        self.assertIsNone(system.generate_first_impression({"job": "x"}, "hi", person_key="Ann"))
        self.assertTrue(system.should_generate_first_impression({"job": "x"}, person_key="Ann"))
        llm.invoke.side_effect = RuntimeError("unavailable")
        self.assertIsNone(system.generate_first_impression({"job": "x"}, "hi", person_key="Ann"))
        self.assertTrue(system.should_generate_first_impression({"job": "x"}, person_key="Ann"))

    def _chat_with_bob(self, first_impression):
        from core.person.person import Person
        from core.interaction.chat_handler import handle_chat_interaction

        person = Person()
        person.init_social_cognition()
        person.social_cognition.get_or_create_model("Bob").user_dossier = {"job": "baker"}
        person.receive_message("Bob", "Hello")
        person.send_message("Bob", "Hi")
        person.insight_system = MagicMock()
        person.insight_system.should_generate_first_impression.return_value = first_impression
        person.insight_system.generate_first_impression.return_value = "A first impression."
        person.insight_system.should_generate_insight.return_value = True
        person.insight_system.generate_insight.return_value = "An observation."
        result = handle_chat_interaction(
            st=MagicMock(), llm=_make_mock_llm("Hello Bob."),
            needs_response={}, world_description="{}", action_decision={},
            user_input="How are you?", person_state={}, person=person,
            conversation_partner_name="Bob",
        )
        self.assertEqual(result["assistant_response"], "Hello Bob.")
        return person.insight_system

    def test_chat_passes_the_person_key_to_first_impression_calls(self):
        system = self._chat_with_bob(first_impression=True)
        system.should_generate_first_impression.assert_called_once_with({"job": "baker"}, person_key="Bob")
        self.assertEqual(system.generate_first_impression.call_args.kwargs["person_key"], "Bob")

    def test_chat_passes_the_person_key_to_subtle_insight_calls(self):
        system = self._chat_with_bob(first_impression=False)
        system.should_generate_insight.assert_called_once_with(2, person_key="Bob")
        self.assertEqual(system.generate_insight.call_args.kwargs["person_key"], "Bob")


class TestInsightSystem(unittest.TestCase):
    def test_initialization(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        assert system.people == {}
        assert system.max_per_day == 3

    def test_should_not_trigger_before_min_messages(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        # Only 1 message exchanged
        assert system.should_generate_insight(message_count=1) is False

    def test_should_trigger_at_min_messages(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        # 2 messages exchanged — minimum threshold
        assert system.should_generate_insight(message_count=2) is True

    def test_should_trigger_at_3_messages(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        assert system.should_generate_insight(message_count=3) is True

    def test_respects_max_per_day(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        system.people["User"] = {"day": date.today().isoformat(), "count": 3, "first_impression_delivered": False}
        assert system.should_generate_insight(message_count=5) is False

    def test_generate_insight(self):
        response = "You seem like someone who measures their worth by how much they produce."
        llm = _make_mock_llm(response)
        system = InsightSystem(llm)

        dossier = {"personality_traits": ["driven", "analytical"]}
        conversation = [
            {"sender": "user", "content": "I spent the whole weekend refactoring my side project"},
            {"sender": "person", "content": "That sounds intense! What were you refactoring?"},
            {"sender": "user", "content": "Just making the architecture cleaner. I can't stand messy code."},
        ]
        emotions = {"joy": 35, "curiosity": 60}
        self_narrative = "I am someone who values genuine connection."

        insight = system.generate_insight(
            dossier=dossier,
            recent_messages=conversation,
            emotional_state=emotions,
            self_narrative=self_narrative,
        )
        assert insight is not None
        assert len(insight) > 0
        assert system.people["User"]["count"] == 1
        llm.invoke.assert_called_once()

    def test_generate_insight_increments_counter(self):
        llm = _make_mock_llm("An observation.")
        system = InsightSystem(llm)
        system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert system.people["User"]["count"] == 1
        system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert system.people["User"]["count"] == 2

    def test_generate_insight_returns_none_on_empty_response(self):
        llm = _make_mock_llm("")
        system = InsightSystem(llm)
        insight = system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert insight is None

    def test_serialization_roundtrip(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        system.people["User"] = {"day": date.today().isoformat(), "count": 2, "first_impression_delivered": True}

        data = system.to_dict()
        restored = InsightSystem.from_dict(data, llm)
        assert restored.people == system.people
        assert restored.max_per_day == 3

    def test_next_day_has_a_fresh_quota(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        day = date(2026, 11, 15)
        system.people["User"] = {"day": day.isoformat(), "count": 3, "first_impression_delivered": True}
        assert not system.should_generate_insight(5, today=day)
        assert system.should_generate_insight(5, today=day + timedelta(days=1))

    # ------------------------------------------------------------------
    # generate_insight LLM failure path
    # ------------------------------------------------------------------
    def test_generate_insight_llm_failure_returns_none(self):
        llm = _make_mock_llm()
        llm.invoke.side_effect = Exception("LLM error")
        system = InsightSystem(llm)
        insight = system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert insight is None

    # ------------------------------------------------------------------
    # JENBINA_ALWAYS_INSIGHT env var (line 125-126)
    # ------------------------------------------------------------------
    @patch.dict("os.environ", {"JENBINA_ALWAYS_INSIGHT": "1"})
    def test_always_insight_env_bypasses_minimum_but_keeps_daily_cap(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        assert system.should_generate_insight(message_count=0) is True
        system.people["User"] = {"day": date.today().isoformat(), "count": 3, "first_impression_delivered": False}
        assert system.should_generate_insight(message_count=0) is False

    def test_from_dict_defaults(self):
        llm = _make_mock_llm()
        restored = InsightSystem.from_dict({}, llm)
        assert restored.max_per_day == 3
        assert restored.min_messages == 2
