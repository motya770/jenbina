"""Working memory system for Jenbina — short-term buffer of current thoughts."""
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


# ---------------------------------------------------------------------------
# Salience weights by Maslow level
# ---------------------------------------------------------------------------

NEED_LEVEL_WEIGHTS = {
    1: 1.0,   # Physiological
    2: 0.8,   # Safety
    3: 0.6,   # Social
    4: 0.4,   # Esteem
    5: 0.2,   # Self-actualization
}

PLAN_STEP_SALIENCE = 0.7
EXPERIENCE_BASE_SALIENCE = 0.6
EXPERIENCE_DECAY_CYCLES = 3
ENVIRONMENT_SALIENCE = 0.5
CONTEXT_SWITCH_PENALTY = 5.0


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class WorkingMemoryItem:
    """An item currently in working memory."""
    content: str
    source: str  # "need" | "emotion" | "plan_step" | "goal" | "experience" | "environment"
    salience: float = 0.0
    entered_at: float = field(default_factory=time.time)
    source_id: str = ""

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "source": self.source,
            "salience": self.salience,
            "entered_at": self.entered_at,
            "source_id": self.source_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkingMemoryItem":
        return cls(**data)


# ---------------------------------------------------------------------------
# WorkingMemorySystem
# ---------------------------------------------------------------------------

