import json
import time
import pytest
from unittest.mock import MagicMock

from core.insights.insight_system import InsightSystem


def _make_mock_llm(response_content: str = ""):
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content=response_content)
    return mock


class TestInsightSystem:
    def test_initialization(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        assert system.insights_delivered == 0
        assert system.max_per_session == 3

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

    def test_respects_max_per_session(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        system.insights_delivered = 3
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
        assert system.insights_delivered == 1
        llm.invoke.assert_called_once()

    def test_generate_insight_increments_counter(self):
        llm = _make_mock_llm("An observation.")
        system = InsightSystem(llm)
        system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert system.insights_delivered == 1
        system.generate_insight(
            dossier={}, recent_messages=[], emotional_state={}, self_narrative="",
        )
        assert system.insights_delivered == 2

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
        system.insights_delivered = 2

        data = system.to_dict()
        restored = InsightSystem.from_dict(data, llm)
        assert restored.insights_delivered == 0  # session counter resets on deserialize
        assert restored.max_per_session == 3

    def test_reset_session(self):
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        system.insights_delivered = 3
        system.reset_session()
        assert system.insights_delivered == 0

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
    def test_should_generate_insight_always_insight_env(self, monkeypatch):
        monkeypatch.setenv("JENBINA_ALWAYS_INSIGHT", "1")
        llm = _make_mock_llm()
        system = InsightSystem(llm)
        system.insights_delivered = 100  # over limit, but env var overrides
        assert system.should_generate_insight(message_count=0) is True

    def test_from_dict_defaults(self):
        llm = _make_mock_llm()
        restored = InsightSystem.from_dict({}, llm)
        assert restored.max_per_session == 3
        assert restored.min_messages == 2
