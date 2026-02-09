"""Tests for the planning system."""
import time
import json
import pytest
from unittest.mock import MagicMock

from core.planning.planning_system import (
    PlanStep,
    Plan,
    PlanningSystem,
)
from core.learning.learning_system import Experience


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_step(**overrides) -> PlanStep:
    defaults = dict(
        description="Go to the store",
        action_hint="walk to store",
        expected_outcome="be at the store",
        estimated_cycles=2,
    )
    defaults.update(overrides)
    return PlanStep(**defaults)


def make_plan(**overrides) -> Plan:
    defaults = dict(
        goal_description="Get food",
        goal_id=0,
    )
    defaults.update(overrides)
    plan = Plan(**defaults)
    if not plan.steps:
        plan.steps = [
            make_step(description="Go to store", action_hint="walk to store", status="active"),
            make_step(description="Buy food", action_hint="buy food"),
            make_step(description="Eat food", action_hint="eat food"),
        ]
    return plan


def make_experience(**overrides) -> Experience:
    defaults = dict(
        action_taken="walk to store",
        action_reasoning="need food",
        needs_before={"hunger": 30.0},
        needs_after={"hunger": 35.0},
        needs_delta={"hunger": 5.0},
        emotions_before={"joy": 40.0},
        emotions_after={"joy": 45.0},
        emotions_delta={"joy": 5.0},
        world_context={},
        overall_satisfaction_before=40.0,
        overall_satisfaction_after=45.0,
    )
    defaults.update(overrides)
    return Experience(**defaults)


def make_mock_llm(response_text="{}"):
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_text
    mock.invoke.return_value = mock_response
    return mock


# ===========================================================================
# PlanStep tests
# ===========================================================================

class TestPlanStep:
    def test_initialization(self):
        s = make_step()
        assert s.description == "Go to the store"
        assert s.action_hint == "walk to store"
        assert s.expected_outcome == "be at the store"
        assert s.estimated_cycles == 2
        assert s.actual_cycles == 0
        assert s.status == "pending"
        assert s.failure_reason == ""

    def test_to_dict(self):
        s = make_step()
        d = s.to_dict()
        assert d["description"] == "Go to the store"
        assert d["action_hint"] == "walk to store"
        assert d["estimated_cycles"] == 2

    def test_from_dict_roundtrip(self):
        s = make_step(actual_cycles=3, status="completed")
        d = s.to_dict()
        s2 = PlanStep.from_dict(d)
        assert s2.description == s.description
        assert s2.actual_cycles == 3
        assert s2.status == "completed"


# ===========================================================================
# Plan tests
# ===========================================================================

class TestPlan:
    def test_initialization(self):
        p = Plan(goal_description="Test", goal_id=0)
        assert p.goal_description == "Test"
        assert p.status == "active"
        assert p.times_replanned == 0
        assert p.consecutive_overrides == 0

    def test_get_current_step(self):
        p = make_plan()
        step = p.get_current_step()
        assert step is not None
        assert step.description == "Go to store"

    def test_get_current_step_none_when_completed(self):
        p = make_plan(status="completed")
        assert p.get_current_step() is None

    def test_advance(self):
        p = make_plan()
        p.advance()
        assert p.current_step_index == 1
        assert p.steps[0].status == "completed"
        assert p.steps[1].status == "active"
        assert p.status == "active"

    def test_advance_completes_plan(self):
        p = make_plan()
        p.advance()  # step 0 -> 1
        p.advance()  # step 1 -> 2
        p.advance()  # step 2 -> done
        assert p.status == "completed"

    def test_fail_current_step(self):
        p = make_plan()
        p.fail_current_step("store is closed")
        step = p.steps[0]
        assert step.status == "failed"
        assert step.failure_reason == "store is closed"

    def test_get_completed_steps(self):
        p = make_plan()
        p.advance()
        p.advance()
        completed = p.get_completed_steps()
        assert len(completed) == 2

    def test_to_dict_roundtrip(self):
        p = make_plan()
        p.advance()
        d = p.to_dict()
        p2 = Plan.from_dict(d)
        assert p2.goal_description == p.goal_description
        assert p2.current_step_index == 1
        assert len(p2.steps) == 3
        assert p2.steps[0].status == "completed"


# ===========================================================================
# PlanningSystem basic tests
# ===========================================================================

