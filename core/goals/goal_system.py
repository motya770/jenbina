"""Goal system for Jenbina — generates and tracks short/mid/long-term goals."""
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

DECAY_RATES = {
    "short_term": 0.03,
    "mid_term": 0.008,
    "long_term": 0.002,
}

ABANDONMENT_THRESHOLDS = {
    "short_term": 0.1,
    "mid_term": 0.05,
    "long_term": 0.05,
}


@dataclass
class Goal:
    """A goal Jenbina is pursuing."""
    description: str
    horizon: str  # "short_term" | "mid_term" | "long_term"
    source_needs: List[str]
    recommended_actions: List[str]
    source_lessons: List[str] = field(default_factory=list)
    progress: float = 0.0
    confidence: float = 0.7
    status: str = "active"  # "active" | "completed" | "abandoned"
    created_at: float = field(default_factory=time.time)
    last_progressed: float = field(default_factory=time.time)
    times_advanced: int = 0
    times_regressed: int = 0

    def advance(self, amount: float):
        self.progress = min(1.0, self.progress + amount)
        self.times_advanced += 1
        self.last_progressed = time.time()

    def regress(self, amount: float):
        self.progress = max(0.0, self.progress - amount)
        self.times_regressed += 1

    def decay(self, hours: float):
        rate = DECAY_RATES.get(self.horizon, 0.01)
        self.confidence = max(0.0, self.confidence - rate * hours)

    def is_active(self) -> bool:
        if self.status != "active":
            return False
        threshold = ABANDONMENT_THRESHOLDS.get(self.horizon, 0.05)
        return self.confidence > threshold

    def complete(self):
        self.status = "completed"

    def abandon(self):
        self.status = "abandoned"

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "horizon": self.horizon,
            "source_needs": self.source_needs,
            "source_lessons": self.source_lessons,
            "recommended_actions": self.recommended_actions,
            "progress": self.progress,
            "confidence": self.confidence,
            "status": self.status,
            "created_at": self.created_at,
            "last_progressed": self.last_progressed,
            "times_advanced": self.times_advanced,
            "times_regressed": self.times_regressed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        return cls(**data)


# ---------------------------------------------------------------------------
# LLM prompts
# ---------------------------------------------------------------------------

GOAL_GENERATION_PROMPT = PromptTemplate(
    input_variables=["needs_summary", "emotions_summary", "personality_traits", "learned_lessons", "existing_goals"],
    template="""You are helping a virtual person set meaningful goals based on their current state.

Current Needs (name: satisfaction%):
{needs_summary}

Current Emotions:
{emotions_summary}

Personality Traits:
{personality_traits}

Lessons Learned:
{learned_lessons}

Existing Active Goals (avoid duplicates):
{existing_goals}

Generate up to 3 NEW goals across different time horizons that this person should pursue.
Consider which needs are lowest and most pressing, what lessons have been learned, and how personality shapes aspirations.

Short-term goals: immediate actions (1-3 iterations), driven by urgent needs.
Mid-term goals: sustained effort (10-20 iterations), driven by social/esteem needs.
Long-term goals: deep aspirations (50+ iterations), driven by self-actualization/meaning.

Return ONLY a JSON array. Each object must have:
- "description": clear goal statement
- "horizon": one of "short_term", "mid_term", "long_term"
- "source_needs": list of need names motivating this goal
- "recommended_actions": list of 2-3 actions that advance this goal

Example: [{{"description": "Find a cozy place to eat", "horizon": "short_term", "source_needs": ["hunger"], "recommended_actions": ["go to restaurant", "find food"]}}]

Return the JSON array:""",
)

MILESTONE_CHECK_PROMPT = PromptTemplate(
    input_variables=["goal_description", "goal_horizon", "recent_experiences", "source_needs_status"],
    template="""A virtual person has been pursuing a goal. Determine if it has been meaningfully achieved.

Goal: {goal_description}
Horizon: {goal_horizon}

Recent Related Experiences:
{recent_experiences}

Current Status of Source Needs:
{source_needs_status}

Has this goal been meaningfully achieved based on the experiences and current need satisfaction?
Consider whether enough progress has been made relative to the goal's scope.

Return ONLY a JSON object:
- "achieved": true or false
- "explanation": brief reason

Return the JSON:""",
)


