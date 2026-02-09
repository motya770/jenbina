"""Tests for the goal system."""
import time
import json
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from core.goals.goal_system import (
    Goal,
    GoalSystem,
    DECAY_RATES,
    ABANDONMENT_THRESHOLDS,
)
from core.learning.learning_system import Experience


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_goal(**overrides) -> Goal:
    defaults = dict(
        description="Test goal",
        horizon="short_term",
        source_needs=["hunger"],
        recommended_actions=["eat food"],
    )
    defaults.update(overrides)
    return Goal(**defaults)


def make_experience(**overrides) -> Experience:
    defaults = dict(
        action_taken="eat food",
        action_reasoning="hungry",
        needs_before={"hunger": 30.0},
        needs_after={"hunger": 60.0},
        needs_delta={"hunger": 30.0},
        emotions_before={"joy": 40.0},
        emotions_after={"joy": 50.0},
        emotions_delta={"joy": 10.0},
        world_context={},
        overall_satisfaction_before=40.0,
        overall_satisfaction_after=55.0,
    )
    defaults.update(overrides)
    return Experience(**defaults)


def make_mock_llm(response_text="[]"):
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_text
    mock.invoke.return_value = mock_response
    return mock


# ===========================================================================
# Goal dataclass tests
# ===========================================================================

class TestGoal:
    def test_initialization(self):
        g = make_goal()
        assert g.description == "Test goal"
        assert g.horizon == "short_term"
        assert g.source_needs == ["hunger"]
        assert g.recommended_actions == ["eat food"]
        assert g.progress == 0.0
        assert g.confidence == 0.7
        assert g.status == "active"
        assert g.times_advanced == 0
        assert g.times_regressed == 0

    def test_advance(self):
        g = make_goal()
        g.advance(0.2)
        assert g.progress == pytest.approx(0.2)
        assert g.times_advanced == 1

    def test_advance_caps_at_one(self):
        g = make_goal(progress=0.9)
        g.advance(0.5)
        assert g.progress == pytest.approx(1.0)

    def test_regress(self):
        g = make_goal(progress=0.5)
        g.regress(0.2)
        assert g.progress == pytest.approx(0.3)
        assert g.times_regressed == 1

    def test_regress_floors_at_zero(self):
        g = make_goal(progress=0.1)
        g.regress(0.5)
        assert g.progress == pytest.approx(0.0)

    def test_decay_short_term(self):
        g = make_goal(horizon="short_term", confidence=0.7)
        g.decay(1.0)
        assert g.confidence == pytest.approx(0.7 - DECAY_RATES["short_term"])

    def test_decay_mid_term(self):
        g = make_goal(horizon="mid_term", confidence=0.7)
        g.decay(1.0)
        assert g.confidence == pytest.approx(0.7 - DECAY_RATES["mid_term"])

    def test_decay_long_term(self):
        g = make_goal(horizon="long_term", confidence=0.7)
        g.decay(1.0)
        assert g.confidence == pytest.approx(0.7 - DECAY_RATES["long_term"])

    def test_decay_floors_at_zero(self):
        g = make_goal(confidence=0.01)
        g.decay(10.0)
        assert g.confidence == pytest.approx(0.0)

    def test_is_active(self):
        g = make_goal(confidence=0.5)
        assert g.is_active() is True

    def test_is_active_below_threshold(self):
        g = make_goal(horizon="short_term", confidence=0.05)
        assert g.is_active() is False

    def test_is_active_completed(self):
        g = make_goal(confidence=0.9, status="completed")
        assert g.is_active() is False

    def test_is_active_abandoned(self):
        g = make_goal(confidence=0.9, status="abandoned")
        assert g.is_active() is False

    def test_complete(self):
        g = make_goal()
        g.complete()
        assert g.status == "completed"

    def test_abandon(self):
        g = make_goal()
        g.abandon()
        assert g.status == "abandoned"

    def test_to_dict(self):
        g = make_goal()
        d = g.to_dict()
        assert d["description"] == "Test goal"
        assert d["horizon"] == "short_term"
        assert d["source_needs"] == ["hunger"]
        assert d["recommended_actions"] == ["eat food"]
        assert d["progress"] == 0.0
        assert d["confidence"] == 0.7
        assert d["status"] == "active"

    def test_from_dict_roundtrip(self):
        g = make_goal(progress=0.4, confidence=0.8, times_advanced=3)
        d = g.to_dict()
        g2 = Goal.from_dict(d)
        assert g2.description == g.description
        assert g2.progress == g.progress
        assert g2.confidence == g.confidence
        assert g2.times_advanced == g.times_advanced


