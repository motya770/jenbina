"""The UI theme: the page CSS and the HTML helpers for timeline rows,
markers, the stage pill, sprites, icons and dialog boxes.

The skin is "Blade Runner 2049, hologram look" (docs/plans/2026-11-14-blade-runner-theme-redesign.md):
violet-black smoke, a magenta and violet glow behind the page, hologram pink for
Jenbina, teal for the system and the user, periwinkle for strong feeling. The module
keeps its old name and ``px-`` class names so callers, tests and E2E selectors keep
working. The pixel sprite and icon helpers stay for pages that still use them; the
home screen no longer does.

Everything here emits plain HTML strings for ``st.markdown(..., unsafe_allow_html=True)``.
Image data is embedded as base64 data URIs, cached per path for the process.
"""

from __future__ import annotations

import base64
import functools
import html
import os
import re

import streamlit as st

from core.ui.sprites import ICONS, MOTION_STATES, icon_path, sprite_path

PLACEHOLDER = "[Jenbina]"

_DIALOG_KINDS = ("thought", "action")


@functools.lru_cache(maxsize=None)
def _data_uri(path: str) -> str:
    """Base64 data URI of a committed asset, cached for the process lifetime.

    Assets are never rebuilt at runtime; rebuilding them under a running app
    needs a restart to be seen.
    """
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def sprite_html(state: str, caption: str | None = None, scale: int = 4) -> str:
    """The animated sprite for ``state`` with an optional caption.

    ``scale`` 4 is the 192px hero sprite; ``scale`` 2 is the 96px badge laid
    out in a row with its caption. Unknown states resolve to the ``base``
    sheet; a missing sheet file gives a text placeholder instead of raising.
    """
    small = scale == 2
    wrap_class = "px-sprite-wrap px-wrap-2x" if small else "px-sprite-wrap"
    path = sprite_path(state)
    if not os.path.isfile(path):
        return f'<div class="{wrap_class}"><span class="px-placeholder">{PLACEHOLDER}</span></div>'
    anim = "px-anim-motion" if state in MOTION_STATES else "px-anim-blink"
    size_class = " px-sprite-2x" if small else ""
    caption_html = f'<div class="px-caption">{html.escape(caption)}</div>' if caption else ""
    return (
        f'<div class="{wrap_class}">'
        f'<div class="px-sprite{size_class} {anim}" style="background-image:url({_data_uri(path)})"></div>'
        f"{caption_html}"
        "</div>"
    )


def icon_html(name: str, alt: str = "") -> str:
    """An inline 16x16 pixel icon, or an empty span when the icon does not exist.

    Only names in ``ICONS`` reach the filesystem, so a caller-supplied name can
    never resolve to another file or fill the data-URI cache.
    """
    if name not in ICONS:
        return '<span class="px-icon px-icon-missing"></span>'
    path = icon_path(name)
    if not os.path.isfile(path):
        return '<span class="px-icon px-icon-missing"></span>'
    return f'<img class="px-icon" alt="{html.escape(alt, quote=True)}" src="{_data_uri(path)}">'


def dialog_html(body: str, kind: str = "thought") -> str:
    """An RPG dialog box around escaped ``body`` text (newlines become ``<br>``)."""
    if kind not in _DIALOG_KINDS:
        kind = "thought"
    text = html.escape(body).replace("\n", "<br>")
    return f'<div class="px-dialog px-dialog-{kind}">{text}</div>'


# Event kind -> 8x8 icon name, kept for callers that still pick icons
# (``action_icon``). Timeline rows show a text tag instead (``EVENT_TAGS``).
EVENT_ICONS = {
    "thought": "thought",
    "action": "act",
    "mood": "mood",
    "goal": "esteem",
    "plan": "plan",
    "move": "walk",
}
GENERIC_EVENT_ICON = "act"

# Event kind -> the short mono tag at the start of a timeline row.
EVENT_TAGS = {
    "thought": "THINK",
    "action": "ACT",
    "mood": "MOOD",
    "goal": "GOAL",
    "plan": "PLAN",
    "move": "MOVE",
}
GENERIC_EVENT_TAG = "EVENT"

