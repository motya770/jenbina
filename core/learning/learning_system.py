"""Learning system for Jenbina — records experiences, extracts lessons, and applies them."""
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
class Experience:
    """Before/after snapshot around an action."""
    action_taken: str
    action_reasoning: str
    needs_before: Dict[str, float]
    needs_after: Dict[str, float]
    needs_delta: Dict[str, float]
    emotions_before: Dict[str, float]
    emotions_after: Dict[str, float]
    emotions_delta: Dict[str, float]
    world_context: Dict[str, str] = field(default_factory=dict)
    overall_satisfaction_before: float = 0.0
    overall_satisfaction_after: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "action_taken": self.action_taken,
            "action_reasoning": self.action_reasoning,
            "needs_before": self.needs_before,
            "needs_after": self.needs_after,
            "needs_delta": self.needs_delta,
            "emotions_before": self.emotions_before,
            "emotions_after": self.emotions_after,
            "emotions_delta": self.emotions_delta,
            "world_context": self.world_context,
            "overall_satisfaction_before": self.overall_satisfaction_before,
            "overall_satisfaction_after": self.overall_satisfaction_after,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Experience":
        return cls(**data)


@dataclass
class Lesson:
    """A learned pattern extracted from experiences."""
    description: str
    category: str  # "action_outcome" | "emotional_pattern" | "environmental"
    condition: str
    recommended_action: str
    confidence: float = 0.5
    times_confirmed: int = 0
    times_contradicted: int = 0
    last_confirmed: float = field(default_factory=time.time)

    def reinforce(self):
        self.times_confirmed += 1
        self.confidence = min(1.0, self.confidence + 0.1)
        self.last_confirmed = time.time()

    def contradict(self):
        self.times_contradicted += 1
        self.confidence = max(0.0, self.confidence - 0.15)

    def decay(self, hours: float):
        self.confidence = max(0.0, self.confidence - 0.01 * hours)

    def is_active(self) -> bool:
        return self.confidence > 0.15

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "category": self.category,
            "condition": self.condition,
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "times_confirmed": self.times_confirmed,
            "times_contradicted": self.times_contradicted,
            "last_confirmed": self.last_confirmed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Lesson":
        return cls(**data)


# ---------------------------------------------------------------------------
# LLM prompt for lesson extraction
# ---------------------------------------------------------------------------

LESSON_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["experiences_summary", "existing_lessons"],
    template="""You are analyzing a series of experiences to extract lessons and patterns.

Recent Experiences:
{experiences_summary}

Existing Lessons (avoid duplicates):
{existing_lessons}

Based on these experiences, extract up to 3 NEW lessons or patterns.
Each lesson should describe a cause-and-effect relationship observed in the experiences.

Return ONLY a JSON array of lesson objects. Each object must have:
- "description": a clear statement of the pattern (e.g. "Eating when hungry significantly improves mood")
- "category": one of "action_outcome", "emotional_pattern", or "environmental"
- "condition": when this lesson applies (e.g. "when hunger is below 40%")
- "recommended_action": what to do when the condition is met

Example: [{{"description": "Eating when hungry improves satisfaction", "category": "action_outcome", "condition": "hunger below 40%", "recommended_action": "eat food"}}]

Return the JSON array:""",
)


# ---------------------------------------------------------------------------
# LearningSystem
# ---------------------------------------------------------------------------

