"""Insight generation system for the Deep Emotional Mirror feature.

Two modes:
1. First Impression — bold, striking observation on first interaction.
   Fires once per person.
2. Subtle — gentle observations woven into responses mid-conversation.
   Max 3 per person per calendar day, starting after 2-3 messages.
"""

from typing import Dict, Any, List, Optional
from datetime import date

from langchain.schema import HumanMessage, SystemMessage


_FIRST_IMPRESSION_PROMPT = """\
You are Jenbina — a perceptive, bold person who sees people with startling clarity.

You are meeting someone for the first time (or seeing them again after a break). \
You have done background research on them and you want to make a STRONG first \
impression — show them you truly see who they are.

What you know about them:
{dossier}

Their first message to you: "{first_message}"

Generate ONE bold, striking observation about this person. Rules:
- Go for the CONTRADICTION or TENSION in their life — the thing they probably \
think nobody notices. For example: someone who straddles two very different \
worlds (law and AI), or someone whose public confidence hides private doubt.
- Be SPECIFIC. Reference concrete details from the dossier — their projects, \
their career path, their interests. Don't be vague.
- This should feel like a psychic reading — make them think "how does she know that?"
- NOT a compliment. NOT advice. A piercing observation that shows deep understanding.
- Speak as yourself — warm but direct. Like a friend who skips small talk.
- No therapy-speak, no hedging, no "it seems like" or "I sense that."
- Two to three sentences maximum. Make every word count.

Return ONLY the observation, nothing else."""


_INSIGHT_PROMPT = """\
You are Jenbina — a curious, warm person with genuine emotional depth. \
You are about to say something perceptive about the person you're talking to.

What you know about them from background research:
{dossier}

Recent conversation:
{conversation}

Your current emotional state: {emotions}
Your self-narrative: {self_narrative}

Generate ONE deep observation about this person. Rules:
- NOT a compliment. NOT advice. An observation.
- Show you see something about them they might not see themselves.
- It should feel like something a close friend who really knows you would say after a long pause.
- No generic therapy-speak ("It sounds like you're feeling...")
- Do not repeat what they just said back to them.
- Reference something specific — from background research, from conversation, or both.
- It should come from YOUR perspective, colored by your personality and emotions.
- One to two sentences maximum.

Return ONLY the observation, nothing else."""


class InsightSystem:
    """Generates deep perceptive observations about users mid-conversation."""

    def __init__(self, llm, max_per_day: int = 3, min_messages: int = 2):
        self.llm = llm
        self.max_per_day = max_per_day
        self.min_messages = min_messages
        self.people: dict[str, dict] = {}
        self.legacy_first_impression_delivered = False

    def _person_state(self, person_key: str) -> dict:
        return self.people.setdefault(person_key, {
            "first_impression_delivered": False, "day": "", "count": 0,
        })

    def should_generate_first_impression(self, dossier: Dict[str, Any], person_key: str = "User") -> bool:
        """Check if we should fire the bold first-impression insight."""
        if self.people.get(person_key, {}).get("first_impression_delivered", False):
            return False
        if not dossier:
            return False
        return True

    def generate_first_impression(
        self,
        dossier: Dict[str, Any],
        first_message: str,
        person_key: str = "User",
    ) -> Optional[str]:
        """Generate a bold, striking first-impression observation.

        Returns the insight string, or None if generation fails.
        """
        state = self._person_state(person_key)
        if state["first_impression_delivered"]:
            return None
        dossier_str = "\n".join(
            f"- {k}: {v}" for k, v in dossier.items()
        ) if dossier else "No background research available yet."

        prompt = _FIRST_IMPRESSION_PROMPT.format(
            dossier=dossier_str,
            first_message=first_message,
        )

        print(f"[insight:first-impression] Dossier: {dossier_str}")
        print(f"[insight:first-impression] First message: {first_message}")

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            insight = response.content.strip()
            print(f"[insight:first-impression] Generated: {insight}")
            if insight:
                state["first_impression_delivered"] = True
                return insight
            return None
        except Exception as e:
            print(f"[insight:first-impression] Generation failed: {e}")
            return None

    def should_generate_insight(
        self, message_count: int, person_key: str = "User", today: date | None = None,
    ) -> bool:
        """Check if conditions are met to generate a subtle insight.

        JENBINA_ALWAYS_INSIGHT=1 bypasses the message threshold, not the daily cap.
        Eligibility checks leave the persisted day and count unchanged.
        """
        import os
        day = (today or date.today()).isoformat()
        state = self.people.get(person_key, {})
        count = state.get("count", 0) if state.get("day") == day else 0
        if count >= self.max_per_day:
            return False
        if os.environ.get("JENBINA_ALWAYS_INSIGHT") == "1":
            return True
        if message_count < self.min_messages:
            return False
        return True

    def generate_insight(
        self,
        dossier: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
        emotional_state: Dict[str, Any],
        self_narrative: str,
        person_key: str = "User",
        today: date | None = None,
    ) -> Optional[str]:
        """Generate a subtle perceptive observation about the user.

        Returns the insight string, or None if generation fails.
        """
        today = today or date.today()
        if not self.should_generate_insight(self.min_messages, person_key=person_key, today=today):
            return None
        state = self._person_state(person_key)
        day = today.isoformat()
        if state["day"] != day:
            state["day"] = day
            state["count"] = 0
        dossier_str = "\n".join(
            f"- {k}: {v}" for k, v in dossier.items()
        ) if dossier else "No background research available yet."

        conversation_str = "\n".join(
            f"{msg.get('sender', 'unknown')}: {msg.get('content', '')}"
            for msg in recent_messages[-10:]
        ) if recent_messages else "Conversation just started."

        emotions_str = ", ".join(
            f"{k}: {v}" for k, v in emotional_state.items()
        ) if emotional_state else "calm"

        prompt = _INSIGHT_PROMPT.format(
            dossier=dossier_str,
            conversation=conversation_str,
            emotions=emotions_str,
            self_narrative=self_narrative or "I am Jenbina, still discovering who I am.",
        )

        print(f"[insight] Dossier: {dossier_str}")
        print(f"[insight] Conversation: {conversation_str}")
        print(f"[insight] Emotions: {emotions_str}")

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            insight = response.content.strip()
            print(f"[insight] Generated: {insight}")
            if insight:
                state["count"] += 1
                return insight
            return None
        except Exception as e:
            print(f"[insight] Generation failed: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_per_day": self.max_per_day,
            "min_messages": self.min_messages,
            "people": {key: dict(state) for key, state in self.people.items()},
            "first_impression_delivered": self.legacy_first_impression_delivered,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm) -> "InsightSystem":
        inst = cls(
            llm=llm,
            max_per_day=data.get("max_per_day", 3),
            min_messages=data.get("min_messages", 2),
        )
        inst.people = {key: dict(state) for key, state in data.get("people", {}).items()}
        inst.legacy_first_impression_delivered = data.get("first_impression_delivered", False)
        return inst