# First matching group wins.
_ACTION_ICON_KEYWORDS = (
    (("eat", "food", "meal", "snack", "cook", "breakfast", "lunch", "dinner"), "hunger"),
    (("drink", "coffee", "tea", "water"), "drink"),
    (("sleep", "nap", "rest"), "sleep"),
    (("walk", "stroll", "visit", "go to", "wander", "explor", "hike"), "walk"),
    (("talk", "chat", "call", "friend", "social", "music", "convers"), "love"),
    (("read", "study", "learn", "book"), "self_actualization"),
)


def action_icon(action: str) -> str:
    """The icon name for an action's row, by keyword; the star when none fits."""
    text = (action or "").lower()
    for keywords, icon in _ACTION_ICON_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return icon
    return GENERIC_EVENT_ICON


def event_html(kind: str, title: str, meta: str = "", details: tuple | None = None,
               badge: str | None = None, icon: str | None = None) -> str:
    """One timeline row for a life event: a kind tag, the title, then badge and meta.

    ``details`` is ``(summary, body)`` rendered as a native ``<details>``;
    ``badge`` is trusted HTML (build it with ``delta_badge_html``). ``icon`` is
    accepted for backward compatibility and ignored: rows carry a text tag
    (``EVENT_TAGS``) instead of a pixel icon. Everything else is escaped.
    """
    kind_token = re.sub(r"[^a-z0-9_]", "", str(kind).lower())
    tag = EVENT_TAGS.get(kind_token, GENERIC_EVENT_TAG)
    parts = [
        f'<span class="px-event-tag">{tag}</span>',
        f'<span class="px-event-title">{html.escape(title)}</span>',
    ]
    if badge:
        parts.append(badge)
    if meta:
        parts.append(f'<span class="px-event-meta">{html.escape(meta)}</span>')
    if details:
        summary, body = details
        body_html = html.escape(body).replace("\n", "<br>")
        parts.append(
            f"<details><summary>{html.escape(summary)}</summary>"
            f'<div class="px-event-body">{body_html}</div></details>'
        )
    return f'<div class="px-event px-event-{kind_token}">' + "".join(parts) + "</div>"


def delta_badge_html(before: float, after: float) -> str:
    """The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests."""
    delta = round(float(after) - float(before), 1) or 0.0
    if delta > 0:
        cls = "delta-positive"
    elif delta < 0:
        cls = "delta-negative"
    else:
        cls = "delta-neutral"
    return (
        f'<span class="satisfaction-delta {cls}" data-before="{float(before):g}" '
        f'data-after="{float(after):g}" data-delta="{delta:.1f}">'
        f"{float(before):.0f}% → {float(after):.0f}% ({delta:+.1f}%)</span>"
    )


def marker_html(text: str) -> str:
    """A centered time/place divider between timeline rows."""
    return f'<div class="px-marker">{html.escape(text)}</div>'


def stage_pill_html(text: str) -> str:
    """The system stage pill in the status rail."""
    return f'<span class="px-stage">{html.escape(text)}</span>'


def portrait_caption_html(caption: str) -> str:
    """The name strip under the rail portrait."""
    return f'<div class="px-portrait-cap">{html.escape(caption)}</div>'