class TestPlanningSystem:
    def test_initialization(self):
        ps = PlanningSystem(make_mock_llm())
        assert ps.plans == []

    def test_get_current_step_empty(self):
        ps = PlanningSystem(make_mock_llm())
        assert ps.get_current_step() is None

    def test_format_plan_no_active(self):
        ps = PlanningSystem(make_mock_llm())
        assert ps.format_plan_for_prompt() == "No active plan."

    def test_format_plan_with_active(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())
        result = ps.format_plan_for_prompt()
        assert "Get food" in result
        assert "Go to store" in result
        assert "walk to store" in result
        assert "Step 1 of 3" in result

    def test_get_plan_for_goal(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan(goal_id=5))
        assert ps.get_plan_for_goal(5) is not None
        assert ps.get_plan_for_goal(3) is None

    def test_get_plan_for_goal_ignores_non_active(self):
        ps = PlanningSystem(make_mock_llm())
        p = make_plan(goal_id=5, status="completed")
        ps.plans.append(p)
        assert ps.get_plan_for_goal(5) is None


# ===========================================================================
# Plan creation tests
# ===========================================================================

class TestPlanningSystemCreation:
    def test_create_plan_from_llm(self):
        response = json.dumps({"steps": [
            {"description": "Find job", "action_hint": "look for work", "expected_outcome": "have a lead", "estimated_cycles": 2},
            {"description": "Work", "action_hint": "work", "expected_outcome": "earn money", "estimated_cycles": 3},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = ps.create_plan(
            goal_description="Earn money",
            goal_id=0,
            needs={"hunger": 50.0},
            emotions={"joy": 40.0},
            world_context={"location": "home"},
            lessons=[],
        )
        assert plan is not None
        assert len(plan.steps) == 2
        assert plan.steps[0].status == "active"
        assert plan.steps[0].description == "Find job"
        assert plan.goal_description == "Earn money"

    def test_create_plan_skips_duplicate_goal(self):
        response = json.dumps({"steps": [
            {"description": "Step", "action_hint": "do", "expected_outcome": "done", "estimated_cycles": 1},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        ps.create_plan("Goal", 0, {}, {}, {}, [])
        result = ps.create_plan("Goal", 0, {}, {}, {}, [])
        assert result is None
        assert len(ps.plans) == 1

    def test_create_plan_respects_max_active(self):
        response = json.dumps({"steps": [
            {"description": "Step", "action_hint": "do", "expected_outcome": "done", "estimated_cycles": 1},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        for i in range(PlanningSystem.MAX_ACTIVE_PLANS):
            ps.create_plan(f"Goal {i}", i, {}, {}, {}, [])
        result = ps.create_plan("Extra", 99, {}, {}, {}, [])
        assert result is None

    def test_create_plan_max_6_steps(self):
        steps = [
            {"description": f"Step {i}", "action_hint": f"do {i}", "expected_outcome": f"done {i}", "estimated_cycles": 1}
            for i in range(10)
        ]
        ps = PlanningSystem(make_mock_llm(json.dumps({"steps": steps})))
        plan = ps.create_plan("Big goal", 0, {}, {}, {}, [])
        assert len(plan.steps) == 6

    def test_create_plan_clamps_estimated_cycles(self):
        response = json.dumps({"steps": [
            {"description": "S", "action_hint": "do", "expected_outcome": "done", "estimated_cycles": 100},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = ps.create_plan("Goal", 0, {}, {}, {}, [])
        assert plan.steps[0].estimated_cycles == 5

    def test_create_plan_survives_llm_error(self):
        llm = MagicMock()
        llm.invoke.side_effect = RuntimeError("LLM down")
        ps = PlanningSystem(llm)
        result = ps.create_plan("Goal", 0, {}, {}, {}, [])
        assert result is None

    def test_create_plan_handles_list_response(self):
        response = json.dumps([
            {"description": "Step 1", "action_hint": "do", "expected_outcome": "done", "estimated_cycles": 1},
        ])
        ps = PlanningSystem(make_mock_llm(response))
        plan = ps.create_plan("Goal", 0, {}, {}, {}, [])
        assert plan is not None
        assert len(plan.steps) == 1

    def test_create_plan_skips_invalid_items(self):
        response = json.dumps({"steps": [
            {"not_a_step": True},
            {"description": "Valid", "action_hint": "do", "expected_outcome": "done", "estimated_cycles": 1},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = ps.create_plan("Goal", 0, {}, {}, {}, [])
        assert len(plan.steps) == 1


# ===========================================================================
# Step evaluation tests
# ===========================================================================

class TestPlanningSystemEvaluation:
    def test_step_completed_on_match_and_positive(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())

        exp = make_experience(
            action_taken="walk to store",
            overall_satisfaction_before=40.0,
            overall_satisfaction_after=45.0,
        )
        result = ps.evaluate_step(exp)
        assert result == "step_completed"
        assert ps.plans[0].current_step_index == 1

    def test_step_in_progress_on_match_and_negative(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())

        exp = make_experience(
            action_taken="walk to store",
            overall_satisfaction_before=45.0,
            overall_satisfaction_after=40.0,
        )
        result = ps.evaluate_step(exp)
        assert result == "step_in_progress"

    def test_step_overridden_on_different_action(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())

        exp = make_experience(action_taken="go to sleep")
        result = ps.evaluate_step(exp)
        assert result == "step_overridden"
        assert ps.plans[0].consecutive_overrides == 1

    def test_no_plan_returns_none(self):
        ps = PlanningSystem(make_mock_llm())
        exp = make_experience()
        assert ps.evaluate_step(exp) is None

    def test_actual_cycles_incremented(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())

        exp = make_experience(action_taken="go to sleep")
        ps.evaluate_step(exp)
        assert ps.plans[0].steps[0].actual_cycles == 1

    def test_plan_completes_when_all_steps_done(self):
        ps = PlanningSystem(make_mock_llm())
        plan = make_plan()
        ps.plans.append(plan)

        # Complete all 3 steps
        actions = ["walk to store", "buy food", "eat food"]
        for action in actions:
            exp = make_experience(
                action_taken=action,
                overall_satisfaction_before=40.0,
                overall_satisfaction_after=45.0,
            )
            ps.evaluate_step(exp)

        assert plan.status == "completed"

    def test_override_resets_on_match(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())

        # Override twice
        ps.evaluate_step(make_experience(action_taken="sleep"))
        ps.evaluate_step(make_experience(action_taken="sleep"))
        assert ps.plans[0].consecutive_overrides == 2

        # Match resets counter (and completes step)
        ps.evaluate_step(make_experience(
            action_taken="walk to store",
            overall_satisfaction_before=40.0,
            overall_satisfaction_after=45.0,
        ))
        assert ps.plans[0].consecutive_overrides == 0


# ===========================================================================
# Replan check tests
# ===========================================================================

class TestPlanningSystemReplan:
    def test_check_replan_when_stuck(self):
        response = json.dumps({"steps": [
            {"description": "Alternative", "action_hint": "try different", "expected_outcome": "done", "estimated_cycles": 2},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = make_plan()
        plan.steps[0].estimated_cycles = 1
        plan.steps[0].actual_cycles = 3  # > 1 * 2.0
        ps.plans.append(plan)

        new_plan = ps.check_for_replan(needs={"hunger": 20.0}, world_context={})
        assert new_plan is not None
        assert plan.status == "replanned"
        assert new_plan.times_replanned == 1

    def test_check_replan_when_overridden(self):
        response = json.dumps({"steps": [
            {"description": "Alternative", "action_hint": "try different", "expected_outcome": "done", "estimated_cycles": 2},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = make_plan()
        plan.consecutive_overrides = 3
        ps.plans.append(plan)

        new_plan = ps.check_for_replan(needs={}, world_context={})
        assert new_plan is not None

    def test_no_replan_when_not_stuck(self):
        ps = PlanningSystem(make_mock_llm())
        plan = make_plan()
        plan.steps[0].estimated_cycles = 5
        plan.steps[0].actual_cycles = 1
        ps.plans.append(plan)

        result = ps.check_for_replan(needs={}, world_context={})
        assert result is None

    def test_replan_fails_at_max_replans(self):
        ps = PlanningSystem(make_mock_llm())
        plan = make_plan()
        plan.times_replanned = Plan.MAX_REPLANS
        plan.steps[0].estimated_cycles = 1
        plan.steps[0].actual_cycles = 10
        ps.plans.append(plan)

        result = ps.check_for_replan(needs={}, world_context={})
        assert result is None
        assert plan.status == "failed"

    def test_replan_increments_counter(self):
        response = json.dumps({"steps": [
            {"description": "New", "action_hint": "new", "expected_outcome": "done", "estimated_cycles": 1},
        ]})
        ps = PlanningSystem(make_mock_llm(response))
        plan = make_plan()
        plan.times_replanned = 1
        ps.plans.append(plan)

        new_plan = ps.replan(plan, "stuck", needs={}, world_context={})
        assert new_plan is not None
        assert new_plan.times_replanned == 2

    def test_replan_survives_llm_error(self):
        llm = MagicMock()
        llm.invoke.side_effect = RuntimeError("LLM error")
        ps = PlanningSystem(llm)
        plan = make_plan()
        ps.plans.append(plan)

        result = ps.replan(plan, "stuck", needs={}, world_context={})
        assert result is None
        assert plan.status == "failed"


# ===========================================================================
# Serialization tests
# ===========================================================================

class TestPlanningSystemSerialization:
    def test_empty_roundtrip(self):
        llm = make_mock_llm()
        ps = PlanningSystem(llm)
        d = ps.to_dict()
        ps2 = PlanningSystem.from_dict(d, llm)
        assert ps2.plans == []

    def test_roundtrip_with_data(self):
        llm = make_mock_llm()
        ps = PlanningSystem(llm)
        ps.plans.append(make_plan())
        ps.plans[0].advance()

        d = ps.to_dict()
        ps2 = PlanningSystem.from_dict(d, llm)

        assert len(ps2.plans) == 1
        assert ps2.plans[0].goal_description == "Get food"
        assert ps2.plans[0].current_step_index == 1
        assert ps2.plans[0].steps[0].status == "completed"


# ===========================================================================
# Stats tests
# ===========================================================================

class TestPlanningSystemStats:
    def test_empty_stats(self):
        ps = PlanningSystem(make_mock_llm())
        stats = ps.get_planning_stats()
        assert stats["total_plans"] == 0
        assert stats["active_plans"] == 0
        assert stats["completed_plans"] == 0
        assert stats["failed_plans"] == 0

    def test_stats_with_data(self):
        ps = PlanningSystem(make_mock_llm())
        ps.plans.append(make_plan())
        ps.plans.append(make_plan(goal_id=1, goal_description="Sleep", status="completed"))
        ps.plans.append(make_plan(goal_id=2, goal_description="Failed", status="failed"))

        stats = ps.get_planning_stats()
        assert stats["total_plans"] == 3
        assert stats["active_plans"] == 1
        assert stats["completed_plans"] == 1
        assert stats["failed_plans"] == 1
        assert len(stats["plans"]) == 1
        assert stats["plans"][0]["goal_description"] == "Get food"


# ===========================================================================
# Integration test
# ===========================================================================

class TestPlanningSystemIntegration:
    def test_full_plan_lifecycle(self):
        """Test: create plan → execute steps → complete."""
        response = json.dumps({"steps": [
            {"description": "Walk to store", "action_hint": "walk to store", "expected_outcome": "at store", "estimated_cycles": 1},
            {"description": "Buy food", "action_hint": "buy food", "expected_outcome": "have food", "estimated_cycles": 1},
            {"description": "Eat", "action_hint": "eat food", "expected_outcome": "not hungry", "estimated_cycles": 1},
        ]})
        ps = PlanningSystem(make_mock_llm(response))

        # Create plan
        plan = ps.create_plan("Get food to eat", 0, {"hunger": 20.0}, {}, {}, [])
        assert plan is not None
        assert plan.status == "active"
        assert len(plan.steps) == 3

        # Execute step 1
        exp1 = make_experience(
            action_taken="walk to store",
            overall_satisfaction_before=40.0,
            overall_satisfaction_after=42.0,
        )
        result = ps.evaluate_step(exp1)
        assert result == "step_completed"

        # Execute step 2
        exp2 = make_experience(
            action_taken="buy food",
            overall_satisfaction_before=42.0,
            overall_satisfaction_after=44.0,
        )
        result = ps.evaluate_step(exp2)
        assert result == "step_completed"

        # Execute step 3
        exp3 = make_experience(
            action_taken="eat food",
            overall_satisfaction_before=44.0,
            overall_satisfaction_after=55.0,
        )
        result = ps.evaluate_step(exp3)
        assert result == "step_completed"

        # Plan should be completed
        assert plan.status == "completed"
        stats = ps.get_planning_stats()
        assert stats["completed_plans"] == 1

    def test_plan_with_replan(self):
        """Test: create plan → get stuck → replan → complete."""
        # First LLM call: original plan
        # Second LLM call: replanned steps
        responses = [
            json.dumps({"steps": [
                {"description": "Walk to store", "action_hint": "walk to store", "expected_outcome": "at store", "estimated_cycles": 1},
            ]}),
            json.dumps({"steps": [
                {"description": "Order delivery", "action_hint": "order food", "expected_outcome": "food coming", "estimated_cycles": 1},
            ]}),
        ]
        llm = MagicMock()
        call_count = [0]

        def mock_invoke(messages):
            resp = MagicMock()
            resp.content = responses[min(call_count[0], len(responses) - 1)]
            call_count[0] += 1
            return resp

        llm.invoke.side_effect = mock_invoke

        ps = PlanningSystem(llm)

        # Create plan
        plan = ps.create_plan("Get food", 0, {}, {}, {}, [])
        assert plan is not None

        # Get stuck (exceed 2x estimate)
        plan.steps[0].actual_cycles = 3  # > 1 * 2.0

        new_plan = ps.check_for_replan(needs={"hunger": 15.0}, world_context={})
        assert new_plan is not None
        assert new_plan.steps[0].description == "Order delivery"
        assert plan.status == "replanned"
