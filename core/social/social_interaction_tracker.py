"""Social interaction tracker for Jenbina.

Records each social interaction (chat, simulated social action) with metadata
about who was involved, the emotional tone of the exchange, and a short
sentiment summary.  Provides a ``describe_day`` helper that produces a
first-person narrative Jenbina can use when reflecting on her day.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SocialInteraction:
    """A single recorded social interaction."""

    person_name: str  # who Jenbina interacted with
    interaction_type: str  # "chat", "simulated_social", "greeting", etc.
    emotional_tone: str  # e.g. "warm", "tense", "joyful", "neutral"
    sentiment: str  # short free-text feeling summary
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_name": self.person_name,
            "interaction_type": self.interaction_type,
            "emotional_tone": self.emotional_tone,
            "sentiment": self.sentiment,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialInteraction":
        return cls(
            person_name=data.get("person_name", "unknown"),
            interaction_type=data.get("interaction_type", "chat"),
            emotional_tone=data.get("emotional_tone", "neutral"),
            sentiment=data.get("sentiment", ""),
            timestamp=float(data.get("timestamp", time.time())),
        )


# ---------------------------------------------------------------------------
# Emotional-tone inference helpers (lightweight, no LLM needed)
# ---------------------------------------------------------------------------

_POSITIVE_CUES = [
    "thank", "happy", "great", "glad", "love", "awesome", "wonderful",
    "appreciate", "enjoy", "fun", "exciting", "nice", "kind", "warm",
]

_NEGATIVE_CUES = [
    "angry", "sad", "upset", "frustrated", "hate", "annoyed", "hurt",
    "worried", "anxious", "stressed", "scared", "lonely", "depressed",
]


def infer_emotional_tone(text: str) -> str:
    """Return a simple emotional-tone label from message text."""
    lower = text.lower()
    pos = sum(1 for w in _POSITIVE_CUES if w in lower)
    neg = sum(1 for w in _NEGATIVE_CUES if w in lower)
    if pos > neg:
        return "warm"
    if neg > pos:
        return "tense"
    return "neutral"


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

class SocialInteractionTracker:
    """Tracks all of Jenbina's social interactions during the session."""

    MAX_HISTORY = 200  # keep last N interactions

    def __init__(self) -> None:
        self.interactions: List[SocialInteraction] = []

    # -- recording ----------------------------------------------------------

    def record_chat(
        self,
        person_name: str,
        message_text: str,
        emotional_tone: Optional[str] = None,
        sentiment: Optional[str] = None,
    ) -> SocialInteraction:
        """Record a chat-based interaction (user talking to Jenbina)."""
        tone = emotional_tone or infer_emotional_tone(message_text)
        feel = sentiment or self._auto_sentiment(person_name, tone)
        interaction = SocialInteraction(
            person_name=person_name,
            interaction_type="chat",
            emotional_tone=tone,
            sentiment=feel,
        )
        self._store(interaction)
        return interaction

    def record_social_action(
        self,
        action_description: str,
        emotional_tone: str = "neutral",
        sentiment: Optional[str] = None,
    ) -> SocialInteraction:
        """Record a simulated social action (e.g. 'talk to neighbor')."""
        person_name = self._extract_person_from_action(action_description)
        feel = sentiment or self._auto_sentiment(person_name, emotional_tone)
        interaction = SocialInteraction(
            person_name=person_name,
            interaction_type="simulated_social",
            emotional_tone=emotional_tone,
            sentiment=feel,
        )
        self._store(interaction)
        return interaction

    # -- querying -----------------------------------------------------------

    def get_today_interactions(self, day_start_ts: Optional[float] = None) -> List[SocialInteraction]:
        """Return interactions from today (or since *day_start_ts*)."""
        if day_start_ts is None:
            import datetime as _dt
            now = _dt.datetime.now()
            day_start_ts = _dt.datetime(now.year, now.month, now.day).timestamp()
        return [i for i in self.interactions if i.timestamp >= day_start_ts]

    def get_unique_people_today(self, day_start_ts: Optional[float] = None) -> List[str]:
        """Return unique person names encountered today."""
        today = self.get_today_interactions(day_start_ts)
        seen = []
        for i in today:
            if i.person_name not in seen:
                seen.append(i.person_name)
        return seen

    def people_met_count(self, day_start_ts: Optional[float] = None) -> int:
        """How many distinct people Jenbina interacted with today."""
        return len(self.get_unique_people_today(day_start_ts))

    # -- day description ----------------------------------------------------

    def describe_day(self, day_start_ts: Optional[float] = None) -> str:
        """Produce a first-person summary Jenbina can use to describe her social day.

        Example output:
            "Today I met 3 people. I had a warm conversation with Alice and
             felt happy about it. I also chatted with Bob — the tone was
             neutral but nice. I briefly talked to a stranger during my walk,
             which felt a bit tense."
        """
        today = self.get_today_interactions(day_start_ts)
        if not today:
            return "I didn't really talk to anyone today."

        people = self.get_unique_people_today(day_start_ts)
        count = len(people)

        parts: List[str] = []
        if count == 1:
            parts.append(f"Today I met 1 person.")
        else:
            parts.append(f"Today I met {count} people.")

        # Group interactions by person
        by_person: Dict[str, List[SocialInteraction]] = {}
        for interaction in today:
            by_person.setdefault(interaction.person_name, []).append(interaction)

        for name, interactions in by_person.items():
            # Summarise the dominant tone across interactions with this person
            tones = [i.emotional_tone for i in interactions]
            dominant_tone = max(set(tones), key=tones.count)

            sentiments = [i.sentiment for i in interactions if i.sentiment]
            sentiment_text = sentiments[-1] if sentiments else ""

            n = len(interactions)
            if n == 1:
                exchange_word = "a brief exchange"
            elif n <= 3:
                exchange_word = "a conversation"
            else:
                exchange_word = "a long conversation"

            line = f"I had {exchange_word} with {name}"
            if dominant_tone != "neutral":
                line += f" — it felt {dominant_tone}"
            if sentiment_text:
                line += f". {sentiment_text}"
            else:
                line += "."
            parts.append(line)

        return " ".join(parts)

    def format_for_prompt(self, day_start_ts: Optional[float] = None) -> str:
        """Short context block suitable for injection into LLM prompts."""
        count = self.people_met_count(day_start_ts)
        if count == 0:
            return "Social interactions today: none so far."
        people = self.get_unique_people_today(day_start_ts)
        today = self.get_today_interactions(day_start_ts)
        tones = [i.emotional_tone for i in today]
        dominant = max(set(tones), key=tones.count) if tones else "neutral"
        return (
            f"Social interactions today: met {count} "
            f"{'person' if count == 1 else 'people'} "
            f"({', '.join(people)}). Overall tone: {dominant}."
        )

    # -- stats & serialization ----------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_interactions": len(self.interactions),
            "people_met_today": self.people_met_count(),
            "unique_people_today": self.get_unique_people_today(),
            "recent_interactions": [
                i.to_dict() for i in self.interactions[-5:]
            ],
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interactions": [i.to_dict() for i in self.interactions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialInteractionTracker":
        tracker = cls()
        raw_interactions = data.get("interactions", []) if isinstance(data, dict) else []
        tracker.interactions = [
            SocialInteraction.from_dict(r) for r in raw_interactions
        ]
        return tracker

    # -- private helpers ----------------------------------------------------

    def _store(self, interaction: SocialInteraction) -> None:
        self.interactions.append(interaction)
        if len(self.interactions) > self.MAX_HISTORY:
            self.interactions = self.interactions[-self.MAX_HISTORY:]

    @staticmethod
    def _auto_sentiment(person_name: str, tone: str) -> str:
        """Generate a simple automatic sentiment string."""
        if tone == "warm":
            return f"I felt good about talking to {person_name}"
        elif tone == "tense":
            return f"The interaction with {person_name} left me feeling uneasy"
        return ""

    @staticmethod
    def _extract_person_from_action(action: str) -> str:
        """Try to extract a person/entity name from a simulated action string."""
        lower = action.lower()

        # Generic role nouns — if the action mentions one, use it directly
        _GENERIC_ROLES = [
            "neighbor", "friend", "stranger", "barista", "shopkeeper",
            "coworker", "colleague", "acquaintance", "cashier", "waiter",
            "waitress", "passerby",
        ]
        for role in _GENERIC_ROLES:
            if role in lower:
                return f"a {role}"

        # Common patterns: "talk to <person>", "chat with <person>", "greet <person>"
        import re as _re
        for prefix in ["talk to ", "chat with ", "speak to ", "speak with ",
                        "greet ", "visit ", "call "]:
            if prefix in lower:
                idx = lower.index(prefix) + len(prefix)
                rest = action[idx:].strip()
                # Take the next 1-3 words as the name (stop at prepositions/punctuation)
                stop_words = {"about", "at", "in", "on", "for", "and", "the", "to", "from", "during"}
                words = _re.split(r"[\s,\.!]+", rest)
                name_parts = []
                for w in words:
                    if w.lower() in stop_words or not w:
                        break
                    name_parts.append(w)
                    if len(name_parts) >= 3:
                        break
                if name_parts:
                    return " ".join(name_parts).title()

        return "someone"
