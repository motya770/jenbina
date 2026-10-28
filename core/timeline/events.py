"""The vocabulary of Jenbina's life events, their one-line titles, and the
``EventLog`` that persists them per user.

This module has no Streamlit dependency so the headless runner can record
the same events as the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

THOUGHT = "thought"
ACTION = "action"
MOOD = "mood"
GOAL = "goal"
PLAN = "plan"
MOVE = "move"
KINDS = (THOUGHT, ACTION, MOOD, GOAL, PLAN, MOVE)

ACTION_TITLE_LIMIT = 90
MOOD_MIN_DELTA = 1.0


@dataclass
class TimelineEvent:
    """One entry of Jenbina's day. ``title`` is the line the timeline shows."""

    kind: str
    title: str
    detail: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def shorten(text: str, limit: int = ACTION_TITLE_LIMIT) -> str:
    """Cut ``text`` to at most ``limit`` characters, at a word boundary when
    there is one, ending with an ellipsis."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    head = text[: limit - 1]
    cut = head.rfind(" ")
    if cut > 0:
        head = head[:cut]
    return head.rstrip() + "…"


def lessons_text(lessons) -> str:
    """Lessons as one line: lists joined with '; ', strings as they are."""
    if not lessons:
        return ""
    if isinstance(lessons, (list, tuple)):
        return "; ".join(str(item) for item in lessons if str(item).strip())
    return str(lessons)


def mood_changes(before: dict, after: dict, limit: int = 3) -> dict:
    """``{emotion: (before, after)}`` for the ``limit`` largest changes of at
    least one point, for emotions present on both sides."""
    deltas = []
    for name, old in (before or {}).items():
        if name not in (after or {}):
            continue
        new = after[name]
        try:
            if abs(float(new) - float(old)) >= MOOD_MIN_DELTA:
                deltas.append((abs(float(new) - float(old)), name, old, new))
        except (TypeError, ValueError):
            continue
    deltas.sort(key=lambda item: item[0], reverse=True)
    return {name: (old, new) for _, name, old, new in deltas[:limit]}


# --------------------------------------------------------------------------
# Builders: one per kind, titles computed here and only here
# --------------------------------------------------------------------------

def make_thought(mode: str, text: str) -> TimelineEvent:
    return TimelineEvent(THOUGHT, text, {"mode": mode, "text": text})


def make_action(action: str, reasoning: str, lessons, satisfaction_before: float,
                satisfaction_after: float, location: str, time_of_day: str,
                weather: str, temperature: float) -> TimelineEvent:
    if isinstance(lessons, str):
        lessons_list = [lessons] if lessons.strip() else []
    else:
        lessons_list = [str(item) for item in (lessons or [])]
    title = "Jenbina decided to " + shorten(str(action or "").lower(), ACTION_TITLE_LIMIT)
    return TimelineEvent(ACTION, title, {
        "action": action,
        "reasoning": reasoning or "",
        "lessons": lessons_list,
        "satisfaction_before": satisfaction_before,
        "satisfaction_after": satisfaction_after,
        "location": location,
        "time_of_day": time_of_day,
        "weather": weather,
        "temperature": temperature,
    })


def make_mood(changes: dict, source: str) -> Optional[TimelineEvent]:
    if not changes:
        return None
    total = sum(float(new) - float(old) for old, new in changes.values())
    word = "lifted" if total > 0 else "dipped"
    parts = ", ".join(f"{name} {float(old):.0f} → {float(new):.0f}" for name, (old, new) in changes.items())
    return TimelineEvent(MOOD, f"Mood {word}: {parts}", {
        "source": source,
        "changes": {name: [old, new] for name, (old, new) in changes.items()},
    })


def make_goal(event: str, description: str, progress: float) -> TimelineEvent:
    if event == "created":
        title = f"New goal: {description}"
    elif event == "completed":
        title = f"Goal reached: {description}"
    else:
        title = f"Goal advanced: {description} → {float(progress):.0%}"
    return TimelineEvent(GOAL, title, {"event": event, "description": description, "progress": progress})


def make_plan(event: str, goal: str, step: str) -> TimelineEvent:
    if event == "step_completed":
        title = f"Plan step done: {step}"
    elif event == "replanned":
        title = f"Replanned: {goal}, first step {step}"
    elif event == "completed":
        title = f"Plan finished: {goal}"
    else:
        title = "Plan step skipped for an urgent need"
    return TimelineEvent(PLAN, title, {"event": event, "goal": goal, "step": step})


def make_move(src: str, dst: str) -> TimelineEvent:
    return TimelineEvent(MOVE, f"Walked from {src} to {dst}", {"from": src, "to": dst})


# --------------------------------------------------------------------------
# The log
# --------------------------------------------------------------------------

class EventLog:
    """Persists events through ``UserDatabase`` when it has a user, otherwise
    keeps them in memory (tests, sessions without a user)."""

    def __init__(self, user_db=None, user_id=None):
        self.user_db = user_db
        self.user_id = user_id
        self._memory: list[TimelineEvent] = []

    @property
    def persistent(self) -> bool:
        return self.user_db is not None and self.user_id is not None

    def record(self, event: TimelineEvent) -> TimelineEvent:
        """Store ``event`` and return it. Never raises: a storage failure is
        printed and the event is dropped so an iteration keeps going."""
        if event is None:
            return None
        if not self.persistent:
            self._memory.append(event)
            return event
        try:
            event.id = self.user_db.store_event(
                self.user_id, event.kind, event.title, event.detail, event.created_at
            )
        except Exception as exc:  # noqa: BLE001 - storage must never break the runner
            print(f"EventLog: could not store {event.kind} event: {exc}")
        return event

    def recent(self, limit: int = 200) -> list[TimelineEvent]:
        """The most recent ``limit`` events, oldest first."""
        if not self.persistent:
            return list(self._memory[-limit:]) if limit else []
        try:
            rows = self.user_db.get_events(self.user_id, limit=limit)
        except Exception as exc:  # noqa: BLE001
            print(f"EventLog: could not read events: {exc}")
            return []
        return [
            TimelineEvent(row["kind"], row["title"], row.get("detail") or {}, row["created_at"], row.get("id"))
            for row in rows
        ]