def inject_pixel_css(wide: bool = False) -> None:
    """Inject the theme. Call once per page, right after ``st.set_page_config``.

    ``wide=True`` widens the page to 64rem for the two-column home screen.
    """
    css = PIXEL_CSS + (WIDE_CSS if wide else "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


WIDE_CSS = """
.stApp .block-container { max-width: 64rem; }
"""




# --------------------------------------------------------------------------
# The theme: Blade Runner 2049, hologram look. Token values are the
# "Hologram look" table in the spec. Portraits are never filtered or tinted.
# --------------------------------------------------------------------------
PIXEL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;1,400&family=Rajdhani:wght@500;600&display=swap');

:root {
    --br-smoke: #0A0710;
    --br-haze: #140D1C;
    --br-dust: #21152D;
    --br-line: #3A2650;
    --br-text: #F3E8F3;
    --br-muted: #A795B3;
    --br-her: #FF5FC1;
    --br-ice: #62D2DA;
    --br-joi: #8C96FF;
    --br-rust: #FF7850;
    --her-rgb: 255, 95, 193;
    --ice-rgb: 98, 210, 218;
    --joi-rgb: 140, 150, 255;
    --rust-rgb: 255, 120, 80;
    --br-display: 'Rajdhani', 'Arial Narrow', system-ui, sans-serif;
    --br-body: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
    --br-data: 'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace;
}

/* ---- page: smoke with a magenta and violet glow ------------------------ */
.stApp {
    background:
        radial-gradient(64rem 40rem at 92% 0%, rgba(255, 60, 170, .42), transparent 65%),
        radial-gradient(48rem 40rem at 70% 45%, rgba(255, 60, 170, .14), transparent 70%),
        radial-gradient(56rem 44rem at -8% 35%, rgba(120, 70, 235, .40), transparent 65%),
        radial-gradient(56rem 36rem at 40% 105%, rgba(90, 110, 255, .28), transparent 65%),
        var(--br-smoke);
    background-attachment: fixed;
    color: var(--br-text);
}
.stApp [data-testid="stHeader"] {
    background: transparent;
}
.stApp [data-testid="stHeader"] *,
.stApp [data-testid="stToolbar"] * {
    color: var(--br-muted);
}
.stApp .block-container {
    max-width: 46rem;
    padding-top: 3.5rem;
    padding-bottom: 4rem;
}

/* ---- type ------------------------------------------------------------ */
.stApp, .stApp p, .stApp li, .stApp input, .stApp textarea,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    font-family: var(--br-body);
}
.stApp p, .stApp li,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    font-size: 15px;
    line-height: 1.55;
    color: var(--br-text);
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stHeading"] {
    font-family: var(--br-display);
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--br-text);
    line-height: 1.2;
}
.stApp h1 { font-size: 28px; }
.stApp h2 { font-size: 20px; }
.stApp h3, .stApp h4, .stApp h5, .stApp h6 { font-size: 16px; color: var(--br-her); }
.stApp label, .stApp [data-testid="stWidgetLabel"] p {
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--br-muted);
}
.stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stCaptionContainer"] {
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .04em;
    color: var(--br-muted);
}
.stApp a {
    color: var(--br-ice);
    text-decoration: none;
    border-bottom: 1px solid rgba(var(--ice-rgb), .4);
}
.stApp a:hover {
    color: var(--br-her);
    border-bottom-color: var(--br-her);
}
.stApp code, .stApp pre, .stApp [data-testid="stCode"] pre, .stApp [data-testid="stJson"] {
    font-family: var(--br-data);
    font-size: 13px;
    border-radius: 2px;
    background: var(--br-dust);
    color: var(--br-text);
}
.stApp hr {
    border: 0;
    border-top: 1px solid var(--br-line);
    margin: 1rem 0;
}

/* ---- sidebar --------------------------------------------------------- */
.stApp [data-testid="stSidebar"] {
    background: rgba(10, 7, 16, .92);
    border-right: 1px solid var(--br-line);
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stSidebar"] label,
.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--br-text);
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 2px;
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(var(--her-rgb), .10);
    box-shadow: inset 2px 0 0 0 var(--br-her);
}

/* ---- buttons --------------------------------------------------------- */
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"],
.stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"],
.stApp [data-testid="stFormSubmitButton"] button {
    border-radius: 2px;
    border: 1px solid var(--br-her);
    padding: 8px 12px;
    background: transparent;
    color: var(--br-her);
    box-shadow: none;
    transition: background .15s ease, filter .15s ease;
}
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"] {
    background: var(--br-her);
    color: var(--br-smoke);
}
.stApp button[kind="primary"] p, .stApp button[kind="secondary"] p,
.stApp button[data-testid="stBaseButton-primary"] p,
.stApp button[data-testid="stBaseButton-secondary"] p,
.stApp [data-testid="stFormSubmitButton"] button p {
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: inherit;
}
.stApp button[kind="secondary"]:hover, .stApp button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(var(--her-rgb), .14);
    color: var(--br-her);
    border-color: var(--br-her);
}
.stApp button[kind="primary"]:hover, .stApp button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(1.1);
    color: var(--br-smoke);
    border-color: var(--br-her);
}
.stApp button:focus-visible {
    outline: 1px solid var(--br-her);
    outline-offset: 2px;
    box-shadow: none;
}