# ===========================================================================
# GoalSystem basic tests
# ===========================================================================

class TestGoalSystem:
    def test_initialization(self):
        llm = make_mock_llm()
        gs = GoalSystem(llm)
        assert gs.goals == []
        assert gs._experience_count_since_generation == 0

    def test_should_generate_false_initially(self):
        gs = GoalSystem(make_mock_llm())
        assert gs.should_generate() is False

    def test_should_generate_after_interval(self):
        gs = GoalSystem(make_mock_llm())
        gs._experience_count_since_generation = 5
        assert gs.should_generate() is True

    def test_reset_generation_counter(self):
        gs = GoalSystem(make_mock_llm())
        gs._experience_count_since_generation = 5
        gs.reset_generation_counter()
        assert gs._experience_count_since_generation == 0


# ===========================================================================
# Progress tracking tests
# ===========================================================================

class TestGoalSystemProgress:
    def test_advance_on_positive_delta(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(source_needs=["hunger"], recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(
            action_taken="eat food",
            needs_delta={"hunger": 20.0},
        )
        advanced = gs.update_progress(exp)

        assert len(advanced) == 1
        assert goal.progress == pytest.approx(0.2)
        assert goal.times_advanced == 1

    def test_regress_on_negative_delta(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(source_needs=["hunger"], recommended_actions=["eat food"], progress=0.5)
        gs.goals.append(goal)

        exp = make_experience(
            action_taken="eat food",
            needs_delta={"hunger": -10.0},
        )
        advanced = gs.update_progress(exp)

        assert len(advanced) == 0
        assert goal.progress == pytest.approx(0.4)
        assert goal.times_regressed == 1

    def test_no_effect_on_unrelated_action(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(source_needs=["hunger"], recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(
            action_taken="go to sleep",
            needs_delta={"hunger": 20.0},
        )
        advanced = gs.update_progress(exp)

        assert len(advanced) == 0
        assert goal.progress == pytest.approx(0.0)

    def test_inactive_goals_skipped(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(status="completed", recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(action_taken="eat food", needs_delta={"hunger": 20.0})
        advanced = gs.update_progress(exp)
        assert len(advanced) == 0

    def test_partial_action_match(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(source_needs=["hunger"], recommended_actions=["eat"])
        gs.goals.append(goal)

        exp = make_experience(action_taken="eat a sandwich", needs_delta={"hunger": 15.0})
        advanced = gs.update_progress(exp)
        assert len(advanced) == 1

    def test_experience_counter_increments(self):
        gs = GoalSystem(make_mock_llm())
        exp = make_experience()
        gs.update_progress(exp)
        assert gs._experience_count_since_generation == 1

    def test_multiple_source_needs_averaged(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(
            source_needs=["hunger", "health"],
            recommended_actions=["eat food"],
        )
        gs.goals.append(goal)

        exp = make_experience(
            action_taken="eat food",
            needs_delta={"hunger": 20.0, "health": 10.0},
        )
        advanced = gs.update_progress(exp)

        assert len(advanced) == 1
        # avg delta = (20+10)/2 = 15, progress = 15/100 = 0.15
        assert goal.progress == pytest.approx(0.15)


# ===========================================================================
# Decay tests
# ===========================================================================

class TestGoalSystemDecay:
    def test_decay_reduces_confidence(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(confidence=0.7)
        gs.goals.append(goal)
        gs.decay_all_goals(1.0)
        assert goal.confidence < 0.7

    def test_decay_abandons_below_threshold(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(horizon="short_term", confidence=0.12)
        gs.goals.append(goal)
        gs.decay_all_goals(1.0)
        assert goal.status == "abandoned"

    def test_decay_does_not_abandon_completed(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(confidence=0.01, status="completed")
        gs.goals.append(goal)
        gs.decay_all_goals(1.0)
        assert goal.status == "completed"

    def test_zero_hours_no_change(self):
        gs = GoalSystem(make_mock_llm())
        goal = make_goal(confidence=0.7)
        gs.goals.append(goal)
        gs.decay_all_goals(0.0)
        assert goal.confidence == pytest.approx(0.7)


# ===========================================================================
# Formatting tests
# ===========================================================================

class TestGoalSystemFormatting:
    def test_empty_goals(self):
        gs = GoalSystem(make_mock_llm())
        assert gs.format_goals_for_prompt() == "No goals set yet."

    def test_active_goals_formatted(self):
        gs = GoalSystem(make_mock_llm())
        gs.goals.append(make_goal(description="Eat something", horizon="short_term", confidence=0.8))
        result = gs.format_goals_for_prompt()
        assert "Eat something" in result
        assert "short_term" in result

    def test_inactive_goals_excluded(self):
        gs = GoalSystem(make_mock_llm())
        gs.goals.append(make_goal(description="Active goal", confidence=0.8))
        gs.goals.append(make_goal(description="Dead goal", confidence=0.01))
        result = gs.format_goals_for_prompt()
        assert "Active goal" in result
        assert "Dead goal" not in result

    def test_sorted_by_horizon_then_progress(self):
        gs = GoalSystem(make_mock_llm())
        gs.goals.append(make_goal(description="Long", horizon="long_term", progress=0.9, confidence=0.8))
        gs.goals.append(make_goal(description="Short", horizon="short_term", progress=0.1, confidence=0.8))
        gs.goals.append(make_goal(description="Mid", horizon="mid_term", progress=0.5, confidence=0.8))
        result = gs.format_goals_for_prompt()
        lines = result.strip().split("\n")
        assert "Short" in lines[0]
        assert "Mid" in lines[1]
        assert "Long" in lines[2]


# ===========================================================================
# Generation tests
# ===========================================================================

class TestGoalSystemGeneration:
    def test_generate_goals_from_llm(self):
        response = json.dumps([{
            "description": "Find food",
            "horizon": "short_term",
            "source_needs": ["hunger"],
            "recommended_actions": ["go to restaurant"],
        }])
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)

        gs.generate_goals(
            needs={"hunger": 20.0},
            emotions={"joy": 30.0},
            personality_traits={},
            lessons=[],
        )

        assert len(gs.goals) == 1
        assert gs.goals[0].description == "Find food"
        assert gs.goals[0].horizon == "short_term"

    def test_generate_handles_dict_wrapper(self):
        response = json.dumps({"goals": [{
            "description": "Make a friend",
            "horizon": "mid_term",
            "source_needs": ["friendship"],
            "recommended_actions": ["talk to people"],
        }]})
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 1

    def test_generate_handles_single_dict(self):
        response = json.dumps({
            "description": "Sleep well",
            "horizon": "short_term",
            "source_needs": ["sleep"],
            "recommended_actions": ["go to bed"],
        })
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 1

    def test_generate_max_three(self):
        goals_list = [
            {"description": f"Goal {i}", "horizon": "short_term", "source_needs": [], "recommended_actions": []}
            for i in range(5)
        ]
        llm = make_mock_llm(json.dumps(goals_list))
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 3

    def test_generate_respects_max_goals(self):
        llm = make_mock_llm(json.dumps([{
            "description": "New goal",
            "horizon": "short_term",
            "source_needs": [],
            "recommended_actions": [],
        }]))
        gs = GoalSystem(llm)
        # Fill to MAX_GOALS
        for i in range(GoalSystem.MAX_GOALS):
            gs.goals.append(make_goal(description=f"Goal {i}", confidence=0.8))
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == GoalSystem.MAX_GOALS

    def test_generate_survives_llm_error(self):
        llm = MagicMock()
        llm.invoke.side_effect = RuntimeError("LLM down")
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 0

    def test_generate_invalid_horizon_defaults(self):
        response = json.dumps([{
            "description": "Bad horizon",
            "horizon": "ultra_long_term",
            "source_needs": [],
            "recommended_actions": [],
        }])
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert gs.goals[0].horizon == "short_term"

    def test_generate_skips_invalid_items(self):
        response = json.dumps([
            {"not_a_goal": True},
            {"description": "Valid goal", "horizon": "short_term", "source_needs": [], "recommended_actions": []},
        ])
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        gs.generate_goals(needs={}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 1
        assert gs.goals[0].description == "Valid goal"


# ===========================================================================
# Milestone check tests
# ===========================================================================

class TestGoalSystemMilestone:
    def test_milestone_completes_goal(self):
        response = json.dumps({"achieved": True, "explanation": "Hunger satisfied"})
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        goal = make_goal(progress=0.9, source_needs=["hunger"], recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(action_taken="eat food", needs_delta={"hunger": 5.0})
        gs._last_experiences = [exp]
        gs.check_milestone(goal)

        assert goal.status == "completed"

    def test_milestone_does_not_complete_if_not_achieved(self):
        response = json.dumps({"achieved": False, "explanation": "Not yet"})
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)
        goal = make_goal(progress=0.9, source_needs=["hunger"], recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(action_taken="eat food", needs_delta={"hunger": 5.0})
        gs._last_experiences = [exp]
        gs.check_milestone(goal)

        assert goal.status == "active"

    def test_milestone_survives_llm_error(self):
        llm = MagicMock()
        llm.invoke.side_effect = RuntimeError("LLM error")
        gs = GoalSystem(llm)
        goal = make_goal(progress=0.9, recommended_actions=["eat food"])
        gs.goals.append(goal)

        exp = make_experience(action_taken="eat food")
        gs._last_experiences = [exp]
        gs.check_milestone(goal)

        assert goal.status == "active"

    def test_milestone_no_related_experiences(self):
        llm = make_mock_llm()
        gs = GoalSystem(llm)
        goal = make_goal(progress=0.9, recommended_actions=["eat food"])
        gs.goals.append(goal)
        gs._last_experiences = []
        gs.check_milestone(goal)
        # LLM should not be called
        llm.invoke.assert_not_called()


# ===========================================================================
# Serialization tests
# ===========================================================================

class TestGoalSystemSerialization:
    def test_empty_roundtrip(self):
        llm = make_mock_llm()
        gs = GoalSystem(llm)
        d = gs.to_dict()
        gs2 = GoalSystem.from_dict(d, llm)
        assert gs2.goals == []
        assert gs2._experience_count_since_generation == 0

    def test_roundtrip_with_data(self):
        llm = make_mock_llm()
        gs = GoalSystem(llm)
        gs.goals.append(make_goal(description="Persisted goal", progress=0.4))
        gs._experience_count_since_generation = 3

        d = gs.to_dict()
        gs2 = GoalSystem.from_dict(d, llm)

        assert len(gs2.goals) == 1
        assert gs2.goals[0].description == "Persisted goal"
        assert gs2.goals[0].progress == pytest.approx(0.4)
        assert gs2._experience_count_since_generation == 3

    def test_counter_preserved(self):
        llm = make_mock_llm()
        gs = GoalSystem(llm)
        gs._experience_count_since_generation = 4
        d = gs.to_dict()
        gs2 = GoalSystem.from_dict(d, llm)
        assert gs2._experience_count_since_generation == 4


# ===========================================================================
# Stats tests
# ===========================================================================

class TestGoalSystemStats:
    def test_empty_stats(self):
        gs = GoalSystem(make_mock_llm())
        stats = gs.get_goal_stats()
        assert stats["total_goals"] == 0
        assert stats["active_goals"] == 0
        assert stats["completed_goals"] == 0
        assert stats["abandoned_goals"] == 0

    def test_stats_with_data(self):
        gs = GoalSystem(make_mock_llm())
        gs.goals.append(make_goal(description="Active", confidence=0.8))
        gs.goals.append(make_goal(description="Done", status="completed"))
        gs.goals.append(make_goal(description="Dead", status="abandoned"))

        stats = gs.get_goal_stats()
        assert stats["total_goals"] == 3
        assert stats["active_goals"] == 1
        assert stats["completed_goals"] == 1
        assert stats["abandoned_goals"] == 1
        assert len(stats["goals"]) == 1
        assert stats["goals"][0]["description"] == "Active"

    def test_completed_capped_at_five(self):
        gs = GoalSystem(make_mock_llm())
        for i in range(8):
            gs.goals.append(make_goal(description=f"Done {i}", status="completed"))
        stats = gs.get_goal_stats()
        assert len(stats["completed"]) == 5


# ===========================================================================
# Integration test
# ===========================================================================

class TestGoalSystemIntegration:
    def test_full_goal_lifecycle(self):
        """Test: generate → advance → decay → abandon."""
        response = json.dumps([{
            "description": "Eat when hungry",
            "horizon": "short_term",
            "source_needs": ["hunger"],
            "recommended_actions": ["eat food"],
        }])
        llm = make_mock_llm(response)
        gs = GoalSystem(llm)

        # Generate
        gs.generate_goals(needs={"hunger": 20.0}, emotions={}, personality_traits={}, lessons=[])
        assert len(gs.goals) == 1
        goal = gs.goals[0]
        assert goal.status == "active"

        # Advance via experience
        exp = make_experience(action_taken="eat food", needs_delta={"hunger": 25.0})
        advanced = gs.update_progress(exp)
        assert len(advanced) == 1
        assert goal.progress == pytest.approx(0.25)

        # Decay
        gs.decay_all_goals(10.0)
        assert goal.confidence < 0.7

        # Heavy decay to abandonment
        gs.decay_all_goals(100.0)
        assert goal.status == "abandoned"
