"""Internal monologue / stream-of-consciousness system for Jenbina.

Generates the narrative inner voice that runs *between* decisions.
Four thought modes:

1. **Deliberation** — thinking through what to do next given current state.
2. **Rumination** — replaying past events, especially negative or unresolved ones.
3. **Worry** — projecting future problems based on trends and unmet needs.
4. **Daydreaming** — idle, creative, or wishful thinking when needs are met
   and nothing urgent demands attention.

The system selects a mode based on the current cognitive/emotional landscape,
then uses the LLM to generate a short first-person thought stream.
"""

import json
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..fix_llm_json import fix_llm_json


# ---------------------------------------------------------------------------
# Thought mode enum
# ---------------------------------------------------------------------------

class ThoughtMode(str, Enum):
    DELIBERATION = "deliberation"
    RUMINATION = "rumination"
    WORRY = "worry"
    DAYDREAMING = "daydreaming"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class InnerThought:
    """A single inner-monologue entry."""
    content: str
    mode: str  # ThoughtMode value
    trigger: str  # what caused this thought
    emotional_tone: str  # e.g. "anxious", "content", "melancholic"
    intensity: float  # 0.0 – 1.0, how loud / intrusive
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "mode": self.mode,
            "trigger": self.trigger,
            "emotional_tone": self.emotional_tone,
            "intensity": self.intensity,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InnerThought":
        return cls(**data)


# ---------------------------------------------------------------------------
# Mode selection thresholds
# ---------------------------------------------------------------------------

# If *any* need satisfaction is below this → deliberation mode
DELIBERATION_NEED_THRESHOLD = 50.0

# If the dominant negative emotion is above this → rumination mode
RUMINATION_EMOTION_THRESHOLD = 45.0

# If multiple needs are trending downward → worry mode
WORRY_TREND_THRESHOLD = -5.0  # average delta across needs

# Daydreaming is the default when nothing else fires
BOREDOM_SATISFACTION_THRESHOLD = 65.0  # all needs above this → bored/content


# ---------------------------------------------------------------------------
# LLM prompt templates
# ---------------------------------------------------------------------------

DELIBERATION_PROMPT = PromptTemplate(
    input_variables=["working_memory", "needs_summary", "emotional_state",
                     "world_context", "recent_action"],
    template="""You are generating the internal monologue of a person named Jenbina.
She is currently thinking through what to do next. This is her private inner voice —
stream-of-consciousness style, first person, informal, with natural hesitations and
self-questioning.

What's on her mind right now:
{working_memory}

Her current needs (satisfaction %):
{needs_summary}

Her emotional state:
{emotional_state}

World around her:
{world_context}

What she just did:
{recent_action}

Generate 2-4 sentences of Jenbina's internal deliberation. She should weigh options,
consider her needs, and think about what matters most right now. Include natural
self-talk like "maybe I should...", "but then again...", "the thing is...".

Return JSON:
{{
    "thought": "the internal monologue text",
    "emotional_tone": "one word describing the tone (e.g. restless, focused, torn)",
    "intensity": 0.7
}}""",
)

RUMINATION_PROMPT = PromptTemplate(
    input_variables=["working_memory", "emotional_state", "recent_experiences",
                     "lessons_learned"],
    template="""You are generating the internal monologue of a person named Jenbina.
She is ruminating — replaying past events in her mind, especially ones that left
a mark emotionally. This is her private inner voice — stream-of-consciousness,
first person, slightly repetitive as rumination tends to be.

What's on her mind:
{working_memory}

Her emotional state:
{emotional_state}

Recent experiences she keeps thinking about:
{recent_experiences}

Lessons she's drawn (or is still processing):
{lessons_learned}

Generate 2-4 sentences of Jenbina ruminating. She should replay a specific event,
question whether she handled it right, and circle back to the feeling it left.
Use phrases like "I keep thinking about...", "what if I had...", "it still bothers me that...".

Return JSON:
{{
    "thought": "the internal monologue text",
    "emotional_tone": "one word (e.g. regretful, wistful, frustrated)",
    "intensity": 0.6
}}""",
)

