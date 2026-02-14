"""Curiosity and exploration system for Jenbina.

Implements:
- Information-seeking drive
- "I wonder what happens if..." reasoning
- Novelty detection
- Boredom-driven exploration
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time


EXPLORATION_KEYWORDS = [
    "explore", "learn", "study", "read", "ask", "investigate", "observe",
    "try", "experiment", "discover", "visit", "research", "browse",
]


@dataclass
class NoveltyEvent:
    signature: str
    novelty_score: float
    description: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature": self.signature,
            "novelty_score": self.novelty_score,
            "description": self.description,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoveltyEvent":
        return cls(
            signature=data.get("signature", ""),
            novelty_score=float(data.get("novelty_score", 0.0)),
            description=data.get("description", ""),
            timestamp=float(data.get("timestamp", time.time())),
        )


class CuriositySystem:
    """Tracks curiosity, boredom, novelty, and exploration opportunities."""

    MAX_HISTORY = 60

    def __init__(self):
        self.curiosity_level: float = 0.35
        self.boredom_level: float = 0.20
        self.last_novelty_score: float = 0.0
        self.known_signatures: Dict[str, int] = {}
        self.novelty_events: List[NoveltyEvent] = []
        self.open_questions: List[str] = []
        self.recent_actions: List[str] = []
        self.suggested_explorations: List[str] = []

    def observe_cycle(
        self,
        needs: Dict[str, float],
        world_context: Dict[str, str],
        available_actions: Optional[List[str]] = None,
        recent_actions: Optional[List[str]] = None,
    ):
        """Update curiosity state from current world and repetition patterns."""
        signature = self._make_signature(world_context)
        novelty = self._detect_novelty(signature)
        self.last_novelty_score = novelty

        if recent_actions is not None:
            self.recent_actions = [a.lower() for a in recent_actions][-10:]

        self.boredom_level = self._compute_boredom(needs)
        repetition = self._repetition_score()

        # Curiosity rises from novelty and boredom/repetition pressure
        self.curiosity_level = self._clamp(
            0.25 + novelty * 0.55 + self.boredom_level * 0.35 + repetition * 0.15,
            0.0,
            1.0,
        )

        self.suggested_explorations = self._find_exploration_actions(available_actions or [])
        self._refresh_questions(world_context)

    def update_after_action(self, action: str):
        a = (action or "").lower().strip()
        if not a:
            return
        self.recent_actions.append(a)
        self.recent_actions = self.recent_actions[-10:]

    def should_explore(self) -> bool:
        return self.curiosity_level >= 0.58 or self.boredom_level >= 0.62

    def exploration_score(self, action: str) -> float:
        lower = (action or "").lower()
        base = 0.1
        if any(k in lower for k in EXPLORATION_KEYWORDS):
            base += 0.45
        if self.should_explore():
            base += 0.2
        if lower in self.recent_actions[-3:]:
            base -= 0.2
        return self._clamp(base, 0.0, 1.0)

    def format_for_prompt(self) -> str:
        novelty = f"{self.last_novelty_score:.2f}"
        curiosity = f"{self.curiosity_level:.2f}"
        boredom = f"{self.boredom_level:.2f}"
        explore_flag = "yes" if self.should_explore() else "no"

        questions = self.open_questions[-3:]
        q_text = "\n".join(f"- {q}" for q in questions) if questions else "- No strong questions right now."

        suggestions = self.suggested_explorations[:5]
        s_text = ", ".join(suggestions) if suggestions else "none"

        return (
            f"Curiosity state: level={curiosity}, boredom={boredom}, novelty={novelty}, should_explore={explore_flag}.\n"
            f"Open questions:\n{q_text}\n"
            f"Exploration candidates: {s_text}.\n"
            f"When appropriate, prefer information-seeking or novel actions over repetitive defaults."
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "curiosity_level": self.curiosity_level,
            "boredom_level": self.boredom_level,
            "last_novelty_score": self.last_novelty_score,
            "should_explore": self.should_explore(),
            "open_questions": list(self.open_questions[-5:]),
            "suggested_explorations": list(self.suggested_explorations[:5]),
            "recent_actions": list(self.recent_actions[-10:]),
            "recent_novelty_events": [e.to_dict() for e in self.novelty_events[-5:]],
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curiosity_level": self.curiosity_level,
            "boredom_level": self.boredom_level,
            "last_novelty_score": self.last_novelty_score,
            "known_signatures": dict(self.known_signatures),
            "novelty_events": [e.to_dict() for e in self.novelty_events],
            "open_questions": list(self.open_questions),
            "recent_actions": list(self.recent_actions),
            "suggested_explorations": list(self.suggested_explorations),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CuriositySystem":
        s = cls()
        s.curiosity_level = float(data.get("curiosity_level", 0.35))
        s.boredom_level = float(data.get("boredom_level", 0.20))
        s.last_novelty_score = float(data.get("last_novelty_score", 0.0))
        s.known_signatures = dict(data.get("known_signatures", {}))
        s.novelty_events = [NoveltyEvent.from_dict(e) for e in data.get("novelty_events", [])]
        s.open_questions = list(data.get("open_questions", []))
        s.recent_actions = list(data.get("recent_actions", []))
        s.suggested_explorations = list(data.get("suggested_explorations", []))
        return s

    def _make_signature(self, world: Dict[str, str]) -> str:
        loc = str(world.get("location", "unknown")).lower()
        time_of_day = str(world.get("time_of_day", "unknown")).lower()
        weather = str(world.get("weather", "unknown")).lower()
        return f"{loc}|{time_of_day}|{weather}"

    def _detect_novelty(self, signature: str) -> float:
        seen = self.known_signatures.get(signature, 0)
        self.known_signatures[signature] = seen + 1

        novelty = 1.0 if seen == 0 else 1.0 / (seen + 1)
        if novelty > 0.45:
            event = NoveltyEvent(
                signature=signature,
                novelty_score=novelty,
                description=f"New context noticed: {signature}",
            )
            self.novelty_events.append(event)
            self.novelty_events = self.novelty_events[-self.MAX_HISTORY:]
        return novelty

    def _compute_boredom(self, needs: Dict[str, float]) -> float:
        if not needs:
            return self.boredom_level

        avg_need = sum(needs.values()) / max(1, len(needs))
        low_pressure = self._clamp((avg_need - 65.0) / 35.0, 0.0, 1.0)
        repetition = self._repetition_score()

        return self._clamp(0.15 + low_pressure * 0.55 + repetition * 0.35, 0.0, 1.0)

    def _repetition_score(self) -> float:
        if len(self.recent_actions) < 4:
            return 0.0
        window = self.recent_actions[-6:]
        unique = len(set(window))
        if unique <= 1:
            return 1.0
        return self._clamp((len(window) - unique) / len(window), 0.0, 1.0)

    def _find_exploration_actions(self, actions: List[str]) -> List[str]:
        matches = []
        for action in actions:
            lower = action.lower()
            if any(k in lower for k in EXPLORATION_KEYWORDS):
                matches.append(action)

        # If nothing explicitly exploratory, encourage novelty by switching action
        if not matches and actions and self.should_explore():
            unseen = [a for a in actions if a.lower() not in self.recent_actions[-5:]]
            matches.extend(unseen[:3])

        return matches[:5]

    def _refresh_questions(self, world: Dict[str, str]):
        questions = []
        if self.last_novelty_score > 0.45:
            loc = world.get("location", "this place")
            weather = world.get("weather", "these conditions")
            questions.append(f"I wonder what happens in {loc} under {weather}.")

        if self.boredom_level > 0.6:
            questions.append("I wonder what happens if I try something different right now.")

        if self.suggested_explorations:
            questions.append(f"I wonder what I would learn by trying '{self.suggested_explorations[0]}'.")

        # Keep stable memory of questions without unbounded growth
        for q in questions:
            if q not in self.open_questions:
                self.open_questions.append(q)
        self.open_questions = self.open_questions[-12:]

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))
