"""Insight generation system for the Deep Emotional Mirror feature.

Generates unexpectedly perceptive observations about the user based on
their dossier, conversation history, and Jenbina's emotional state.
Insights are rare — max 3 per session, starting after 2-3 messages.
"""

from typing import Dict, Any, List, Optional

from langchain.schema import HumanMessage, SystemMessage


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

    def __init__(self, llm, max_per_session: int = 3, min_messages: int = 2):
        self.llm = llm
        self.max_per_session = max_per_session
        self.min_messages = min_messages
        self.insights_delivered = 0

    def should_generate_insight(self, message_count: int) -> bool:
        """Check if conditions are met to generate an insight."""
        if self.insights_delivered >= self.max_per_session:
            return False
        if message_count < self.min_messages:
            return False
        return True

    def generate_insight(
        self,
        dossier: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
        emotional_state: Dict[str, Any],
        self_narrative: str,
    ) -> Optional[str]:
        """Generate a perceptive observation about the user.

        Returns the insight string, or None if generation fails.
        """
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

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            insight = response.content.strip()
            if insight:
                self.insights_delivered += 1
                return insight
            return None
        except Exception as e:
            print(f"Insight generation failed: {e}")
            return None

    def reset_session(self):
        """Reset the per-session counter (call on new session start)."""
        self.insights_delivered = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_per_session": self.max_per_session,
            "min_messages": self.min_messages,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm) -> "InsightSystem":
        return cls(
            llm=llm,
            max_per_session=data.get("max_per_session", 3),
            min_messages=data.get("min_messages", 2),
        )
