"""Self-narrative and identity system for Jenbina.

Builds a stable-but-evolving identity from experiences and lessons:
- Self-concept statements
- Emergent values
- Life story timeline
- Identity crisis tracking when behavior contradicts self-concept
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import time


VALUE_KEYWORDS = {
    "connection": ["talk", "friend", "social", "community", "together", "relationship"],
    "growth": ["learn", "study", "improve", "practice", "explore", "build"],
    "stability": ["sleep", "rest", "routine", "plan", "safe", "security"],
    "compassion": ["help", "support", "care", "listen", "kind", "comfort"],
    "autonomy": ["decide", "choose", "independent", "self", "control"],
    "creativity": ["create", "write", "design", "music", "art", "imagine"],
}

OPPOSITE_SIGNALS = {
    "connection": ["isolate", "withdraw", "ignore everyone", "avoid people"],
    "growth": ["avoid learning", "give up", "stagnate", "procrastinate"],
    "stability": ["chaos", "impulsive", "risky", "gamble"],
    "compassion": ["insult", "hurt", "attack", "dismiss"],
}


@dataclass
class NarrativeEvent:
    timestamp: float
    action: str
    outcome_delta: float
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "outcome_delta": self.outcome_delta,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NarrativeEvent":
        return cls(
            timestamp=float(data.get("timestamp", time.time())),
            action=str(data.get("action", "unknown")),
            outcome_delta=float(data.get("outcome_delta", 0.0)),
            summary=str(data.get("summary", "")),
        )


class SelfNarrativeSystem:
    """Tracks identity and narrative continuity from experiences."""

    MAX_EVENTS = 120

    def __init__(self):
        self.values: Dict[str, float] = {k: 0.20 for k in VALUE_KEYWORDS}
        self.events: List[NarrativeEvent] = []
        self.self_concept: List[str] = [
            "I am someone who adapts and tries to take care of what matters.",
        ]
        self.life_story: str = "I am still figuring out who I am through my choices."
        self.identity_coherence: float = 0.70
        self.identity_crisis_level: float = 0.0
        self.last_crisis_reason: str = ""

    def integrate_experience(self, experience, lessons: List[Any] = None):
        """Update identity from a new experience and current lessons."""
        sat_delta = (
            float(experience.overall_satisfaction_after)
            - float(experience.overall_satisfaction_before)
        )
        action = str(experience.action_taken or "unknown")
        reasoning = str(experience.action_reasoning or "")

        summary = self._make_event_summary(action, sat_delta, reasoning)
        self.events.append(
            NarrativeEvent(
                timestamp=float(getattr(experience, "timestamp", time.time())),
                action=action,
                outcome_delta=sat_delta,
                summary=summary,
            )
        )
        if len(self.events) > self.MAX_EVENTS:
            self.events = self.events[-self.MAX_EVENTS:]

        self._update_values_from_action(action, sat_delta)
        self._update_values_from_lessons(lessons or [])
        self._detect_identity_contradiction(action, sat_delta)
        self._refresh_self_concept()
        self._refresh_life_story()

    def format_for_prompt(self) -> str:
        top_values = self.get_top_values(3)
        values_text = ", ".join(f"{k} ({v:.2f})" for k, v in top_values) or "none"
        concept_text = "; ".join(self.self_concept[:2])
        crisis_note = (
            f"Identity tension is elevated ({self.identity_crisis_level:.2f}) because {self.last_crisis_reason}."
            if self.identity_crisis_level >= 0.35 and self.last_crisis_reason
            else "Identity is currently coherent."
        )

        return (
            f"Self-concept: {concept_text}\n"
            f"Core values: {values_text}\n"
            f"Life story: {self.life_story}\n"
            f"Identity state: coherence={self.identity_coherence:.2f}, crisis={self.identity_crisis_level:.2f}. {crisis_note}"
        )

    def get_top_values(self, n: int = 3) -> List[tuple]:
        return sorted(self.values.items(), key=lambda kv: kv[1], reverse=True)[:n]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "self_concept": list(self.self_concept),
            "values": dict(self.values),
            "life_story": self.life_story,
            "identity_coherence": self.identity_coherence,
            "identity_crisis_level": self.identity_crisis_level,
            "last_crisis_reason": self.last_crisis_reason,
            "recent_events": [e.to_dict() for e in self.events[-5:]],
            "total_events": len(self.events),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "values": dict(self.values),
            "events": [e.to_dict() for e in self.events],
            "self_concept": list(self.self_concept),
            "life_story": self.life_story,
            "identity_coherence": self.identity_coherence,
            "identity_crisis_level": self.identity_crisis_level,
            "last_crisis_reason": self.last_crisis_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelfNarrativeSystem":
        system = cls()
        system.values.update(data.get("values", {}))
        system.events = [NarrativeEvent.from_dict(e) for e in data.get("events", [])]
        system.self_concept = data.get("self_concept", system.self_concept)
        system.life_story = data.get("life_story", system.life_story)
        system.identity_coherence = float(data.get("identity_coherence", system.identity_coherence))
        system.identity_crisis_level = float(data.get("identity_crisis_level", system.identity_crisis_level))
        system.last_crisis_reason = data.get("last_crisis_reason", "")
        return system

    def _make_event_summary(self, action: str, sat_delta: float, reasoning: str) -> str:
        direction = "improved" if sat_delta >= 0 else "worsened"
        return (
            f"I chose to {action}. It {direction} my overall satisfaction by {sat_delta:+.1f}. "
            f"I did it because {reasoning or 'it seemed right at the time'}."
        )

    def _update_values_from_action(self, action: str, sat_delta: float):
        lower = action.lower()
        reinforcement = 0.03 if sat_delta >= 0 else -0.02

        for value, keys in VALUE_KEYWORDS.items():
            hits = sum(1 for k in keys if k in lower)
            if hits:
                self.values[value] = self._clamp(self.values.get(value, 0.2) + reinforcement * hits)

    def _update_values_from_lessons(self, lessons: List[Any]):
        for lesson in lessons[-10:]:
            desc = str(getattr(lesson, "description", "") or lesson.get("description", "")).lower() if isinstance(lesson, dict) else str(getattr(lesson, "description", "")).lower()
            cat = str(getattr(lesson, "category", "") or lesson.get("category", "")).lower() if isinstance(lesson, dict) else str(getattr(lesson, "category", "")).lower()
            conf = float(getattr(lesson, "confidence", 0.5) if not isinstance(lesson, dict) else lesson.get("confidence", 0.5))

            bump = 0.01 * max(0.2, conf)
            if cat == "emotional_pattern":
                self.values["compassion"] = self._clamp(self.values["compassion"] + bump)
                self.values["connection"] = self._clamp(self.values["connection"] + bump)
            elif cat == "environmental":
                self.values["stability"] = self._clamp(self.values["stability"] + bump)
            elif cat == "action_outcome":
                self.values["growth"] = self._clamp(self.values["growth"] + bump)

            for value, keys in VALUE_KEYWORDS.items():
                if any(k in desc for k in keys):
                    self.values[value] = self._clamp(self.values[value] + bump)

    def _detect_identity_contradiction(self, action: str, sat_delta: float):
        dominant_value, dominant_score = self.get_top_values(1)[0]
        lower = action.lower()
        contradiction = False

        if dominant_score >= 0.45:
            contradiction = any(token in lower for token in OPPOSITE_SIGNALS.get(dominant_value, []))

        if contradiction and sat_delta < 0:
            self.identity_crisis_level = self._clamp(self.identity_crisis_level + 0.18)
            self.identity_coherence = self._clamp(self.identity_coherence - 0.12)
            self.last_crisis_reason = (
                f"my action ({action}) conflicted with my value of {dominant_value}"
            )
        else:
            self.identity_crisis_level = self._clamp(self.identity_crisis_level - 0.05)
            self.identity_coherence = self._clamp(self.identity_coherence + 0.03)
            if self.identity_crisis_level < 0.15:
                self.last_crisis_reason = ""

    def _refresh_self_concept(self):
        top = self.get_top_values(3)
        value_phrase = ", ".join(name for name, _ in top[:2])

        new_concept = [
            f"I am someone who values {value_phrase}.",
            "I become who I am through repeated choices and their consequences.",
        ]
        if self.identity_crisis_level >= 0.35:
            new_concept.append("Lately, I feel uncertain about whether my actions match who I believe I am.")

        self.self_concept = new_concept

    def _refresh_life_story(self):
        if not self.events:
            self.life_story = "I am still figuring out who I am through my choices."
            return

        recent = self.events[-5:]
        improves = sum(1 for e in recent if e.outcome_delta >= 0)
        declines = len(recent) - improves
        dominant_value, _ = self.get_top_values(1)[0]

        direction = "mostly improving" if improves >= declines else "full of setbacks"
        latest = recent[-1].summary
        self.life_story = (
            f"Recently my path has been {direction}. "
            f"My choices increasingly reflect {dominant_value}. "
            f"Most recent chapter: {latest}"
        )

    @staticmethod
    def _clamp(x: float) -> float:
        return max(0.0, min(1.0, x))