# ---------------------------------------------------------------------------
# GoalSystem
# ---------------------------------------------------------------------------

class GoalSystem:
    """Generates, tracks, and manages goals across time horizons."""

    MAX_GOALS = 10
    GENERATION_INTERVAL = 5
    MILESTONE_CHECK_THRESHOLD = 0.85

    def __init__(self, llm):
        self.llm = llm
        self.goals: List[Goal] = []
        self._experience_count_since_generation = 0

    # -- goal generation ----------------------------------------------------

    def generate_goals(
        self,
        needs: Dict[str, float],
        emotions: Dict[str, float],
        personality_traits: Dict[str, float],
        lessons: List[dict],
    ):
        """Use LLM to propose new goals based on current state."""
        active_count = len([g for g in self.goals if g.is_active()])
        if active_count >= self.MAX_GOALS:
            return

        needs_summary = "\n".join(f"- {k}: {v:.1f}%" for k, v in needs.items())
        emotions_summary = "\n".join(f"- {k}: {v}" for k, v in emotions.items())
        personality_str = "\n".join(f"- {k}: {v}" for k, v in personality_traits.items()) or "No specific traits defined."
        lessons_str = "\n".join(f"- {l.get('description', '')} (confidence: {l.get('confidence', 0):.2f})" for l in lessons) or "None yet."
        existing_str = "\n".join(f"- [{g.horizon}] {g.description} (progress: {g.progress:.0%})" for g in self.goals if g.is_active()) or "None yet."

        prompt_text = GOAL_GENERATION_PROMPT.format(
            needs_summary=needs_summary,
            emotions_summary=emotions_summary,
            personality_traits=personality_str,
            learned_lessons=lessons_str,
            existing_goals=existing_str,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)

            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)

            if isinstance(parsed, dict):
                for key in ("goals", "results", "data"):
                    if key in parsed and isinstance(parsed[key], list):
                        parsed = parsed[key]
                        break
                else:
                    if "description" in parsed:
                        parsed = [parsed]
                    else:
                        return

            if not isinstance(parsed, list):
                return

            slots_available = self.MAX_GOALS - active_count
            for item in parsed[:min(3, slots_available)]:
                if not isinstance(item, dict) or "description" not in item:
                    continue
                horizon = item.get("horizon", "short_term")
                if horizon not in DECAY_RATES:
                    horizon = "short_term"
                goal = Goal(
                    description=item["description"],
                    horizon=horizon,
                    source_needs=item.get("source_needs", []),
                    recommended_actions=item.get("recommended_actions", []),
                )
                self.goals.append(goal)
        except Exception:
            pass

    # -- progress tracking --------------------------------------------------

    def update_progress(self, experience) -> List[Goal]:
        """Update goal progress based on a new experience. Returns goals that advanced."""
        advanced = []
        action_lower = experience.action_taken.lower()

        for goal in self.goals:
            if not goal.is_active():
                continue

            # Check if action is related to goal's recommended actions
            action_relevant = any(
                rec.lower() in action_lower or action_lower in rec.lower()
                for rec in goal.recommended_actions
            )
            if not action_relevant:
                continue

            # Calculate progress from source need deltas
            relevant_deltas = [
                experience.needs_delta.get(need, 0.0)
                for need in goal.source_needs
                if need in experience.needs_delta
            ]

            if not relevant_deltas:
                continue

            avg_delta = sum(relevant_deltas) / len(relevant_deltas)

            if avg_delta > 0:
                # Scale: +10 satisfaction = +0.1 progress
                goal.advance(avg_delta / 100.0)
                advanced.append(goal)
            elif avg_delta < 0:
                goal.regress(abs(avg_delta) / 100.0)

        self._experience_count_since_generation += 1

        # Check milestones for any goal near completion
        for goal in self.goals:
            if goal.is_active() and goal.progress >= self.MILESTONE_CHECK_THRESHOLD:
                self.check_milestone(goal)

        return advanced

    def check_milestone(self, goal: Goal):
        """Ask LLM whether a goal has been achieved."""
        recent = []
        from ..learning.learning_system import Experience
        # We don't have direct access to experiences here, so milestone
        # checking is called from the simulation with experience context.
        # This method can be called directly with _last_experiences set.
        experiences = getattr(self, "_last_experiences", [])

        related = [
            e for e in experiences
            if any(
                rec.lower() in e.action_taken.lower() or e.action_taken.lower() in rec.lower()
                for rec in goal.recommended_actions
            )
        ][-5:]

        if not related:
            return

        exp_summary = "\n".join(
            f"- Action: {e.action_taken} | Needs Δ: {e.needs_delta} | "
            f"Satisfaction: {e.overall_satisfaction_before:.1f}→{e.overall_satisfaction_after:.1f}"
            for e in related
        )

        needs_status = "\n".join(
            f"- {need}: {related[-1].needs_after.get(need, 'unknown')}"
            for need in goal.source_needs
        ) if related else "Unknown"

        prompt_text = MILESTONE_CHECK_PROMPT.format(
            goal_description=goal.description,
            goal_horizon=goal.horizon,
            recent_experiences=exp_summary,
            source_needs_status=needs_status,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)
            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)

            if isinstance(parsed, dict) and parsed.get("achieved", False):
                goal.complete()
        except Exception:
            pass

    def set_experiences(self, experiences):
        """Set experience list for milestone checking."""
        self._last_experiences = experiences

    # -- should we generate new goals? --------------------------------------

    def should_generate(self) -> bool:
        return self._experience_count_since_generation >= self.GENERATION_INTERVAL

    def reset_generation_counter(self):
        self._experience_count_since_generation = 0

    # -- decay --------------------------------------------------------------

    def decay_all_goals(self, hours: float):
        """Decay confidence and abandon dead goals."""
        for goal in self.goals:
            if goal.status == "active":
                goal.decay(hours)
                if not goal.is_active():
                    goal.abandon()

    # -- formatting for prompts ---------------------------------------------

    def format_goals_for_prompt(self) -> str:
        active = [g for g in self.goals if g.is_active()]
        if not active:
            return "No goals set yet."

        # Sort: short_term first, then by progress descending
        horizon_order = {"short_term": 0, "mid_term": 1, "long_term": 2}
        active.sort(key=lambda g: (horizon_order.get(g.horizon, 1), -g.progress))

        lines = []
        for g in active:
            actions_str = ", ".join(g.recommended_actions[:3])
            lines.append(
                f"- [{g.horizon}] {g.description} "
                f"(progress: {g.progress:.0%}, confidence: {g.confidence:.0%}) "
                f"→ {actions_str}"
            )
        return "\n".join(lines)

    # -- stats --------------------------------------------------------------

    def get_goal_stats(self) -> Dict[str, Any]:
        active = [g for g in self.goals if g.is_active()]
        completed = [g for g in self.goals if g.status == "completed"]
        abandoned = [g for g in self.goals if g.status == "abandoned"]
        return {
            "total_goals": len(self.goals),
            "active_goals": len(active),
            "completed_goals": len(completed),
            "abandoned_goals": len(abandoned),
            "goals": [g.to_dict() for g in active],
            "completed": [g.to_dict() for g in completed[-5:]],
        }

    # -- serialization ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "goals": [g.to_dict() for g in self.goals],
            "experience_count_since_generation": self._experience_count_since_generation,
        }

    @classmethod
    def from_dict(cls, data: dict, llm) -> "GoalSystem":
        system = cls(llm)
        system.goals = [Goal.from_dict(g) for g in data.get("goals", [])]
        system._experience_count_since_generation = data.get("experience_count_since_generation", 0)
        return system
