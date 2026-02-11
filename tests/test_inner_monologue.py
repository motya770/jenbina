"""Tests for the inner monologue / stream-of-consciousness system."""
import pytest
import time
from unittest.mock import MagicMock, patch

from core.cognition.inner_monologue import (
    InnerMonologueSystem,
    InnerThought,
    ThoughtMode,
    DELIBERATION_NEED_THRESHOLD,
    RUMINATION_EMOTION_THRESHOLD,
    WORRY_TREND_THRESHOLD,
    BOREDOM_SATISFACTION_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_llm(thought_text="I wonder what I should do...",
                  tone="thoughtful", intensity=0.5):
    """Create a mock LLM that returns a canned JSON response."""
    import json
    mock_llm = MagicMock()
    response = MagicMock()
    response.content = json.dumps({
        "thought": thought_text,
        "emotional_tone": tone,
        "intensity": intensity,
    })
    mock_llm.invoke.return_value = response
    return mock_llm


def make_needs(**overrides):
    """Create a needs dict with sensible defaults."""
    defaults = {
        "hunger": 80.0,
        "sleep": 85.0,
        "security": 75.0,
        "friendship": 60.0,
        "self_esteem": 55.0,
    }
    defaults.update(overrides)
    return defaults


def make_emotions(**overrides):
    defaults = {"joy": 40.0, "sadness": 15.0, "fear": 10.0, "anger": 5.0,
                "trust": 50.0, "anticipation": 30.0}
    defaults.update(overrides)
    return defaults


# ===========================================================================
# InnerThought data structure tests
# ===========================================================================

class TestInnerThought:
    def test_initialization(self):
        t = InnerThought(
            content="thinking...",
            mode="deliberation",
            trigger="unmet needs",
            emotional_tone="restless",
            intensity=0.7,
        )
        assert t.content == "thinking..."
        assert t.mode == "deliberation"
        assert t.intensity == 0.7
        assert t.timestamp > 0

    def test_to_dict(self):
        t = InnerThought(
            content="hmm",
            mode="worry",
            trigger="trends",
            emotional_tone="anxious",
            intensity=0.6,
        )
        d = t.to_dict()
        assert d["content"] == "hmm"
        assert d["mode"] == "worry"
        assert d["emotional_tone"] == "anxious"
        assert d["intensity"] == 0.6

    def test_roundtrip(self):
        t = InnerThought(
            content="test",
            mode="daydreaming",
            trigger="idle",
            emotional_tone="dreamy",
            intensity=0.3,
            timestamp=12345.0,
        )
        d = t.to_dict()
        t2 = InnerThought.from_dict(d)
        assert t2.content == t.content
        assert t2.mode == t.mode
        assert t2.timestamp == t.timestamp


# ===========================================================================
# ThoughtMode enum tests
# ===========================================================================

class TestThoughtMode:
    def test_values(self):
        assert ThoughtMode.DELIBERATION.value == "deliberation"
        assert ThoughtMode.RUMINATION.value == "rumination"
        assert ThoughtMode.WORRY.value == "worry"
        assert ThoughtMode.DAYDREAMING.value == "daydreaming"

    def test_string_enum(self):
        assert str(ThoughtMode.DELIBERATION) == "ThoughtMode.DELIBERATION"
        assert ThoughtMode("deliberation") == ThoughtMode.DELIBERATION


# ===========================================================================
# Mode selection tests
# ===========================================================================

class TestModeSelection:
    def test_deliberation_when_need_critical(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(hunger=20.0),  # below threshold
            emotions=make_emotions(),
        )
        assert mode == ThoughtMode.DELIBERATION

    def test_deliberation_when_multiple_needs_low(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(hunger=30.0, sleep=25.0),
            emotions=make_emotions(),
        )
        assert mode == ThoughtMode.DELIBERATION

    def test_rumination_when_negative_emotions_high(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(),  # all above threshold
            emotions=make_emotions(sadness=60.0),  # above rumination threshold
            recent_experiences=[{"action": "failed_task"}],
        )
        assert mode == ThoughtMode.RUMINATION

    def test_rumination_needs_experiences(self):
        """High negative emotions without experiences should NOT trigger rumination."""
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(),
            emotions=make_emotions(sadness=60.0),
            recent_experiences=None,  # no experiences to replay
        )
        # Should fall through to daydreaming (or worry if trends bad)
        assert mode != ThoughtMode.RUMINATION

    def test_worry_when_needs_trending_down(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(),
            emotions=make_emotions(),
            needs_trends={"hunger": -8.0, "sleep": -6.0, "security": -4.0},
        )
        assert mode == ThoughtMode.WORRY

    def test_worry_with_multiple_declining(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(),
            emotions=make_emotions(),
            needs_trends={"hunger": -2.0, "sleep": -1.0, "security": -3.0},
        )
        assert mode == ThoughtMode.WORRY

    def test_daydreaming_when_all_fine(self):
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(),  # all above 50
            emotions=make_emotions(),  # no strong negatives
        )
        assert mode == ThoughtMode.DAYDREAMING

    def test_deliberation_takes_priority_over_rumination(self):
        """Even with high negative emotions, critical needs override to deliberation."""
        system = InnerMonologueSystem(make_mock_llm())
        mode = system.select_mode(
            needs=make_needs(hunger=10.0),  # critically low
            emotions=make_emotions(sadness=80.0),  # high negative
            recent_experiences=[{"action": "something"}],
        )
        assert mode == ThoughtMode.DELIBERATION


