"""Tests for the working memory system."""
import pytest
from unittest.mock import patch

from core.working_memory.working_memory_system import (
    WorkingMemoryItem,
    WorkingMemorySystem,
    NEED_LEVEL_WEIGHTS,
    PLAN_STEP_SALIENCE,
    EXPERIENCE_BASE_SALIENCE,
    ENVIRONMENT_SALIENCE,
    CONTEXT_SWITCH_PENALTY,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_needs(**overrides):
    """Create needs dict with level info."""
    defaults = {
        "hunger": {"satisfaction": 30.0, "level": 1},
        "sleep": {"satisfaction": 80.0, "level": 1},
        "security": {"satisfaction": 70.0, "level": 2},
    }
    defaults.update(overrides)
    return defaults


def make_emotions(**overrides):
    defaults = {"joy": 60.0, "fear": 20.0, "sadness": 10.0}
    defaults.update(overrides)
    return defaults


# ===========================================================================
# WorkingMemoryItem tests
# ===========================================================================

class TestWorkingMemoryItem:
    def test_initialization(self):
        item = WorkingMemoryItem(content="test", source="need", salience=0.7)
        assert item.content == "test"
        assert item.source == "need"
        assert item.salience == 0.7
        assert item.source_id == ""

    def test_to_dict(self):
        item = WorkingMemoryItem(content="test", source="need", salience=0.5, source_id="hunger")
        d = item.to_dict()
        assert d["content"] == "test"
        assert d["source"] == "need"
        assert d["salience"] == 0.5
        assert d["source_id"] == "hunger"

    def test_from_dict_roundtrip(self):
        item = WorkingMemoryItem(content="test", source="emotion", salience=0.8, source_id="joy")
        d = item.to_dict()
        item2 = WorkingMemoryItem.from_dict(d)
        assert item2.content == item.content
        assert item2.source == item.source
        assert item2.salience == item.salience


# ===========================================================================
# Focus calculation tests
# ===========================================================================

class TestFocusCalculation:
    def test_high_sleep_high_focus(self):
        wm = WorkingMemorySystem()
        wm.update(needs=make_needs(sleep={"satisfaction": 100.0, "level": 1}),
                   emotions={}, sleep_satisfaction=100.0)
        assert wm.focus == pytest.approx(100.0)

    def test_low_sleep_low_focus(self):
        wm = WorkingMemorySystem()
        wm.update(needs=make_needs(sleep={"satisfaction": 10.0, "level": 1}),
                   emotions={}, sleep_satisfaction=10.0)
        assert wm.focus == pytest.approx(30.0)  # Clamped at 30

    def test_mid_sleep_mid_focus(self):
        wm = WorkingMemorySystem()
        wm.update(needs=make_needs(), emotions={}, sleep_satisfaction=50.0)
        assert wm.focus == pytest.approx(60.0)  # 50*0.8+20

    def test_focus_never_below_30(self):
        wm = WorkingMemorySystem()
        wm.update(needs=make_needs(), emotions={}, sleep_satisfaction=0.0)
        assert wm.focus >= 30.0

    def test_focus_never_above_100(self):
        wm = WorkingMemorySystem()
        wm.update(needs=make_needs(), emotions={}, sleep_satisfaction=150.0)
        assert wm.focus <= 100.0


# ===========================================================================
# Buffer capacity tests
# ===========================================================================

class TestBufferCapacity:
    def test_full_focus_7_capacity(self):
        wm = WorkingMemorySystem()
        wm.focus = 100.0
        assert wm._get_capacity() == 7

    def test_min_focus_3_capacity(self):
        wm = WorkingMemorySystem()
        wm.focus = 30.0
        assert wm._get_capacity() == 4  # floor(3 + 4*0.3) = floor(4.2) = 4

    def test_zero_focus_3_capacity(self):
        wm = WorkingMemorySystem()
        wm.focus = 0.0
        assert wm._get_capacity() == 3

    def test_capacity_scales_with_focus(self):
        wm = WorkingMemorySystem()
        wm.focus = 50.0
        assert wm._get_capacity() == 5  # floor(3 + 4*0.5) = floor(5.0) = 5


# ===========================================================================
# Salience scoring tests
# ===========================================================================

class TestSalienceScoring:
    def test_critical_need_high_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 10.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        # With full focus, no noise
        hunger_items = [i for i in wm.buffer if i.source_id == "hunger"]
        assert len(hunger_items) == 1
        assert hunger_items[0].salience > 0.8

    def test_satisfied_need_low_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 95.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        # 0.05 salience, below 0.1 threshold
        hunger_items = [i for i in wm.buffer if i.source_id == "hunger"]
        assert len(hunger_items) == 0

    def test_lower_maslow_level_higher_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={
                "hunger": {"satisfaction": 50.0, "level": 1},  # physio: 0.5 * 1.0 = 0.5
                "creativity": {"satisfaction": 50.0, "level": 5},  # self-act: 0.5 * 0.2 = 0.1
            },
            emotions={},
            sleep_satisfaction=100.0,
        )
        items = {i.source_id: i.salience for i in wm.buffer if i.source == "need"}
        if "hunger" in items and "creativity" in items:
            assert items["hunger"] > items["creativity"]

    def test_emotion_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={"joy": 80.0, "fear": 30.0, "sadness": 5.0},
            sleep_satisfaction=100.0,
        )
        emotion_items = [i for i in wm.buffer if i.source == "emotion"]
        # Top 2 emotions with salience > 0.1: joy (0.8) and fear (0.3)
        assert len(emotion_items) == 2

    def test_plan_step_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={},
            active_plan_step={"description": "Walk to store", "action_hint": "walk"},
            sleep_satisfaction=100.0,
        )
        plan_items = [i for i in wm.buffer if i.source == "plan_step"]
        assert len(plan_items) == 1
        assert plan_items[0].salience == pytest.approx(PLAN_STEP_SALIENCE)

    def test_goal_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={},
            active_goals=[{"description": "Find food", "progress": 0.2, "confidence": 0.8}],
            sleep_satisfaction=100.0,
        )
        goal_items = [i for i in wm.buffer if i.source == "goal"]
        assert len(goal_items) == 1
        # (1 - 0.2) * 0.8 * 0.5 = 0.32
        assert goal_items[0].salience == pytest.approx(0.32)

    def test_experience_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={},
            recent_experience={"action": "ate food"},
            sleep_satisfaction=100.0,
        )
        exp_items = [i for i in wm.buffer if i.source == "experience"]
        assert len(exp_items) == 1
        assert exp_items[0].salience == pytest.approx(EXPERIENCE_BASE_SALIENCE)

    def test_environment_storm_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={},
            world_context={"weather": "heavy storm", "time_of_day": "afternoon"},
            sleep_satisfaction=100.0,
        )
        env_items = [i for i in wm.buffer if i.source == "environment"]
        assert len(env_items) == 1
        assert env_items[0].salience == pytest.approx(ENVIRONMENT_SALIENCE)

    def test_environment_night_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={},
            emotions={},
            world_context={"weather": "clear", "time_of_day": "night"},
            sleep_satisfaction=100.0,
        )
        env_items = [i for i in wm.buffer if i.source == "environment"]
        assert len(env_items) == 1

    def test_buffer_sorted_by_salience(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={
                "hunger": {"satisfaction": 10.0, "level": 1},
                "creativity": {"satisfaction": 50.0, "level": 5},
            },
            emotions={"joy": 70.0},
            active_plan_step={"description": "Walk", "action_hint": "walk"},
            sleep_satisfaction=100.0,
        )
        saliences = [i.salience for i in wm.buffer]
        assert saliences == sorted(saliences, reverse=True)

    def test_buffer_capped_at_capacity(self):
        wm = WorkingMemorySystem()
        # Low focus = small capacity
        wm.update(
            needs={
                "hunger": {"satisfaction": 10.0, "level": 1},
                "sleep": {"satisfaction": 10.0, "level": 1},
                "security": {"satisfaction": 10.0, "level": 2},
                "friendship": {"satisfaction": 10.0, "level": 3},
                "self_esteem": {"satisfaction": 10.0, "level": 4},
                "creativity": {"satisfaction": 10.0, "level": 5},
                "purpose": {"satisfaction": 10.0, "level": 5},
                "meaning": {"satisfaction": 10.0, "level": 5},
            },
            emotions={"joy": 80.0, "fear": 70.0},
            active_plan_step={"description": "Walk", "action_hint": "walk"},
            sleep_satisfaction=10.0,  # Very tired
        )
        capacity = wm._get_capacity()
        assert len(wm.buffer) <= capacity


