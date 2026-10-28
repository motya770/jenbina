"""The chat timeline: the conversation with Jenbina interleaved with her life
events (thoughts, actions, moods, goals, plans, moves), newest at the bottom."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

from core.timeline import ACTION, GOAL, MOOD, MOVE, PLAN, THOUGHT, TimelineEvent, lessons_text
from core.ui.pixel_theme import action_icon, delta_badge_html, event_html, marker_html
from core.ui.sprites import avatar_path, icon_path

FILTERS = ("All", "Chat", "Her day", "Thoughts")
TIMELINE_LIMIT = 200
TIMELINE_HEIGHT = 560
MARKER_GAP = timedelta(minutes=60)
EMPTY_TEXT = "Nothing yet. Say hi, or let her live."
OUTREACH_META = "she reached out first"
OUTREACH_TYPES = ("greeting", "proactive")
MESSAGE_KINDS = ("user", "jenbina")
HER_DAY_KINDS = frozenset({ACTION, MOVE, GOAL, PLAN, MOOD})

_SENTENCE_END = re.compile(r"[.!?…](?:\s|$)")


@dataclass
class TimelineItem:
    """One row of the timeline: a message, a life event, or a marker."""

    kind: str                      # "user", "jenbina", "marker", or an event kind
    timestamp: datetime
    text: str                      # message content, marker text, or event title
    meta: str = ""                 # "23:38 · she reached out first"
    event: Optional[TimelineEvent] = None


def first_sentence(text: str) -> tuple[str, str]:
    """``(first sentence, remainder)``; the whole text and ``""`` when it has
    no sentence punctuation."""
    text = (text or "").strip()
    match = _SENTENCE_END.search(text)
    if not match:
        return text, ""
    return text[: match.end()].strip(), text[match.end():].strip()


def _hhmm(when: datetime) -> str:
    return when.strftime("%H:%M")


def _passes(item: TimelineItem, filter_name: str) -> bool:
    if filter_name == "Chat":
        return item.kind in MESSAGE_KINDS
    if filter_name == "Her day":
        return item.kind in HER_DAY_KINDS
    if filter_name == "Thoughts":
        return item.kind == THOUGHT
    return True


def _marker_text(when: datetime, previous: Optional[TimelineItem], actions: list[TimelineEvent]) -> str:
    text = _hhmm(when)
    if previous is not None and when.date() != previous.timestamp.date():
        text += " · " + when.strftime("%a %d %b")
    context = None
    for event in actions:
        if event.created_at <= when:
            context = event
        else:
            break
    if context is not None:
        detail = context.detail or {}
        parts = [str(p) for p in (detail.get("location"), detail.get("time_of_day")) if p]
        weather = detail.get("weather")
        if weather:
            try:
                temperature = float(detail.get("temperature") or 0)
            except (TypeError, ValueError):
                temperature = 0.0
            parts.append(f"{weather}, {temperature:.0f}°C")
        if parts:
            text += " · " + " · ".join(parts)
    return text


def build_timeline(messages, events, person_name: str = "Jenbina", filter_name: str = "All",
                   limit: int = TIMELINE_LIMIT) -> list[TimelineItem]:
    """Merge chat messages and life events by time, apply the filter, keep the
    newest ``limit`` items and insert time markers before gaps and day changes."""
    rows = []
    for msg in messages or []:
        is_jenbina = msg.sender in ("person", person_name)
        meta = _hhmm(msg.timestamp)
        if is_jenbina and getattr(msg, "message_type", "text") in OUTREACH_TYPES:
            meta += " · " + OUTREACH_META
        rows.append((msg.timestamp, 1, TimelineItem("jenbina" if is_jenbina else "user", msg.timestamp, msg.content, meta)))
    actions = []
    for event in events or []:
        rows.append((event.created_at, 0, TimelineItem(event.kind, event.created_at, event.title, _hhmm(event.created_at), event)))
        if event.kind == ACTION:
            actions.append(event)
    rows.sort(key=lambda row: (row[0], row[1]))
    actions.sort(key=lambda event: event.created_at)

    kept = [item for _, _, item in rows if _passes(item, filter_name)]
    if limit:
        kept = kept[-limit:]

    out: list[TimelineItem] = []
    previous: Optional[TimelineItem] = None
    for item in kept:
        if (previous is None or item.timestamp - previous.timestamp > MARKER_GAP
                or item.timestamp.date() != previous.timestamp.date()):
            out.append(TimelineItem("marker", item.timestamp, _marker_text(item.timestamp, previous, actions)))
        out.append(item)
        previous = item
    return out


def action_details_text(reasoning, lessons) -> str:
    """The body of an action row's "why?" details: the reasoning, then the
    lessons applied on their own line."""
    body = str(reasoning or "")
    lessons_line = lessons_text(lessons)
    if lessons_line:
        body = (body + "\n" if body else "") + "Lessons applied: " + lessons_line
    return body


def _event_row_html(item: TimelineItem) -> str:
    detail = (item.event.detail if item.event is not None else None) or {}
    if item.kind == THOUGHT:
        head, rest = first_sentence(item.text)
        return event_html(THOUGHT, head, meta=item.meta, details=("more", item.text) if rest else None)
    if item.kind == ACTION:
        body = action_details_text(detail.get("reasoning", ""), detail.get("lessons"))
        return event_html(
            ACTION,
            item.text,
            meta=item.meta,
            badge=delta_badge_html(detail.get("satisfaction_before", 0) or 0, detail.get("satisfaction_after", 0) or 0),
            icon=action_icon(str(detail.get("action", "") or "")),
            details=("why?", body) if body else None,
        )
    return event_html(item.kind, item.text, meta=item.meta)


def render_timeline(items: list[TimelineItem]) -> None:
    """Render the rows in order; an empty list shows the empty-state marker."""
    if not items:
        st.markdown(marker_html(EMPTY_TEXT), unsafe_allow_html=True)
        return
    for item in items:
        if item.kind == "marker":
            st.markdown(marker_html(item.text), unsafe_allow_html=True)
        elif item.kind == "user":
            with st.chat_message("user", avatar=icon_path("player")):
                st.write(item.text)
                st.caption(item.meta)
        elif item.kind == "jenbina":
            with st.chat_message("assistant", avatar=avatar_path()):
                st.write(item.text)
                st.caption(item.meta)
        else:
            st.markdown(_event_row_html(item), unsafe_allow_html=True)


_SCROLL_JS = """<!-- {nonce} --><script>
(function () {{
  try {{
    var doc = window.parent.document;
    var boxes = Array.prototype.slice.call(doc.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]'))
      .filter(function (el) {{ return (el.getAttribute('style') || '').indexOf('overflow') !== -1; }});
    if (boxes.length) {{ boxes[0].scrollTop = boxes[0].scrollHeight; }}
  }} catch (e) {{}}
}})();
</script>"""


def scroll_timeline_to_bottom() -> None:
    """Scroll the height-limited timeline container to its newest row. A nonce
    makes the snippet differ per rerun so the browser runs it again; when the
    container cannot be found nothing happens."""
    components.html(_SCROLL_JS.format(nonce=time.time()), height=0)
