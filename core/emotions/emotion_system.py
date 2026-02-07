from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime, timedelta


@dataclass
class Emotion:
    """Represents a single emotion with intensity that decays toward a baseline."""
    name: str
    intensity: float = 0.0          # Current intensity (0-100)
    decay_rate: float = 5.0         # How fast it fades per hour
    base_intensity: float = 0.0     # Resting/character baseline
    last_triggered: datetime = field(default_factory=datetime.now)

    def update(self, hours_passed: float):
        """Decay intensity toward base_intensity over time."""
        if hours_passed <= 0:
            return

        decay_amount = self.decay_rate * hours_passed

        if self.intensity > self.base_intensity:
            self.intensity = max(self.base_intensity, self.intensity - decay_amount)
        elif self.intensity < self.base_intensity:
            self.intensity = min(self.base_intensity, self.intensity + decay_amount)

    def trigger(self, amount: float):
        """Spike (or reduce) this emotion's intensity."""
        self.intensity = max(0.0, min(100.0, self.intensity + amount))
        self.last_triggered = datetime.now()


@dataclass
class EmotionSystem:
    """Complete emotion system with decay toward character baselines."""
    emotions: Dict[str, Emotion] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.emotions:
            self._initialize_default_emotions()

    def _initialize_default_emotions(self):
        """Initialize Jenbina's default character emotions (Plutchik's wheel)."""
        defaults = [
            ("joy",          35, 5.0,  35),
            ("sadness",      10, 3.0,  10),
            ("anger",         5, 8.0,   5),
            ("fear",         15, 6.0,  15),
            ("surprise",     20, 10.0, 20),
            ("disgust",       5, 7.0,   5),
            ("trust",        40, 2.0,  40),
            ("anticipation", 30, 4.0,  30),
        ]
        for name, intensity, decay_rate, base in defaults:
            self.emotions[name] = Emotion(
                name=name,
                intensity=float(intensity),
                decay_rate=decay_rate,
                base_intensity=float(base),
            )

    def update_all(self):
        """Decay all emotions toward their baselines based on elapsed time."""
        now = datetime.now()
        hours_passed = (now - self.last_update).total_seconds() / 3600
        if hours_passed > 0:
            for emotion in self.emotions.values():
                emotion.update(hours_passed)
            self.last_update = now

    def trigger_emotion(self, name: str, amount: float):
        """Spike a specific emotion by amount (positive or negative)."""
        if name in self.emotions:
            self.emotions[name].trigger(amount)

    def apply_adjustments(self, adjustments: Dict[str, float]):
        """Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}."""
        for name, amount in adjustments.items():
            self.trigger_emotion(name, amount)

    def get_dominant_emotions(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get the top-k emotions by intensity."""
        sorted_emotions = sorted(
            self.emotions.values(),
            key=lambda e: e.intensity,
            reverse=True,
        )
        return [
            {"name": e.name, "intensity": round(e.intensity, 1)}
            for e in sorted_emotions[:top_k]
        ]

    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get a summary dict suitable for LLM prompts."""
        return {
            "emotions": {
                name: round(e.intensity, 1) for name, e in self.emotions.items()
            },
            "dominant_emotions": self.get_dominant_emotions(3),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "emotions": {
                name: {
                    "name": e.name,
                    "intensity": e.intensity,
                    "decay_rate": e.decay_rate,
                    "base_intensity": e.base_intensity,
                    "last_triggered": e.last_triggered.isoformat(),
                }
                for name, e in self.emotions.items()
            },
            "last_update": self.last_update.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionSystem":
        """Deserialize from dictionary."""
        system = cls.__new__(cls)
        system.last_update = datetime.fromisoformat(data.get("last_update", datetime.now().isoformat()))
        system.emotions = {}
        for name, e_data in data.get("emotions", {}).items():
            system.emotions[name] = Emotion(
                name=e_data["name"],
                intensity=e_data["intensity"],
                decay_rate=e_data["decay_rate"],
                base_intensity=e_data["base_intensity"],
                last_triggered=datetime.fromisoformat(e_data["last_triggered"]),
            )
        return system

    def __str__(self):
        dominant = self.get_dominant_emotions(3)
        dominant_str = ", ".join(f"{d['name']}: {d['intensity']}" for d in dominant)
        return f"EmotionSystem(dominant: {dominant_str})"