class WorkingMemorySystem:
    """Maintains a salience-ranked buffer of what Jenbina is currently thinking about."""

    def __init__(self):
        self.buffer: List[WorkingMemoryItem] = []
        self.focus: float = 100.0
        self.last_top_source: str = ""
        self.context_switches: int = 0
        self._cycles_since_experience: int = 0

    # -- main update --------------------------------------------------------

    def update(
        self,
        needs: Dict[str, Any],
        emotions: Dict[str, float],
        active_plan_step: Optional[Dict[str, str]] = None,
        active_goals: Optional[List[Dict[str, Any]]] = None,
        recent_experience: Optional[Dict[str, str]] = None,
        world_context: Optional[Dict[str, str]] = None,
        sleep_satisfaction: float = 100.0,
    ):
        """Recalculate working memory from current state. Called once per cycle."""
        # Calculate focus from sleep
        self.focus = max(30.0, min(100.0, sleep_satisfaction * 0.8 + 20.0))

        # Generate candidate items
        candidates: List[WorkingMemoryItem] = []

        # Needs
        candidates.extend(self._score_needs(needs))

        # Emotions
        candidates.extend(self._score_emotions(emotions))

        # Active plan step
        if active_plan_step:
            candidates.append(WorkingMemoryItem(
                content=f"Plan step: {active_plan_step.get('description', 'unknown')}",
                source="plan_step",
                salience=PLAN_STEP_SALIENCE,
                source_id=active_plan_step.get("action_hint", ""),
            ))

        # Goals
        if active_goals:
            candidates.extend(self._score_goals(active_goals))

        # Recent experience
        if recent_experience:
            self._cycles_since_experience = 0
        else:
            self._cycles_since_experience += 1

        if self._cycles_since_experience < EXPERIENCE_DECAY_CYCLES and recent_experience:
            decay_factor = 1.0 - (self._cycles_since_experience / EXPERIENCE_DECAY_CYCLES)
            candidates.append(WorkingMemoryItem(
                content=f"Recent: {recent_experience.get('action', 'unknown action')}",
                source="experience",
                salience=EXPERIENCE_BASE_SALIENCE * decay_factor,
                source_id="last_experience",
            ))

        # Environment
        if world_context:
            candidates.extend(self._score_environment(world_context))

        # Apply focus noise (low focus = more noise)
        if self.focus < 100.0:
            noise_range = (100.0 - self.focus) / 1000.0  # max ±0.07 at focus=30
            for item in candidates:
                item.salience = max(0.0, min(1.0, item.salience + random.uniform(-noise_range, noise_range)))

        # Sort by salience, take top N
        candidates.sort(key=lambda x: x.salience, reverse=True)
        capacity = self._get_capacity()
        self.buffer = candidates[:capacity]

        # Detect context switch
        if self.buffer:
            new_top_source = self.buffer[0].source
            if self.last_top_source and new_top_source != self.last_top_source:
                self.focus = max(30.0, self.focus - CONTEXT_SWITCH_PENALTY)
                self.context_switches += 1
            self.last_top_source = new_top_source

    # -- salience scoring ---------------------------------------------------

    def _score_needs(self, needs: Dict[str, Any]) -> List[WorkingMemoryItem]:
        items = []
        for name, need_data in needs.items():
            if isinstance(need_data, dict):
                satisfaction = need_data.get("satisfaction", 100.0)
                level = need_data.get("level", 1)
            else:
                satisfaction = float(need_data)
                level = 1
            weight = NEED_LEVEL_WEIGHTS.get(level, 0.5)
            salience = (100.0 - satisfaction) / 100.0 * weight
            if salience > 0.1:
                urgency = "critically low" if satisfaction < 20 else "low" if satisfaction < 50 else "moderate"
                items.append(WorkingMemoryItem(
                    content=f"{name} is {urgency} ({satisfaction:.0f}%)",
                    source="need",
                    salience=salience,
                    source_id=name,
                ))
        return items

    def _score_emotions(self, emotions: Dict[str, float]) -> List[WorkingMemoryItem]:
        items = []
        # Sort by intensity, take top 2
        sorted_emotions = sorted(emotions.items(), key=lambda x: abs(x[1]), reverse=True)
        for name, intensity in sorted_emotions[:2]:
            salience = abs(intensity) / 100.0
            if salience > 0.1:
                items.append(WorkingMemoryItem(
                    content=f"Feeling {name} ({intensity:.0f})",
                    source="emotion",
                    salience=salience,
                    source_id=name,
                ))
        return items

    def _score_goals(self, active_goals: List[Dict[str, Any]]) -> List[WorkingMemoryItem]:
        items = []
        for goal in active_goals[:5]:
            progress = goal.get("progress", 0.0)
            confidence = goal.get("confidence", 0.5)
            salience = (1.0 - progress) * confidence * 0.5
            if salience > 0.05:
                items.append(WorkingMemoryItem(
                    content=f"Goal: {goal.get('description', 'unknown')} ({progress:.0%} done)",
                    source="goal",
                    salience=salience,
                    source_id=str(goal.get("description", "")),
                ))
        return items

    def _score_environment(self, world_context: Dict[str, str]) -> List[WorkingMemoryItem]:
        items = []
        weather = world_context.get("weather", "")
        if weather and any(w in weather.lower() for w in ("storm", "rain", "extreme", "snow", "hot", "cold")):
            items.append(WorkingMemoryItem(
                content=f"Weather: {weather}",
                source="environment",
                salience=ENVIRONMENT_SALIENCE,
                source_id="weather",
            ))
        time_of_day = world_context.get("time_of_day", "")
        if time_of_day in ("night", "late_night"):
            items.append(WorkingMemoryItem(
                content=f"It's {time_of_day}",
                source="environment",
                salience=0.4,
                source_id="time",
            ))
        return items

    # -- capacity -----------------------------------------------------------

    def _get_capacity(self) -> int:
        """Buffer capacity based on focus: 3 (exhausted) to 7 (rested)."""
        return math.floor(3 + 4 * (self.focus / 100.0))

    # -- formatting ---------------------------------------------------------

    def format_for_prompt(self) -> str:
        if not self.buffer:
            return "Mind is clear — no particular focus."

        items_str = ", ".join(
            f"{item.content} (salience: {item.salience:.2f})"
            for item in self.buffer
        )
        return (
            f"Currently thinking about: {items_str}\n"
            f"Focus level: {self.focus:.0f}% | "
            f"Mental capacity: {len(self.buffer)}/{self._get_capacity()} slots"
        )

    # -- accessors ----------------------------------------------------------

    def get_focus(self) -> float:
        return self.focus

    def get_buffer(self) -> List[WorkingMemoryItem]:
        return list(self.buffer)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "focus": self.focus,
            "capacity": self._get_capacity(),
            "buffer_size": len(self.buffer),
            "context_switches": self.context_switches,
            "items": [item.to_dict() for item in self.buffer],
        }

    # -- serialization ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "buffer": [item.to_dict() for item in self.buffer],
            "focus": self.focus,
            "last_top_source": self.last_top_source,
            "context_switches": self.context_switches,
            "cycles_since_experience": self._cycles_since_experience,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkingMemorySystem":
        system = cls()
        system.buffer = [WorkingMemoryItem.from_dict(item) for item in data.get("buffer", [])]
        system.focus = data.get("focus", 100.0)
        system.last_top_source = data.get("last_top_source", "")
        system.context_switches = data.get("context_switches", 0)
        system._cycles_since_experience = data.get("cycles_since_experience", 0)
        return system