WORRY_PROMPT = PromptTemplate(
    input_variables=["working_memory", "needs_summary", "emotional_state",
                     "needs_trends", "world_context"],
    template="""You are generating the internal monologue of a person named Jenbina.
She is worrying — projecting problems into the future based on how things are trending.
This is her private inner voice — anxious, future-focused, slightly catastrophizing.

What's on her mind:
{working_memory}

Her current needs:
{needs_summary}

How her needs have been trending:
{needs_trends}

Her emotional state:
{emotional_state}

World context:
{world_context}

Generate 2-4 sentences of Jenbina worrying about the future. She should notice
negative trends, project them forward, and imagine what might go wrong.
Use phrases like "what if...", "at this rate...", "I'm worried that...",
"things keep getting worse with...".

Return JSON:
{{
    "thought": "the internal monologue text",
    "emotional_tone": "one word (e.g. anxious, dread, uneasy)",
    "intensity": 0.7
}}""",
)

DAYDREAM_PROMPT = PromptTemplate(
    input_variables=["working_memory", "emotional_state", "goals",
                     "world_context"],
    template="""You are generating the internal monologue of a person named Jenbina.
She is daydreaming — her needs are met, nothing urgent is happening, and her mind
is wandering freely. This is her private inner voice — relaxed, creative, playful,
sometimes philosophical.

What's loosely on her mind:
{working_memory}

Her emotional state:
{emotional_state}

Her longer-term aspirations:
{goals}

World around her:
{world_context}

Generate 2-4 sentences of Jenbina daydreaming. She might imagine future
possibilities, reflect on something beautiful, have a random creative idea,
or just enjoy the moment. Use phrases like "I wonder what it would be like to...",
"wouldn't it be nice if...", "hm, what if I tried...", "this reminds me of...".

Return JSON:
{{
    "thought": "the internal monologue text",
    "emotional_tone": "one word (e.g. content, whimsical, dreamy, curious)",
    "intensity": 0.3
}}""",
)


# ---------------------------------------------------------------------------
# InnerMonologueSystem
# ---------------------------------------------------------------------------

