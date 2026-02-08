"""Planning system for Jenbina — decomposes goals into multi-step plans."""
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..fix_llm_json import fix_llm_json


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PlanStep:
    """A single step in a plan."""
    description: str
    action_hint: str
    expected_outcome: str
    estimated_cycles: int = 2
    actual_cycles: int = 0
    status: str = "pending"  # "pending" | "active" | "completed" | "failed"
    failure_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "action_hint": self.action_hint,
            "expected_outcome": self.expected_outcome,
            "estimated_cycles": self.estimated_cycles,
            "actual_cycles": self.actual_cycles,
            "status": self.status,
            "failure_reason": self.failure_reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlanStep":
        return cls(**data)


@dataclass
class Plan:
    """An ordered sequence of steps to achieve a goal."""
    goal_description: str
    goal_id: int
    steps: List[PlanStep] = field(default_factory=list)
    current_step_index: int = 0
    status: str = "active"  # "active" | "completed" | "failed" | "replanned"
    times_replanned: int = 0
    created_at: float = field(default_factory=time.time)
    consecutive_overrides: int = 0  # times action decision ignored the plan step

    MAX_REPLANS = 3

    def get_current_step(self) -> Optional[PlanStep]:
        if self.status != "active":
            return None
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self):
        """Mark current step completed and move to next."""
        step = self.get_current_step()
        if step:
            step.status = "completed"
        self.current_step_index += 1
        self.consecutive_overrides = 0
        if self.current_step_index >= len(self.steps):
            self.status = "completed"
        else:
            self.steps[self.current_step_index].status = "active"

    def fail_current_step(self, reason: str):
        step = self.get_current_step()
        if step:
            step.status = "failed"
            step.failure_reason = reason

    def get_completed_steps(self) -> List[PlanStep]:
        return [s for s in self.steps if s.status == "completed"]

    def to_dict(self) -> dict:
        return {
            "goal_description": self.goal_description,
            "goal_id": self.goal_id,
            "steps": [s.to_dict() for s in self.steps],
            "current_step_index": self.current_step_index,
            "status": self.status,
            "times_replanned": self.times_replanned,
            "created_at": self.created_at,
            "consecutive_overrides": self.consecutive_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        plan = cls(
            goal_description=data["goal_description"],
            goal_id=data["goal_id"],
            current_step_index=data.get("current_step_index", 0),
            status=data.get("status", "active"),
            times_replanned=data.get("times_replanned", 0),
            created_at=data.get("created_at", time.time()),
            consecutive_overrides=data.get("consecutive_overrides", 0),
        )
        plan.steps = [PlanStep.from_dict(s) for s in data.get("steps", [])]
        return plan


# ---------------------------------------------------------------------------
# LLM prompts
# ---------------------------------------------------------------------------

PLAN_GENERATION_PROMPT = PromptTemplate(
    input_variables=["goal_description", "needs_summary", "emotions_summary", "world_context", "learned_lessons"],
    template="""You are helping a virtual person create a step-by-step plan to achieve a goal.

Goal: {goal_description}

Current Needs (name: satisfaction%):
{needs_summary}

Current Emotions:
{emotions_summary}

World Context:
{world_context}

Lessons Learned:
{learned_lessons}

Decompose this goal into 2-6 sequential steps. Each step should be a concrete action.
Think about prerequisites: what needs to happen first before later steps can succeed.
For example, "eat food" might require "go to store" which requires "earn money" which requires "find work".

Return ONLY a JSON object with a "steps" array. Each step must have:
- "description": what to do
- "action_hint": a short action phrase the person should take
- "expected_outcome": what success looks like
- "estimated_cycles": how many simulation cycles this step should take (1-5)

Example:
{{"steps": [{{"description": "Go to the grocery store", "action_hint": "walk to grocery store", "expected_outcome": "be at the store", "estimated_cycles": 1}}]}}

Return the JSON:""",
)

REPLAN_PROMPT = PromptTemplate(
    input_variables=["goal_description", "completed_steps", "failed_step", "failure_reason", "needs_summary", "world_context"],
    template="""A virtual person's plan hit an obstacle. Help them replan from their current state.

Original Goal: {goal_description}

Steps Completed So Far:
{completed_steps}

Failed Step: {failed_step}
Failure Reason: {failure_reason}

Current Needs (name: satisfaction%):
{needs_summary}

World Context:
{world_context}

Generate a NEW plan starting from the current state (after completed steps).
The new plan should work around the obstacle that caused the failure.
Use 2-6 steps.

Return ONLY a JSON object with a "steps" array. Each step must have:
- "description": what to do
- "action_hint": a short action phrase
- "expected_outcome": what success looks like
- "estimated_cycles": how many cycles (1-5)

Return the JSON:""",
)


# ---------------------------------------------------------------------------
# PlanningSystem
# ---------------------------------------------------------------------------

class PlanningSystem:
    """Decomposes goals into plans and tracks execution across cycles."""

    MAX_ACTIVE_PLANS = 3
    STUCK_MULTIPLIER = 2.0
    OVERRIDE_THRESHOLD = 3

    def __init__(self, llm):
        self.llm = llm
        self.plans: List[Plan] = []

    # -- plan creation ------------------------------------------------------

    def create_plan(
        self,
        goal_description: str,
        goal_id: int,
        needs: Dict[str, float],
        emotions: Dict[str, float],
        world_context: Dict[str, str],
        lessons: List[dict],
    ) -> Optional[Plan]:
        """Use LLM to decompose a goal into steps."""
        # Don't create if goal already has a plan
        if self.get_plan_for_goal(goal_id) is not None:
            return None

        # Don't exceed max active plans
        active_count = len([p for p in self.plans if p.status == "active"])
        if active_count >= self.MAX_ACTIVE_PLANS:
            return None

        needs_summary = "\n".join(f"- {k}: {v:.1f}%" for k, v in needs.items())
        emotions_summary = "\n".join(f"- {k}: {v}" for k, v in emotions.items())
        world_str = "\n".join(f"- {k}: {v}" for k, v in world_context.items()) or "No context."
        lessons_str = "\n".join(
            f"- {l.get('description', '')} (confidence: {l.get('confidence', 0):.2f})"
            for l in lessons
        ) or "None yet."

        prompt_text = PLAN_GENERATION_PROMPT.format(
            goal_description=goal_description,
            needs_summary=needs_summary,
            emotions_summary=emotions_summary,
            world_context=world_str,
            learned_lessons=lessons_str,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)
            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)

            steps_data = self._extract_steps(parsed)
            if not steps_data:
                return None

            plan = Plan(goal_description=goal_description, goal_id=goal_id)
            for item in steps_data[:6]:
                if not isinstance(item, dict) or "description" not in item:
                    continue
                step = PlanStep(
                    description=item["description"],
                    action_hint=item.get("action_hint", item["description"]),
                    expected_outcome=item.get("expected_outcome", ""),
                    estimated_cycles=max(1, min(5, int(item.get("estimated_cycles", 2)))),
                )
                plan.steps.append(step)

            if not plan.steps:
                return None

            # Activate first step
            plan.steps[0].status = "active"
            self.plans.append(plan)
            return plan
        except Exception:
            return None

    def _extract_steps(self, parsed) -> Optional[list]:
        """Extract steps array from various LLM response formats."""
        if isinstance(parsed, dict):
            for key in ("steps", "plan", "results"):
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]
            return None
        if isinstance(parsed, list):
            return parsed
        return None

    # -- current step -------------------------------------------------------

    def get_current_step(self) -> Optional[tuple]:
        """Return (plan, step) for the highest-priority active plan."""
        horizon_order = {"short_term": 0, "mid_term": 1, "long_term": 2}
        active_plans = [p for p in self.plans if p.status == "active"]
        if not active_plans:
            return None

        # Sort by goal horizon if available, otherwise by creation time
        active_plans.sort(key=lambda p: p.created_at)

        for plan in active_plans:
            step = plan.get_current_step()
            if step:
                return (plan, step)
        return None

    # -- step evaluation ----------------------------------------------------

    def evaluate_step(self, experience) -> Optional[str]:
        """Evaluate current step after a cycle. Returns status string or None."""
        result = self.get_current_step()
        if result is None:
            return None

        plan, step = result
        action_lower = experience.action_taken.lower()
        hint_lower = step.action_hint.lower()

        # Check if the action decision followed the plan
        action_matched = hint_lower in action_lower or action_lower in hint_lower

        step.actual_cycles += 1

        if action_matched:
            plan.consecutive_overrides = 0
            sat_delta = experience.overall_satisfaction_after - experience.overall_satisfaction_before

            if sat_delta >= 0:
                # Step succeeded — advance
                plan.advance()
                return "step_completed"
            else:
                # Action matched but outcome was negative — keep trying
                return "step_in_progress"
        else:
            # Action decision overrode the plan (urgent need?)
            plan.consecutive_overrides += 1
            return "step_overridden"

    def check_for_replan(
        self,
        needs: Dict[str, float],
        world_context: Dict[str, str],
    ) -> Optional[Plan]:
        """Check if any active plan needs replanning. Returns replanned Plan or None."""
        result = self.get_current_step()
        if result is None:
            return None

        plan, step = result
        stuck = (
            step.estimated_cycles > 0
            and step.actual_cycles > step.estimated_cycles * self.STUCK_MULTIPLIER
        )
        overridden = plan.consecutive_overrides >= self.OVERRIDE_THRESHOLD

        if stuck or overridden:
            reason = "stuck — exceeded time estimate" if stuck else "repeatedly overridden by urgent needs"
            return self.replan(plan, reason, needs, world_context)

        return None

    # -- replanning ---------------------------------------------------------

    def replan(
        self,
        plan: Plan,
        failure_reason: str,
        needs: Dict[str, float],
        world_context: Dict[str, str],
    ) -> Optional[Plan]:
        """Generate a new plan from current state."""
        if plan.times_replanned >= Plan.MAX_REPLANS:
            plan.fail_current_step(f"max replans reached: {failure_reason}")
            plan.status = "failed"
            return None

        plan.fail_current_step(failure_reason)

        completed_str = "\n".join(
            f"- {s.description} (completed)" for s in plan.get_completed_steps()
        ) or "None yet."

        failed_step_desc = ""
        for s in plan.steps:
            if s.status == "failed":
                failed_step_desc = s.description
                break

        needs_summary = "\n".join(f"- {k}: {v:.1f}%" for k, v in needs.items())
        world_str = "\n".join(f"- {k}: {v}" for k, v in world_context.items()) or "No context."

        prompt_text = REPLAN_PROMPT.format(
            goal_description=plan.goal_description,
            completed_steps=completed_str,
            failed_step=failed_step_desc,
            failure_reason=failure_reason,
            needs_summary=needs_summary,
            world_context=world_str,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)
            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)

            steps_data = self._extract_steps(parsed)
            if not steps_data:
                plan.status = "failed"
                return None

            # Replace remaining steps with new ones
            plan.status = "replanned"

            new_plan = Plan(
                goal_description=plan.goal_description,
                goal_id=plan.goal_id,
                times_replanned=plan.times_replanned + 1,
            )
            for item in steps_data[:6]:
                if not isinstance(item, dict) or "description" not in item:
                    continue
                step = PlanStep(
                    description=item["description"],
                    action_hint=item.get("action_hint", item["description"]),
                    expected_outcome=item.get("expected_outcome", ""),
                    estimated_cycles=max(1, min(5, int(item.get("estimated_cycles", 2)))),
                )
                new_plan.steps.append(step)

            if not new_plan.steps:
                plan.status = "failed"
                return None

            new_plan.steps[0].status = "active"
            self.plans.append(new_plan)
            return new_plan
        except Exception:
            plan.status = "failed"
            return None

    # -- formatting for prompt ----------------------------------------------

    def format_plan_for_prompt(self) -> str:
        result = self.get_current_step()
        if result is None:
            return "No active plan."

        plan, step = result
        total_steps = len(plan.steps)
        step_num = plan.current_step_index + 1
        return (
            f"Current Plan Step (follow this unless urgent needs override):\n"
            f"Goal: \"{plan.goal_description}\"\n"
            f"Step {step_num} of {total_steps}: \"{step.description}\"\n"
            f"Suggested action: {step.action_hint}"
        )

    # -- query helpers ------------------------------------------------------

    def get_plan_for_goal(self, goal_id: int) -> Optional[Plan]:
        """Get active plan for a given goal id."""
        for plan in self.plans:
            if plan.goal_id == goal_id and plan.status == "active":
                return plan
        return None

    def get_active_plans(self) -> List[Plan]:
        return [p for p in self.plans if p.status == "active"]

    # -- stats --------------------------------------------------------------

    def get_planning_stats(self) -> Dict[str, Any]:
        active = [p for p in self.plans if p.status == "active"]
        completed = [p for p in self.plans if p.status == "completed"]
        failed = [p for p in self.plans if p.status == "failed"]
        return {
            "total_plans": len(self.plans),
            "active_plans": len(active),
            "completed_plans": len(completed),
            "failed_plans": len(failed),
            "plans": [p.to_dict() for p in active],
            "completed": [p.to_dict() for p in completed[-5:]],
        }

    # -- serialization ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "plans": [p.to_dict() for p in self.plans],
        }

    @classmethod
    def from_dict(cls, data: dict, llm) -> "PlanningSystem":
        system = cls(llm)
        system.plans = [Plan.from_dict(p) for p in data.get("plans", [])]
        return system