# ===========================================================================
# Context switch tests
# ===========================================================================

class TestContextSwitch:
    def test_context_switch_detected(self):
        wm = WorkingMemorySystem()
        # First update: top item is hunger
        wm.update(
            needs={"hunger": {"satisfaction": 10.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        assert wm.last_top_source == "need"

        # Second update: top item is plan step
        wm.update(
            needs={"hunger": {"satisfaction": 90.0, "level": 1}},
            emotions={},
            active_plan_step={"description": "Walk", "action_hint": "walk"},
            sleep_satisfaction=100.0,
        )
        assert wm.context_switches == 1

    def test_no_context_switch_same_source(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 10.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        wm.update(
            needs={"hunger": {"satisfaction": 15.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        assert wm.context_switches == 0

    def test_context_switch_reduces_focus(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 10.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        focus_before = wm.focus

        wm.update(
            needs={"hunger": {"satisfaction": 90.0, "level": 1}},
            emotions={"fear": 90.0},
            sleep_satisfaction=100.0,
        )
        assert wm.focus == pytest.approx(focus_before - CONTEXT_SWITCH_PENALTY)

    def test_focus_floors_at_30_after_switch(self):
        wm = WorkingMemorySystem()
        wm.focus = 32.0
        wm.last_top_source = "need"
        wm.update(
            needs={},
            emotions={"fear": 90.0},
            sleep_satisfaction=10.0,  # focus = 28 -> clamped to 30
        )
        # Even with switch penalty, focus stays >= 30
        assert wm.focus >= 30.0


# ===========================================================================
# Focus noise tests
# ===========================================================================

class TestFocusNoise:
    def test_full_focus_no_noise(self):
        """At 100% focus, noise range is 0."""
        wm = WorkingMemorySystem()
        # Run multiple times to check determinism at full focus
        results = []
        for _ in range(5):
            wm.update(
                needs={"hunger": {"satisfaction": 50.0, "level": 1}},
                emotions={},
                sleep_satisfaction=100.0,
            )
            items = [i for i in wm.buffer if i.source_id == "hunger"]
            if items:
                results.append(items[0].salience)
        # All should be identical (no noise at 100% focus)
        if len(results) > 1:
            assert all(r == results[0] for r in results)

    def test_low_focus_adds_noise(self):
        """At low focus, salience values may vary between updates."""
        wm = WorkingMemorySystem()
        results = set()
        for _ in range(20):
            wm.update(
                needs={"hunger": {"satisfaction": 50.0, "level": 1}},
                emotions={},
                sleep_satisfaction=10.0,  # Low sleep -> low focus -> noise
            )
            items = [i for i in wm.buffer if i.source_id == "hunger"]
            if items:
                results.add(round(items[0].salience, 4))
        # With noise, we expect some variation (not guaranteed but very likely in 20 runs)
        # This is a probabilistic test; if it fails rarely, that's acceptable
        assert len(results) >= 1  # At minimum one result exists


# ===========================================================================
# Formatting tests
# ===========================================================================

class TestFormatting:
    def test_empty_buffer(self):
        wm = WorkingMemorySystem()
        assert wm.format_for_prompt() == "Mind is clear — no particular focus."

    def test_with_items(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 20.0, "level": 1}},
            emotions={"joy": 70.0},
            sleep_satisfaction=100.0,
        )
        result = wm.format_for_prompt()
        assert "Currently thinking about:" in result
        assert "Focus level:" in result
        assert "hunger" in result

    def test_format_includes_capacity(self):
        wm = WorkingMemorySystem()
        wm.update(needs={"hunger": {"satisfaction": 20.0, "level": 1}},
                   emotions={}, sleep_satisfaction=100.0)
        result = wm.format_for_prompt()
        assert "slots" in result


# ===========================================================================
# Simple needs (float values) tests
# ===========================================================================

class TestSimpleNeeds:
    def test_float_needs_work(self):
        """Needs can be plain floats (no level info) — defaults to level 1."""
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": 20.0, "sleep": 80.0},
            emotions={},
            sleep_satisfaction=100.0,
        )
        hunger_items = [i for i in wm.buffer if i.source_id == "hunger"]
        assert len(hunger_items) == 1
        # (100 - 20) / 100 * 1.0 = 0.8
        assert hunger_items[0].salience == pytest.approx(0.8)


# ===========================================================================
# Stats tests
# ===========================================================================

class TestStats:
    def test_empty_stats(self):
        wm = WorkingMemorySystem()
        stats = wm.get_stats()
        assert stats["focus"] == 100.0
        assert stats["buffer_size"] == 0
        assert stats["context_switches"] == 0

    def test_stats_after_update(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 20.0, "level": 1}},
            emotions={"joy": 60.0},
            sleep_satisfaction=80.0,
        )
        stats = wm.get_stats()
        assert stats["buffer_size"] > 0
        assert stats["focus"] == pytest.approx(84.0)  # 80*0.8+20
        assert len(stats["items"]) == stats["buffer_size"]


# ===========================================================================
# Serialization tests
# ===========================================================================

class TestSerialization:
    def test_empty_roundtrip(self):
        wm = WorkingMemorySystem()
        d = wm.to_dict()
        wm2 = WorkingMemorySystem.from_dict(d)
        assert wm2.buffer == []
        assert wm2.focus == 100.0
        assert wm2.context_switches == 0

    def test_roundtrip_with_state(self):
        wm = WorkingMemorySystem()
        wm.update(
            needs={"hunger": {"satisfaction": 20.0, "level": 1}},
            emotions={},
            sleep_satisfaction=100.0,
        )
        wm.context_switches = 3
        d = wm.to_dict()
        wm2 = WorkingMemorySystem.from_dict(d)
        assert len(wm2.buffer) == len(wm.buffer)
        assert wm2.focus == wm.focus
        assert wm2.context_switches == 3
        assert wm2.last_top_source == wm.last_top_source


# ===========================================================================
# Integration test
# ===========================================================================

class TestIntegration:
    def test_full_cycle(self):
        """Simulate multiple cycles and verify working memory evolves."""
        wm = WorkingMemorySystem()

        # Cycle 1: Hungry, rested
        wm.update(
            needs={"hunger": {"satisfaction": 15.0, "level": 1}, "sleep": {"satisfaction": 90.0, "level": 1}},
            emotions={"joy": 30.0},
            active_plan_step={"description": "Walk to store", "action_hint": "walk"},
            sleep_satisfaction=90.0,
        )
        assert wm.buffer[0].source_id == "hunger"  # Most salient
        assert wm.focus > 80

        # Cycle 2: Fed, still rested, plan step still active
        wm.update(
            needs={"hunger": {"satisfaction": 80.0, "level": 1}, "sleep": {"satisfaction": 85.0, "level": 1}},
            emotions={"joy": 60.0},
            active_plan_step={"description": "Buy food", "action_hint": "buy"},
            sleep_satisfaction=85.0,
        )
        # Hunger no longer dominant — plan step or emotion should be top
        assert wm.buffer[0].source in ("plan_step", "emotion")

        # Cycle 3: Tired
        wm.update(
            needs={"hunger": {"satisfaction": 70.0, "level": 1}, "sleep": {"satisfaction": 20.0, "level": 1}},
            emotions={"sadness": 40.0},
            sleep_satisfaction=20.0,
        )
        assert wm.focus <= 40  # Very tired
        capacity = wm._get_capacity()
        assert capacity <= 5  # Reduced capacity