class InnerMonologueSystem:
    """Generates Jenbina's internal stream of consciousness between decisions."""

    MAX_THOUGHT_HISTORY = 50

    def __init__(self, llm):
        self.llm = llm
        self.thought_history: List[InnerThought] = []
        self.current_thought: Optional[InnerThought] = None
        self._consecutive_mode_counts: Dict[str, int] = {
            mode.value: 0 for mode in ThoughtMode
        }
        self._last_mode: Optional[str] = None
        self._needs_snapshots: List[Dict[str, float]] = []

    # -- mode selection -----------------------------------------------------

    def select_mode(
        self,
        needs: Dict[str, float],
        emotions: Dict[str, float],
        recent_experiences: Optional[List[Dict[str, Any]]] = None,
        needs_trends: Optional[Dict[str, float]] = None,
    ) -> ThoughtMode:
        """Determine which thought mode to activate based on current state.

        Priority order:
        1. Deliberation — if any need is critically low
        2. Rumination  — if strong negative emotions and recent experiences exist
        3. Worry       — if needs are trending downward
        4. Daydreaming — default / all-needs-met state
        """
        # 1. Deliberation: any need below threshold?
        critical_needs = [
            name for name, sat in needs.items()
            if sat < DELIBERATION_NEED_THRESHOLD
        ]
        if critical_needs:
            return ThoughtMode.DELIBERATION

        # 2. Rumination: strong negative emotions + something to replay?
        negative_emotions = {
            name: val for name, val in emotions.items()
            if name in ("sadness", "anger", "fear", "disgust")
        }
        max_negative = max(negative_emotions.values()) if negative_emotions else 0.0
        has_experiences = bool(recent_experiences and len(recent_experiences) > 0)
        if max_negative > RUMINATION_EMOTION_THRESHOLD and has_experiences:
            return ThoughtMode.RUMINATION

        # 3. Worry: needs trending down?
        if needs_trends:
            avg_trend = sum(needs_trends.values()) / max(len(needs_trends), 1)
            declining_count = sum(1 for v in needs_trends.values() if v < 0)
            if avg_trend < WORRY_TREND_THRESHOLD or declining_count >= 3:
                return ThoughtMode.WORRY

        # 4. Daydreaming: everything is fine, mind wanders
        return ThoughtMode.DAYDREAMING

    # -- thought generation -------------------------------------------------

    def generate_thought(
        self,
        mode: ThoughtMode,
        working_memory: str,
        needs_summary: str,
        emotional_state: str,
        world_context: str = "No particular context.",
        recent_action: str = "Nothing in particular.",
        recent_experiences: str = "No notable recent experiences.",
        lessons_learned: str = "No lessons yet.",
        needs_trends: str = "Stable.",
        goals: str = "No particular goals right now.",
    ) -> InnerThought:
        """Use the LLM to generate an inner-monologue thought in the given mode."""

        prompt_map = {
            ThoughtMode.DELIBERATION: DELIBERATION_PROMPT,
            ThoughtMode.RUMINATION: RUMINATION_PROMPT,
            ThoughtMode.WORRY: WORRY_PROMPT,
            ThoughtMode.DAYDREAMING: DAYDREAM_PROMPT,
        }

        prompt_template = prompt_map[mode]

        # Build keyword arguments based on which variables the template expects
        kwargs: Dict[str, str] = {}
        for var in prompt_template.input_variables:
            kwargs[var] = locals().get(var, "N/A")

        prompt_text = prompt_template.format(**kwargs)

        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content if hasattr(response, "content") else str(response)

            parsed = fix_llm_json(broken_json=response_text, llm_json_mode=self.llm)
            if not isinstance(parsed, dict):
                parsed = {}

            thought_text = parsed.get("thought", "...")
            emotional_tone = parsed.get("emotional_tone", "neutral")
            intensity = float(parsed.get("intensity", 0.5))
            intensity = max(0.0, min(1.0, intensity))

        except Exception:
            # Fallback: produce a minimal thought so the system never crashes
            thought_text = self._fallback_thought(mode)
            emotional_tone = "neutral"
            intensity = 0.3

        thought = InnerThought(
            content=thought_text,
            mode=mode.value,
            trigger=self._describe_trigger(mode, needs_summary, emotional_state),
            emotional_tone=emotional_tone,
            intensity=intensity,
        )

        self._record_thought(thought)
        return thought

    # -- public interface ---------------------------------------------------

    def think(
        self,
        needs: Dict[str, float],
        emotions: Dict[str, float],
        working_memory_str: str,
        needs_summary_str: str,
        emotional_state_str: str,
        world_context_str: str = "No particular context.",
        recent_action_str: str = "Nothing in particular.",
        recent_experiences_list: Optional[List[Dict[str, Any]]] = None,
        recent_experiences_str: str = "No notable recent experiences.",
        lessons_learned_str: str = "No lessons yet.",
        goals_str: str = "No particular goals right now.",
        needs_trends: Optional[Dict[str, float]] = None,
    ) -> InnerThought:
        """Main entry point: select mode, generate thought, return it.

        Call this once per simulation cycle, *before* the action decision.
        """
        # Track needs snapshots for trend calculation
        self._needs_snapshots.append(dict(needs))
        if len(self._needs_snapshots) > 10:
            self._needs_snapshots = self._needs_snapshots[-10:]

        # Compute trends if not provided
        if needs_trends is None:
            needs_trends = self._compute_needs_trends(needs)

        # Build needs_trends string for prompt
        if needs_trends:
            trends_parts = []
            for name, delta in sorted(needs_trends.items(), key=lambda x: x[1]):
                direction = "declining" if delta < -1.0 else "rising" if delta > 1.0 else "stable"
                trends_parts.append(f"{name}: {direction} ({delta:+.1f})")
            needs_trends_str = "\n".join(trends_parts)
        else:
            needs_trends_str = "No trend data yet."

        mode = self.select_mode(
            needs=needs,
            emotions=emotions,
            recent_experiences=recent_experiences_list,
            needs_trends=needs_trends,
        )

        # Prevent getting stuck in the same mode forever — add slight randomness
        mode = self._maybe_vary_mode(mode)

        thought = self.generate_thought(
            mode=mode,
            working_memory=working_memory_str,
            needs_summary=needs_summary_str,
            emotional_state=emotional_state_str,
            world_context=world_context_str,
            recent_action=recent_action_str,
            recent_experiences=recent_experiences_str,
            lessons_learned=lessons_learned_str,
            needs_trends=needs_trends_str,
            goals=goals_str,
        )

        return thought

    # -- formatting for prompts --------------------------------------------

    def format_for_prompt(self) -> str:
        """Format the most recent thought for inclusion in action-decision prompts."""
        if self.current_thought is None:
            return "No inner thoughts at the moment."

        t = self.current_thought
        return (
            f"[Inner voice — {t.mode}] {t.content}\n"
            f"(tone: {t.emotional_tone}, intensity: {t.intensity:.1f})"
        )

    def format_recent_thoughts(self, count: int = 3) -> str:
        """Format the last N thoughts for richer context."""
        if not self.thought_history:
            return "No recent thoughts."
        recent = self.thought_history[-count:]
        lines = []
        for t in recent:
            lines.append(f"[{t.mode}] {t.content} (tone: {t.emotional_tone})")
        return "\n".join(lines)

    # -- accessors ----------------------------------------------------------

    def get_current_thought(self) -> Optional[InnerThought]:
        return self.current_thought

    def get_thought_history(self, count: int = 10) -> List[InnerThought]:
        return list(self.thought_history[-count:])

    def get_stats(self) -> Dict[str, Any]:
        mode_counts: Dict[str, int] = {}
        for t in self.thought_history:
            mode_counts[t.mode] = mode_counts.get(t.mode, 0) + 1
        return {
            "total_thoughts": len(self.thought_history),
            "current_mode": self.current_thought.mode if self.current_thought else None,
            "mode_distribution": mode_counts,
            "last_mode": self._last_mode,
            "current_thought": self.current_thought.to_dict() if self.current_thought else None,
        }

    # -- internal helpers ---------------------------------------------------

    def _record_thought(self, thought: InnerThought):
        self.thought_history.append(thought)
        if len(self.thought_history) > self.MAX_THOUGHT_HISTORY:
            self.thought_history = self.thought_history[-self.MAX_THOUGHT_HISTORY:]
        self.current_thought = thought

        # Track consecutive mode usage
        if thought.mode == self._last_mode:
            self._consecutive_mode_counts[thought.mode] = (
                self._consecutive_mode_counts.get(thought.mode, 0) + 1
            )
        else:
            self._consecutive_mode_counts = {m.value: 0 for m in ThoughtMode}
            self._consecutive_mode_counts[thought.mode] = 1
        self._last_mode = thought.mode

    def _maybe_vary_mode(self, selected_mode: ThoughtMode) -> ThoughtMode:
        """If we've been in the same mode for 3+ cycles, occasionally switch."""
        consecutive = self._consecutive_mode_counts.get(selected_mode.value, 0)
        if consecutive >= 3 and random.random() < 0.3:
            alternatives = [m for m in ThoughtMode if m != selected_mode]
            return random.choice(alternatives)
        return selected_mode

    def _compute_needs_trends(self, current_needs: Dict[str, float]) -> Dict[str, float]:
        """Compute per-need deltas from the last 2+ snapshots."""
        if len(self._needs_snapshots) < 2:
            return {}
        previous = self._needs_snapshots[-2]
        trends = {}
        for name in current_needs:
            if name in previous:
                trends[name] = current_needs[name] - previous[name]
        return trends

    def _describe_trigger(self, mode: ThoughtMode, needs: str, emotions: str) -> str:
        triggers = {
            ThoughtMode.DELIBERATION: "unmet needs requiring attention",
            ThoughtMode.RUMINATION: "strong emotions about past events",
            ThoughtMode.WORRY: "needs trending downward",
            ThoughtMode.DAYDREAMING: "contentment and idle mind",
        }
        return triggers.get(mode, "unknown")

    @staticmethod
    def _fallback_thought(mode: ThoughtMode) -> str:
        fallbacks = {
            ThoughtMode.DELIBERATION: "Hmm, I need to figure out what to do next...",
            ThoughtMode.RUMINATION: "I keep going back to what happened earlier...",
            ThoughtMode.WORRY: "I can't stop thinking about what might go wrong...",
            ThoughtMode.DAYDREAMING: "My mind is wandering... it's kind of nice.",
        }
        return fallbacks.get(mode, "...")

    # -- serialization ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "thought_history": [t.to_dict() for t in self.thought_history],
            "current_thought": self.current_thought.to_dict() if self.current_thought else None,
            "consecutive_mode_counts": self._consecutive_mode_counts,
            "last_mode": self._last_mode,
            "needs_snapshots": self._needs_snapshots,
        }

    @classmethod
    def from_dict(cls, data: dict, llm) -> "InnerMonologueSystem":
        system = cls(llm)
        system.thought_history = [
            InnerThought.from_dict(t) for t in data.get("thought_history", [])
        ]
        ct = data.get("current_thought")
        system.current_thought = InnerThought.from_dict(ct) if ct else None
        system._consecutive_mode_counts = data.get(
            "consecutive_mode_counts",
            {m.value: 0 for m in ThoughtMode},
        )
        system._last_mode = data.get("last_mode")
        system._needs_snapshots = data.get("needs_snapshots", [])
        return system