# ===========================================================================
# Thought generation tests
# ===========================================================================

class TestThoughtGeneration:
    def test_generates_thought_with_llm(self):
        llm = make_mock_llm("Maybe I should eat something...", "restless", 0.7)
        system = InnerMonologueSystem(llm)

        thought = system.generate_thought(
            mode=ThoughtMode.DELIBERATION,
            working_memory="hunger is low",
            needs_summary="hunger: 20%",
            emotional_state="restless",
        )

        assert thought.content == "Maybe I should eat something..."
        assert thought.mode == "deliberation"
        assert thought.emotional_tone == "restless"
        assert thought.intensity == 0.7
        llm.invoke.assert_called_once()

    def test_fallback_on_llm_error(self):
        llm = MagicMock()
        llm.invoke.side_effect = Exception("LLM unavailable")
        system = InnerMonologueSystem(llm)

        thought = system.generate_thought(
            mode=ThoughtMode.WORRY,
            working_memory="",
            needs_summary="",
            emotional_state="",
        )

        assert "wrong" in thought.content.lower() or "thinking" in thought.content.lower()
        assert thought.mode == "worry"
        assert thought.emotional_tone == "neutral"
        assert thought.intensity == 0.3

    def test_intensity_clamped(self):
        llm = make_mock_llm("test", "calm", 1.5)  # intensity > 1.0
        system = InnerMonologueSystem(llm)

        thought = system.generate_thought(
            mode=ThoughtMode.DAYDREAMING,
            working_memory="",
            needs_summary="",
            emotional_state="",
        )
        assert thought.intensity <= 1.0

    def test_thought_recorded_in_history(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        system.generate_thought(
            mode=ThoughtMode.DELIBERATION,
            working_memory="",
            needs_summary="",
            emotional_state="",
        )

        assert len(system.thought_history) == 1
        assert system.current_thought is not None

    def test_history_capped(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)
        system.MAX_THOUGHT_HISTORY = 5

        for _ in range(10):
            system.generate_thought(
                mode=ThoughtMode.DAYDREAMING,
                working_memory="",
                needs_summary="",
                emotional_state="",
            )

        assert len(system.thought_history) == 5


# ===========================================================================
# Full think() cycle tests
# ===========================================================================

class TestThinkCycle:
    def test_think_returns_thought(self):
        llm = make_mock_llm("Hmm, I'm getting hungry...", "uneasy", 0.6)
        system = InnerMonologueSystem(llm)

        thought = system.think(
            needs=make_needs(hunger=30.0),
            emotions=make_emotions(),
            working_memory_str="hunger is low",
            needs_summary_str="hunger: 30%",
            emotional_state_str="slightly anxious",
        )

        assert isinstance(thought, InnerThought)
        assert thought.content == "Hmm, I'm getting hungry..."

    def test_think_tracks_needs_snapshots(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        system.think(
            needs=make_needs(hunger=80.0),
            emotions=make_emotions(),
            working_memory_str="",
            needs_summary_str="",
            emotional_state_str="",
        )
        system.think(
            needs=make_needs(hunger=60.0),
            emotions=make_emotions(),
            working_memory_str="",
            needs_summary_str="",
            emotional_state_str="",
        )

        assert len(system._needs_snapshots) == 2

    def test_think_computes_trends(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        # First call — no trend data yet
        system.think(
            needs=make_needs(hunger=80.0),
            emotions=make_emotions(),
            working_memory_str="",
            needs_summary_str="",
            emotional_state_str="",
        )

        # Second call — trend should be computed
        system.think(
            needs=make_needs(hunger=60.0),
            emotions=make_emotions(),
            working_memory_str="",
            needs_summary_str="",
            emotional_state_str="",
        )

        # Should have recorded 2 snapshots
        assert len(system._needs_snapshots) == 2


# ===========================================================================
# Mode variation tests
# ===========================================================================

class TestModeVariation:
    def test_no_variation_below_threshold(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        # Only 1 consecutive, should never vary
        system._consecutive_mode_counts = {"deliberation": 1}
        result = system._maybe_vary_mode(ThoughtMode.DELIBERATION)
        assert result == ThoughtMode.DELIBERATION

    def test_variation_possible_after_many_consecutive(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        system._consecutive_mode_counts = {"deliberation": 5}
        # Run many times — at least once should vary (probabilistic but very likely)
        results = set()
        for _ in range(50):
            results.add(system._maybe_vary_mode(ThoughtMode.DELIBERATION))

        # With 30% chance over 50 runs, we almost certainly get at least one alternative
        assert len(results) > 1


# ===========================================================================
# Formatting tests
# ===========================================================================

class TestFormatting:
    def test_format_no_thought(self):
        system = InnerMonologueSystem(make_mock_llm())
        assert system.format_for_prompt() == "No inner thoughts at the moment."

    def test_format_with_thought(self):
        system = InnerMonologueSystem(make_mock_llm())
        system.current_thought = InnerThought(
            content="Should I eat?",
            mode="deliberation",
            trigger="hunger",
            emotional_tone="restless",
            intensity=0.6,
        )
        result = system.format_for_prompt()
        assert "deliberation" in result
        assert "Should I eat?" in result
        assert "restless" in result

    def test_format_recent_thoughts_empty(self):
        system = InnerMonologueSystem(make_mock_llm())
        assert system.format_recent_thoughts() == "No recent thoughts."

    def test_format_recent_thoughts(self):
        system = InnerMonologueSystem(make_mock_llm())
        for mode_str in ["deliberation", "rumination", "daydreaming"]:
            system.thought_history.append(InnerThought(
                content=f"thought in {mode_str}",
                mode=mode_str,
                trigger="test",
                emotional_tone="neutral",
                intensity=0.5,
            ))

        result = system.format_recent_thoughts(count=2)
        assert "rumination" in result
        assert "daydreaming" in result
        # Only last 2, not deliberation
        lines = result.strip().split("\n")
        assert len(lines) == 2


# ===========================================================================
# Stats tests
# ===========================================================================

class TestStats:
    def test_empty_stats(self):
        system = InnerMonologueSystem(make_mock_llm())
        stats = system.get_stats()
        assert stats["total_thoughts"] == 0
        assert stats["current_mode"] is None
        assert stats["current_thought"] is None

    def test_stats_after_thought(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)
        system.generate_thought(
            mode=ThoughtMode.DAYDREAMING,
            working_memory="",
            needs_summary="",
            emotional_state="",
        )
        stats = system.get_stats()
        assert stats["total_thoughts"] == 1
        assert stats["current_mode"] == "daydreaming"
        assert stats["mode_distribution"]["daydreaming"] == 1


# ===========================================================================
# Serialization tests
# ===========================================================================

class TestSerialization:
    def test_empty_roundtrip(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)
        d = system.to_dict()
        system2 = InnerMonologueSystem.from_dict(d, llm)
        assert system2.thought_history == []
        assert system2.current_thought is None

    def test_roundtrip_with_state(self):
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)
        system.generate_thought(
            mode=ThoughtMode.RUMINATION,
            working_memory="past event replay",
            needs_summary="all ok",
            emotional_state="melancholic",
        )
        system._needs_snapshots = [{"hunger": 80.0}, {"hunger": 70.0}]

        d = system.to_dict()
        system2 = InnerMonologueSystem.from_dict(d, llm)

        assert len(system2.thought_history) == 1
        assert system2.current_thought is not None
        assert system2.current_thought.mode == "rumination"
        assert system2._last_mode == "rumination"
        assert len(system2._needs_snapshots) == 2


# ===========================================================================
# Needs trend computation tests
# ===========================================================================

class TestNeedsTrends:
    def test_no_trend_with_single_snapshot(self):
        system = InnerMonologueSystem(make_mock_llm())
        system._needs_snapshots = [{"hunger": 80.0}]
        trends = system._compute_needs_trends({"hunger": 70.0})
        assert trends == {}

    def test_trend_computed_from_two_snapshots(self):
        system = InnerMonologueSystem(make_mock_llm())
        system._needs_snapshots = [
            {"hunger": 80.0, "sleep": 90.0},
            {"hunger": 70.0, "sleep": 85.0},
        ]
        trends = system._compute_needs_trends({"hunger": 60.0, "sleep": 80.0})
        # Compares current (60, 80) against second-to-last snapshot (80, 90)
        assert trends["hunger"] == pytest.approx(-20.0)
        assert trends["sleep"] == pytest.approx(-10.0)


# ===========================================================================
# Integration test
# ===========================================================================

class TestIntegration:
    def test_multi_cycle_with_mode_shifts(self):
        """Simulate multiple cycles with changing state and verify mode shifts."""
        llm = make_mock_llm()
        system = InnerMonologueSystem(llm)

        # Cycle 1: Hungry — should deliberate
        t1 = system.think(
            needs=make_needs(hunger=20.0),
            emotions=make_emotions(),
            working_memory_str="hunger is critically low",
            needs_summary_str="hunger: 20%",
            emotional_state_str="uneasy",
        )
        assert t1.mode == "deliberation"

        # Cycle 2: Fed, but sad about past — should ruminate
        t2 = system.think(
            needs=make_needs(hunger=80.0),
            emotions=make_emotions(sadness=60.0),
            working_memory_str="thinking about earlier",
            needs_summary_str="hunger: 80%",
            emotional_state_str="sad",
            recent_experiences_list=[{"action": "failed_social_interaction"}],
        )
        assert t2.mode == "rumination"

        # Cycle 3: Everything fine — should daydream
        t3 = system.think(
            needs=make_needs(),
            emotions=make_emotions(),
            working_memory_str="mind is clear",
            needs_summary_str="all needs met",
            emotional_state_str="content",
        )
        assert t3.mode == "daydreaming"

        assert len(system.thought_history) == 3
        modes = [t.mode for t in system.thought_history]
        assert modes == ["deliberation", "rumination", "daydreaming"]