class LearningSystem:
    """Records experiences, extracts lessons via LLM, and formats them for prompts."""

    MAX_EXPERIENCES = 100
    LESSON_EXTRACTION_INTERVAL = 3

    def __init__(self, llm):
        self.llm = llm
        self.experiences: List[Experience] = []
        self.lessons: List[Lesson] = []
        self._experience_count_since_extraction = 0

    # -- recording ----------------------------------------------------------

    def record_experience(
        self,
        action_taken: str,
        action_reasoning: str,
        needs_before: Dict[str, float],
        needs_after: Dict[str, float],
        emotions_before: Dict[str, float],
        emotions_after: Dict[str, float],
        world_context: Optional[Dict[str, str]] = None,
        overall_satisfaction_before: float = 0.0,
        overall_satisfaction_after: float = 0.0,
    ) -> Experience:
        needs_delta = {k: needs_after.get(k, 0) - needs_before.get(k, 0) for k in needs_before}
        emotions_delta = {k: emotions_after.get(k, 0) - emotions_before.get(k, 0) for k in emotions_before}

        exp = Experience(
            action_taken=action_taken,
            action_reasoning=action_reasoning,
            needs_before=needs_before,
            needs_after=needs_after,
            needs_delta=needs_delta,
            emotions_before=emotions_before,
            emotions_after=emotions_after,
            emotions_delta=emotions_delta,
            world_context=world_context or {},
            overall_satisfaction_before=overall_satisfaction_before,
            overall_satisfaction_after=overall_satisfaction_after,
        )

        self.experiences.append(exp)
        if len(self.experiences) > self.MAX_EXPERIENCES:
            self.experiences = self.experiences[-self.MAX_EXPERIENCES:]

        self._experience_count_since_extraction += 1

        # Reinforce / contradict existing lessons with new experience
        self.reinforce_or_contradict_lessons(exp)

        # Extract new lessons periodically
        if self._experience_count_since_extraction >= self.LESSON_EXTRACTION_INTERVAL:
            self._experience_count_since_extraction = 0
            recent = self.experiences[-self.LESSON_EXTRACTION_INTERVAL:]
            self.extract_lessons(recent)

        return exp

    # -- lesson extraction --------------------------------------------------

    def extract_lessons(self, recent: List[Experience]):
        """Use LLM to analyse recent experiences and add new lessons (max 3)."""
        experiences_summary = "\n".join(
            f"- Action: {e.action_taken} | Reasoning: {e.action_reasoning} | "
            f"Needs Δ: {e.needs_delta} | Emotions Δ: {e.emotions_delta} | "
            f"Satisfaction: {e.overall_satisfaction_before:.1f}→{e.overall_satisfaction_after:.1f} | "
            f"Context: {e.world_context}"
            for e in recent
        )

        existing_lessons_str = "\n".join(
            f"- {l.description} (confidence: {l.confidence:.2f})"
            for l in self.lessons if l.is_active()
        ) or "None yet."

        prompt_text = LESSON_EXTRACTION_PROMPT.format(
            experiences_summary=experiences_summary,
            existing_lessons=existing_lessons_str,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)

            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)

            # fix_llm_json may return a dict wrapping the array
            if isinstance(parsed, dict):
                # Try common wrapper keys
                for key in ("lessons", "results", "data"):
                    if key in parsed and isinstance(parsed[key], list):
                        parsed = parsed[key]
                        break
                else:
                    # If it's a single lesson dict, wrap it
                    if "description" in parsed:
                        parsed = [parsed]
                    else:
                        return

            if not isinstance(parsed, list):
                return

            for item in parsed[:3]:
                if not isinstance(item, dict) or "description" not in item:
                    continue
                lesson = Lesson(
                    description=item.get("description", ""),
                    category=item.get("category", "action_outcome"),
                    condition=item.get("condition", ""),
                    recommended_action=item.get("recommended_action", ""),
                )
                self.lessons.append(lesson)
        except Exception:
            # Don't crash the simulation if extraction fails
            pass

    # -- reinforce / contradict ---------------------------------------------

    def reinforce_or_contradict_lessons(self, experience: Experience):
        """Check each active lesson against a new experience."""
        sat_delta = experience.overall_satisfaction_after - experience.overall_satisfaction_before
        action_lower = experience.action_taken.lower()

        for lesson in self.lessons:
            if not lesson.is_active():
                continue

            rec_lower = lesson.recommended_action.lower()
            # Check if this experience is related to the lesson's recommended action
            if rec_lower and (rec_lower in action_lower or action_lower in rec_lower):
                if sat_delta >= 0:
                    lesson.reinforce()
                else:
                    lesson.contradict()

    # -- formatting for prompts ---------------------------------------------

    def format_lessons_for_prompt(
        self,
        needs: Optional[Dict[str, float]] = None,
        emotions: Optional[Dict[str, float]] = None,
        world_context: Optional[Dict[str, str]] = None,
    ) -> str:
        active = [l for l in self.lessons if l.is_active()]
        if not active:
            return "No lessons learned yet."

        # Sort by confidence descending
        active.sort(key=lambda l: l.confidence, reverse=True)

        lines = []
        for l in active[:10]:
            lines.append(
                f"- [{l.category}] {l.description} "
                f"(confidence: {l.confidence:.2f}, confirmed: {l.times_confirmed}x) "
                f"→ {l.recommended_action}"
            )
        return "\n".join(lines)

    # -- decay --------------------------------------------------------------

    def decay_all_lessons(self, hours: float):
        """Decay all lessons and prune dead ones."""
        for lesson in self.lessons:
            lesson.decay(hours)
        self.lessons = [l for l in self.lessons if l.is_active()]

    # -- stats --------------------------------------------------------------

    def get_learning_stats(self) -> Dict[str, Any]:
        active = [l for l in self.lessons if l.is_active()]
        return {
            "total_experiences": len(self.experiences),
            "total_lessons": len(self.lessons),
            "active_lessons": len(active),
            "lessons": [l.to_dict() for l in active],
            "recent_experiences": [e.to_dict() for e in self.experiences[-5:]],
        }

    # -- serialisation ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "experiences": [e.to_dict() for e in self.experiences],
            "lessons": [l.to_dict() for l in self.lessons],
            "experience_count_since_extraction": self._experience_count_since_extraction,
        }

    @classmethod
    def from_dict(cls, data: dict, llm) -> "LearningSystem":
        system = cls(llm)
        system.experiences = [Experience.from_dict(e) for e in data.get("experiences", [])]
        system.lessons = [Lesson.from_dict(l) for l in data.get("lessons", [])]
        system._experience_count_since_extraction = data.get("experience_count_since_extraction", 0)
        return system