/* ---- inputs ---------------------------------------------------------- */
.stApp [data-testid="stNumberInput"] [data-baseweb="input"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"],
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-radius: 2px;
    border: 1px solid var(--br-line);
    background: var(--br-dust);
}
.stApp [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
.stApp [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within {
    border-color: rgba(var(--her-rgb), .6);
}
.stApp [data-testid="stNumberInput"] [data-baseweb="base-input"],
.stApp [data-testid="stTextInput"] [data-baseweb="base-input"],
.stApp [data-testid="stTextArea"] [data-baseweb="base-input"],
.stApp [data-testid="stNumberInput"] input,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea {
    background: var(--br-dust);
    color: var(--br-text);
    caret-color: var(--br-her);
}
.stApp [data-testid="stNumberInput"] input {
    font-family: var(--br-data);
    font-size: 13px;
}
.stApp [data-testid="stNumberInput"] button {
    border-radius: 0;
    background: var(--br-dust);
    color: var(--br-muted);
    border-left: 1px solid var(--br-line);
}
.stApp [data-testid="stNumberInput"] button:hover {
    background: rgba(var(--her-rgb), .14);
    color: var(--br-her);
}

/* ---- the timeline filter (horizontal st.radio) as mono chips ---------- */
.stApp [data-testid="stRadio"] [role="radiogroup"] {
    gap: 4px;
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label {
    margin: 0;
    padding: 3px 9px;
    border: 1px solid transparent;
    border-radius: 2px;
    cursor: pointer;
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    display: none;
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label p {
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--br-muted);
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label:hover p {
    color: var(--br-text);
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    border-color: rgba(var(--ice-rgb), .4);
    background: rgba(var(--ice-rgb), .12);
}
.stApp [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) p {
    color: var(--br-ice);
}

/* ---- tabs (the mind card) -------------------------------------------- */
.stApp [data-baseweb="tab-list"] {
    gap: 16px;
    border-bottom: 1px solid var(--br-line);
}
.stApp [data-baseweb="tab"] {
    background: transparent;
    padding: 0 0 8px;
}
.stApp [data-baseweb="tab"] p {
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 12px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--br-muted);
}
.stApp [data-baseweb="tab"][aria-selected="true"] p {
    color: var(--br-text);
}
.stApp [data-baseweb="tab-highlight"] {
    background: var(--br-her);
    height: 2px;
}
.stApp [data-baseweb="tab-border"] {
    display: none;
}

/* ---- expanders, alerts, metrics -------------------------------------- */
.stApp [data-testid="stExpander"] details {
    border: 1px solid var(--br-line);
    border-radius: 2px;
    background: rgba(20, 13, 28, .86);
}
.stApp [data-testid="stExpander"] summary p,
.stApp [data-testid="stExpander"] summary span {
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--br-text);
}
.stApp [data-testid="stExpander"] summary:hover p {
    color: var(--br-her);
}
.stApp [data-testid="stAlert"] {
    border-radius: 2px;
}
.stApp [data-testid="stMetricLabel"] p {
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--br-muted);
}
.stApp [data-testid="stMetricValue"] {
    font-family: var(--br-data);
    color: var(--br-her);
}

/* ---- portraits: shown exactly as drawn, in a thin frame --------------- */
.stApp [data-testid="stImage"] img {
    border: 1px solid var(--br-line);
    border-radius: 2px;
}
.px-portrait-cap {
    margin: 6px 0 4px;
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 16px;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--br-her);
}

/* ---- chat: messages and input ---------------------------------------- */
.stApp [data-testid="stBottom"] > div,
.stApp [data-testid="stBottomBlockContainer"] {
    background: transparent;
}
.stApp [data-testid="stChatInput"] {
    border: 1px solid var(--br-line);
    border-radius: 2px;
    background: var(--br-dust);
}
.stApp [data-testid="stChatInput"]:focus-within {
    border-color: rgba(var(--her-rgb), .6);
    box-shadow: 0 0 0 3px rgba(var(--her-rgb), .14);
}
.stApp [data-testid="stChatInput"] > div,
.stApp [data-testid="stChatInput"] [data-baseweb="textarea"],
.stApp [data-testid="stChatInput"] [data-baseweb="base-input"] {
    border: 0;
    border-radius: 2px;
    background: var(--br-dust);
}
.stApp [data-testid="stChatInput"] textarea {
    font-family: var(--br-body);
    font-size: 15px;
    color: var(--br-text);
    background: var(--br-dust);
    caret-color: var(--br-her);
}
.stApp [data-testid="stChatInput"] textarea::placeholder {
    color: var(--br-muted);
}
.stApp [data-testid="stChatInput"] button {
    color: var(--br-her);
}
.stApp [data-testid="stChatMessage"] {
    background: var(--br-dust);
    border-left: 2px solid var(--br-her);
    border-radius: 2px;
    padding: 10px 14px;
    margin: 0 12% 12px 0;
    box-shadow: 0 0 24px rgba(var(--her-rgb), .08);
}
.stApp [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    text-align: right;
    margin: 0 0 12px 12%;
    background: transparent;
    border: 1px solid rgba(var(--ice-rgb), .45);
    box-shadow: none;
}
.stApp [data-testid="stChatMessage"] p {
    font-size: 15px;
    color: var(--br-text);
}
.stApp [data-testid="stChatMessageAvatarCustom"],
.stApp [data-testid="stChatMessageAvatarCustom"] img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    object-position: 50% 25%;
}
.stApp [data-testid="stChatMessageAvatarCustom"] {
    border: 1px solid rgba(var(--her-rgb), .6);
    box-shadow: 0 0 12px rgba(var(--her-rgb), .25);
}
.stApp [data-testid="stChatMessageAvatarUser"] {
    border-radius: 50%;
    background: transparent;
    border: 1px solid var(--br-ice);
    color: var(--br-ice);
}

/* ---- environment ribbon (Environment page) ---------------------------- */
.env-ribbon {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 0 0 14px;
    padding: 8px 12px;
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--br-ice);
    border: 1px solid var(--br-line);
    border-radius: 2px;
}

/* ---- legacy pixel sprite (kept for pages that still call sprite_html) - */
.px-sprite-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 6px 0 12px;
}
.px-wrap-2x {
    flex-direction: row;
    justify-content: center;
    gap: 14px;
}
.px-sprite {
    width: var(--px-frame, 192px);
    height: var(--px-frame, 192px);
    flex: 0 0 auto;
    background-repeat: no-repeat;
    background-size: calc(var(--px-frame, 192px) * 2) var(--px-frame, 192px);
    background-position: 0 0;
    image-rendering: pixelated;
}
.px-sprite-2x {
    --px-frame: 96px;
}
.px-anim-blink {
    animation: px-blink 2.4s steps(1, end) infinite;
}
.px-anim-motion {
    animation: px-motion 1.2s steps(1, end) infinite;
}
@keyframes px-blink {
    0%   { background-position: 0 0; }
    85%  { background-position: calc(var(--px-frame, 192px) * -1) 0; }
    100% { background-position: calc(var(--px-frame, 192px) * -1) 0; }
}
@keyframes px-motion {
    0%   { background-position: 0 0; }
    50%  { background-position: calc(var(--px-frame, 192px) * -1) 0; }
    100% { background-position: calc(var(--px-frame, 192px) * -1) 0; }
}
.px-caption, .px-placeholder {
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--br-her);
}
.px-placeholder {
    display: block;
    padding: 36px 0;
}

/* ---- needs bars: thin glowing lines ----------------------------------- */
.need-row {
    display: grid;
    grid-template-columns: 6.5rem minmax(0, 1fr) 2.6rem;
    gap: 10px;
    align-items: center;
    margin: 7px 0;
    font-size: 13px;
}
.need-label {
    color: var(--br-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.need-bar {
    height: 3px;
    background: var(--br-line);
    border-radius: 2px;
    overflow: hidden;
}
.need-fill {
    display: block;
    height: 100%;
    background: var(--br-her);
    box-shadow: 0 0 8px rgba(var(--her-rgb), .5);
}
.need-critical .need-fill {
    background: var(--br-rust);
    box-shadow: 0 0 8px rgba(var(--rust-rgb), .5);
}
.need-pct {
    font-family: var(--br-data);
    font-size: 11px;
    text-align: right;
    font-variant-numeric: tabular-nums;
    color: var(--br-text);
}
.need-critical .need-pct {
    color: var(--br-rust);
}

/* ---- emotion chips and mood badge ------------------------------------- */
.emotion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 10px 0;
}
.emotion-chip, .mood-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    font-family: var(--br-data);
    font-size: 11px;
    color: var(--br-muted);
    border: 1px solid var(--br-line);
    border-radius: 2px;
}
.emotion-chip.emotion-dominant {
    color: var(--br-joi);
    border-color: rgba(var(--joi-rgb), .5);
    box-shadow: 0 0 12px rgba(var(--joi-rgb), .15);
}
.mood-badge {
    font-size: 12px;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.mood-positive {
    color: var(--br-her);
    border-color: rgba(var(--her-rgb), .5);
}
.mood-negative {
    color: var(--br-joi);
    border-color: rgba(var(--joi-rgb), .5);
}

/* ---- dialog boxes (legacy, Environment and Debug pages) ---------------- */
.px-dialog {
    margin: 14px 0;
    padding: 10px 14px;
    color: var(--br-text);
    background: var(--br-dust);
    border-left: 2px solid var(--br-her);
    border-radius: 2px;
}
.px-dialog-thought {
    font-style: italic;
    color: var(--br-muted);
    background: transparent;
    border-left-width: 1px;
}
.px-dialog-action .action-title {
    margin: 0 0 8px;
    font-family: var(--br-display);
    font-weight: 600;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--br-her);
}
.px-dialog-action .action-reasoning {
    color: var(--br-muted);
}
.satisfaction-delta {
    font-family: var(--br-data);
    font-size: 11px;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
    color: var(--br-muted);
}
.delta-positive { color: var(--br-her); }
.delta-negative { color: var(--br-rust); }
.delta-neutral  { color: var(--br-muted); }

/* ---- timeline rows, markers, stage pill ------------------------------ */
.px-event {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    column-gap: 10px;
    row-gap: 2px;
    margin: 6px 0 6px 44px;
    padding: 5px 0;
    border-top: 1px dashed rgba(58, 38, 80, .9);
    font-size: 15px;
    line-height: 1.5;
    color: var(--br-text);
}
.px-event-tag {
    flex: 0 0 44px;
    font-family: var(--br-data);
    font-size: 10px;
    letter-spacing: .1em;
    color: var(--br-ice);
}
.px-event-mood .px-event-tag {
    color: var(--br-joi);
}
.px-event-title {
    flex: 1 1 12rem;
    min-width: 0;
}
.px-event-meta {
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .04em;
    color: var(--br-muted);
    white-space: nowrap;
}
.px-event-thought {
    border-top: 0;
    border-left: 1px solid rgba(var(--her-rgb), .55);
    padding: 2px 0 2px 14px;
}
.px-event-thought .px-event-tag {
    display: none;
}
.px-event-thought .px-event-title {
    font-style: italic;
    color: var(--br-muted);
}
.px-event details {
    flex: 1 0 100%;
    padding-left: 54px;
}
.px-event-thought details {
    padding-left: 0;
}
.px-event summary {
    font-family: var(--br-data);
    font-size: 11px;
    color: var(--br-her);
    cursor: pointer;
}
.px-event-body {
    margin-top: 4px;
    font-size: 14px;
    color: var(--br-muted);
}
.px-marker {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 16px 0 8px;
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--br-ice);
}
.px-marker::before, .px-marker::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(var(--ice-rgb), .35), transparent);
}
.px-stage {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 3px 10px;
    font-family: var(--br-data);
    font-size: 10px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--br-ice);
    border: 1px solid rgba(var(--ice-rgb), .4);
    border-radius: 999px;
}
.px-stage::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
    animation: br-pulse 1.6s ease-in-out infinite;
}
@keyframes br-pulse {
    50% { opacity: .25; }
}
@media (prefers-reduced-motion: reduce) {
    .px-stage::before, .px-anim-blink, .px-anim-motion { animation: none; }
}

/* ---- bordered containers (the timeline box and the rail's cards) ------ */
/* Streamlit 1.38 styles bordered/height-limited containers through a generated
   emotion class; wrappers without styles carry the "-0" class, so everything
   else is a card. */
.stApp [data-testid="stVerticalBlockBorderWrapper"]:not(.st-emotion-cache-0) {
    border: 1px solid var(--br-line);
    border-radius: 2px;
    background: rgba(20, 13, 28, .86);
    backdrop-filter: blur(6px);
    padding: 12px 14px;
}

/* ---- status rail ----------------------------------------------------- */
.px-card-title {
    margin: 0 0 8px;
    font-family: var(--br-display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--br-text);
}
.px-env-line {
    margin: 6px 0 8px;
    font-family: var(--br-data);
    font-size: 11px;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--br-ice);
}
.px-now-lines {
    margin: 6px 0 10px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--br-text);
}

/* ---- icons (legacy) --------------------------------------------------- */
.px-icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    vertical-align: middle;
    image-rendering: pixelated;
}
.px-icon-missing {
    background: transparent;
}
"""
