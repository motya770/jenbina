"""Pixel-art theme: the handheld device shell CSS and the HTML helpers that
render sprites, icons and dialog boxes.

Everything here emits plain HTML strings for ``st.markdown(..., unsafe_allow_html=True)``.
Image data is embedded as base64 data URIs, cached per path for the process.
"""

from __future__ import annotations

import base64
import functools
import html
import os

import streamlit as st

from core.ui.sprites import MOTION_STATES, icon_path, sprite_path

PLACEHOLDER = "[Jenbina]"

_DIALOG_KINDS = ("thought", "action")


@functools.lru_cache(maxsize=None)
def _data_uri(path: str) -> str:
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def sprite_html(state: str, caption: str | None = None) -> str:
    """The animated 192x192 sprite for ``state`` with an optional caption.

    Unknown states resolve to the ``base`` sheet; a missing sheet file gives a
    text placeholder instead of raising.
    """
    path = sprite_path(state)
    if not os.path.isfile(path):
        return f'<div class="px-sprite-wrap"><span class="px-placeholder">{PLACEHOLDER}</span></div>'
    anim = "px-anim-motion" if state in MOTION_STATES else "px-anim-blink"
    caption_html = f'<div class="px-caption">{html.escape(caption)}</div>' if caption else ""
    return (
        '<div class="px-sprite-wrap">'
        f'<div class="px-sprite {anim}" style="background-image:url({_data_uri(path)})"></div>'
        f"{caption_html}"
        "</div>"
    )


def icon_html(name: str, alt: str = "") -> str:
    """An inline 16x16 pixel icon, or an empty span when the icon does not exist."""
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


def inject_pixel_css() -> None:
    """Inject the pixel theme. Call once per page, right after ``st.set_page_config``."""
    st.markdown(f"<style>{PIXEL_CSS}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# The theme. Colors are the table in the spec; no gradients (except the
# scanline overlay), no blur, no soft shadows, no border radius.
# --------------------------------------------------------------------------
PIXEL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

:root {
    --px-chrome: 'Press Start 2P', 'Courier New', Courier, monospace;
    --px-body: 'VT323', 'Courier New', Courier, monospace;
    --px-page: #0E0F16;
    --px-device: #2A2D3A;
    --px-bezel-hi: #3E4254;
    --px-bezel-lo: #1A1C25;
    --px-screen: #1B1F3B;
    --px-screen-edge: #5FB3B3;
    --px-text: #F2EFE6;
    --px-muted: #A9B0C3;
    --px-accent: #FF8FAB;
    --px-dialog: #10132A;
    --px-good: #6BCB77;
    --px-mid: #FFD93D;
    --px-low: #FF6B6B;
    --px-ink: #2B1B2E;
}

/* ---- page and device ------------------------------------------------- */
.stApp {
    background: #0E0F16;
    color: #F2EFE6;
}
.stApp [data-testid="stHeader"] {
    background: transparent;
}
.stApp .block-container {
    position: relative;
    max-width: 46rem;
    margin: 4.5rem auto 4rem;
    padding: 1.25rem 1.25rem 5rem;
    background: #1B1F3B;
    border: 14px solid #2A2D3A;
    outline: 4px solid #1A1C25;
    box-shadow:
        inset 0 0 0 2px #5FB3B3,
        0 0 0 8px #3E4254,
        12px 12px 0 8px #1A1C25;
}
.stApp .block-container::before {
    content: "JENBINA-16";
    position: absolute;
    top: -14px;
    left: 12px;
    line-height: 14px;
    font-family: var(--px-chrome);
    font-size: 7px;
    letter-spacing: 2px;
    color: #A9B0C3;
}
.stApp .block-container::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(0deg, rgba(0,0,0,.06) 0 1px, transparent 1px 3px);
    pointer-events: none;
    z-index: 1;
}

/* ---- sidebar: the control pad ---------------------------------------- */
[data-testid="stSidebar"] {
    background: #2A2D3A;
    border-right: 4px solid #1A1C25;
    box-shadow: inset -4px 0 0 0 #3E4254;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
    color: #F2EFE6;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 11px;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 0;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: #1B1F3B;
    box-shadow: inset 4px 0 0 0 #FF8FAB;
}
[data-testid="stSidebar"] hr {
    border: 0;
    border-top: 3px solid #1A1C25;
    box-shadow: 0 3px 0 0 #3E4254;
}

/* ---- type ------------------------------------------------------------ */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stTitle"], .stApp [data-testid="stHeading"] {
    font-family: var(--px-chrome);
    color: #FF8FAB;
    letter-spacing: 1px;
    line-height: 1.6;
    text-shadow: 3px 3px 0 #1A1C25;
}
.stApp h1 { font-size: 14px; }
.stApp h2 { font-size: 12px; }
.stApp h3, .stApp h4, .stApp h5, .stApp h6 { font-size: 11px; }
.stApp p, .stApp li,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    font-family: var(--px-body);
    font-size: 20px;
    line-height: 1.1;
    color: #F2EFE6;
}
.stApp label, .stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stCaptionContainer"] p {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
    color: #A9B0C3;
}
.stApp a {
    color: #5FB3B3;
    text-decoration: none;
    border-bottom: 2px solid #5FB3B3;
}
.stApp a:hover {
    color: #FF8FAB;
    border-bottom-color: #FF8FAB;
}
.stApp code, .stApp pre, .stApp [data-testid="stCode"] pre, .stApp [data-testid="stJson"] {
    font-family: var(--px-body);
    font-size: 18px;
    border-radius: 0;
    background: #10132A;
    color: #F2EFE6;
}
.stApp hr {
    border: 0;
    border-top: 3px solid #3E4254;
    margin: 1rem 0;
}

/* ---- buttons --------------------------------------------------------- */
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"],
.stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"],
.stApp [data-testid="stFormSubmitButton"] button {
    font-family: var(--px-chrome);
    font-size: 10px;
    border-radius: 0;
    border: 3px solid #1A1C25;
    padding: 10px 12px;
    color: #2B1B2E;
    background: #FF8FAB;
    box-shadow: inset 3px 3px 0 0 rgba(255,255,255,.35), inset -3px -3px 0 0 rgba(0,0,0,.25), 4px 4px 0 0 #1A1C25;
    transition: none;
}
.stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"] {
    background: #5FB3B3;
}
.stApp button p, .stApp button span, .stApp button div {
    font-family: var(--px-chrome) !important;
    font-size: 10px !important;
    line-height: 1.6 !important;
    color: inherit !important;
}
.stApp button[kind="primary"]:hover, .stApp button[kind="secondary"]:hover,
.stApp button[data-testid="stBaseButton-primary"]:hover,
.stApp button[data-testid="stBaseButton-secondary"]:hover {
    color: #2B1B2E;
    border-color: #1A1C25;
    background: #FFD93D;
}
.stApp button[kind="primary"]:active, .stApp button[kind="secondary"]:active,
.stApp button[data-testid="stBaseButton-primary"]:active,
.stApp button[data-testid="stBaseButton-secondary"]:active {
    transform: translate(4px, 4px);
    box-shadow: inset 3px 3px 0 0 rgba(0,0,0,.25);
}
.stApp button:focus, .stApp button:focus-visible {
    outline: 3px solid #FFD93D;
    outline-offset: 0;
    box-shadow: none;
}

/* ---- inputs ---------------------------------------------------------- */
.stApp [data-testid="stNumberInput"] [data-baseweb="input"],
.stApp [data-testid="stNumberInput"] [data-baseweb="base-input"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"],
.stApp [data-testid="stTextInput"] [data-baseweb="base-input"],
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
.stApp [data-testid="stTextArea"] [data-baseweb="base-input"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-radius: 0;
    background: #10132A;
    border-color: #5FB3B3;
}
.stApp [data-testid="stNumberInput"] [data-baseweb="input"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"],
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 3px solid #5FB3B3;
}
.stApp [data-testid="stNumberInput"] input,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] * {
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #F2EFE6;
    background: #10132A;
    border-radius: 0;
}
.stApp [data-testid="stNumberInput"] button {
    border-radius: 0;
    background: #2A2D3A;
    color: #F2EFE6;
    border-left: 3px solid #5FB3B3;
}
.stApp [data-testid="stNumberInput"] button:hover {
    background: #FF8FAB;
    color: #2B1B2E;
}
.stApp [data-testid="stCheckbox"] label span,
.stApp [data-testid="stCheckbox"] label p {
    font-family: var(--px-chrome);
    font-size: 10px;
}
.stApp [data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div {
    border-radius: 0;
}

/* ---- expanders, alerts, metrics -------------------------------------- */
.stApp [data-testid="stExpander"] {
    border-radius: 0;
}
.stApp [data-testid="stExpander"] details {
    border: 3px solid #3E4254;
    border-radius: 0;
    background: #10132A;
}
.stApp [data-testid="stExpander"] summary {
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #A9B0C3;
    border-radius: 0;
}
.stApp [data-testid="stExpander"] summary:hover {
    color: #FF8FAB;
}
.stApp [data-testid="stExpander"] summary p,
.stApp [data-testid="stExpander"] summary span {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
}
.stApp [data-testid="stAlert"] {
    border-radius: 0;
    border: 3px solid #3E4254;
    background: #10132A;
}
.stApp [data-testid="stMetricLabel"] p {
    font-family: var(--px-chrome);
    font-size: 9px;
}
.stApp [data-testid="stMetricValue"] {
    font-family: var(--px-chrome);
    font-size: 16px;
    color: #FFD93D;
}
.stApp [data-testid="stPageLink"] a,
.stApp [data-testid="stPageLink"] span {
    font-family: var(--px-chrome);
    font-size: 10px;
    border-radius: 0;
}
.stApp [data-testid="stImage"] img {
    image-rendering: pixelated;
}

/* ---- chat: the device's bottom bar and dialog rows ------------------- */
.stApp [data-testid="stBottom"] > div,
.stApp [data-testid="stBottomBlockContainer"] {
    background: #2A2D3A;
}
.stApp [data-testid="stBottomBlockContainer"] {
    border-top: 4px solid #1A1C25;
    box-shadow: inset 0 4px 0 0 #3E4254;
    max-width: 46rem;
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
}
.stApp [data-testid="stChatInput"] {
    border: 3px solid #5FB3B3;
    border-radius: 0;
    background: #10132A;
    box-shadow: 4px 4px 0 0 #1A1C25;
}
.stApp [data-testid="stChatInput"] > div,
.stApp [data-testid="stChatInput"] [data-baseweb="textarea"],
.stApp [data-testid="stChatInput"] [data-baseweb="base-input"] {
    border-radius: 0;
    border: 0;
    background: #10132A;
}
.stApp [data-testid="stChatInput"] textarea {
    font-family: var(--px-body);
    font-size: 20px;
    color: #F2EFE6;
    background: #10132A;
    caret-color: #FF8FAB;
}
.stApp [data-testid="stChatInput"] textarea::placeholder {
    color: #A9B0C3;
}
.stApp [data-testid="stChatInput"] button {
    border-radius: 0;
    color: #FF8FAB;
}
.stApp [data-testid="stChatMessage"] {
    background: #10132A;
    border: 3px solid #3E4254;
    border-radius: 0;
    padding: 10px 12px;
    margin-bottom: 10px;
    box-shadow: 4px 4px 0 0 #1A1C25;
}
.stApp [data-testid="stChatMessage"] p {
    font-family: var(--px-body);
    font-size: 20px;
}
.stApp [data-testid="stChatMessage"] img,
.stApp [data-testid="stChatMessageAvatarCustom"],
.stApp [data-testid="stChatMessageAvatarCustom"] img {
    image-rendering: pixelated;
    border-radius: 0;
    width: 40px;
    height: 40px;
}

/* ---- environment ribbon --------------------------------------------- */
.env-ribbon {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 0 0 14px;
    padding: 8px 12px;
    font-family: var(--px-chrome);
    font-size: 10px;
    letter-spacing: 1px;
    color: #A9B0C3;
    background: #10132A;
    border: 3px solid #3E4254;
    box-shadow: inset 0 -3px 0 0 #1A1C25;
}
.env-ribbon .px-icon {
    margin-right: 2px;
}

/* ---- the sprite ------------------------------------------------------ */
.px-sprite-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 6px 0 12px;
}
.px-sprite {
    width: 192px;
    height: 192px;
    background-repeat: no-repeat;
    background-size: 384px 192px;
    background-position: 0 0;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
}
.px-anim-blink {
    animation: px-blink 2.4s steps(1, end) infinite;
}
.px-anim-motion {
    animation: px-motion 1.2s steps(1, end) infinite;
}
@keyframes px-blink {
    0%   { background-position: 0 0; }
    85%  { background-position: -192px 0; }
    100% { background-position: -192px 0; }
}
@keyframes px-motion {
    0%   { background-position: 0 0; }
    50%  { background-position: -192px 0; }
    100% { background-position: -192px 0; }
}
.px-caption {
    margin-top: 8px;
    font-family: var(--px-chrome);
    font-size: 10px;
    letter-spacing: 1px;
    color: #FF8FAB;
    text-align: center;
}
.px-placeholder {
    display: block;
    padding: 84px 0;
    font-family: var(--px-chrome);
    font-size: 12px;
    color: #A9B0C3;
}

/* ---- needs bars ------------------------------------------------------ */
.need-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0;
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #F2EFE6;
}
.need-icon, .need-row .px-icon {
    width: 16px;
    height: 16px;
    flex: 0 0 16px;
}
.need-label {
    flex: 0 0 132px;
    width: 132px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #A9B0C3;
    white-space: nowrap;
    overflow: hidden;
}
.need-segs {
    display: flex;
    gap: 3px;
    flex: 1 1 auto;
    padding: 3px;
    background: #10132A;
    border: 2px solid #3E4254;
}
.need-seg {
    flex: 1 1 0;
    height: 12px;
    background: #2A2D3A;
}
.need-seg.on {
    background: #6BCB77;
}
.need-mid .need-seg.on {
    background: #FFD93D;
}
.need-critical .need-seg.on {
    background: #FF6B6B;
    animation: px-seg-blink 0.8s steps(1, end) infinite;
}
@keyframes px-seg-blink {
    0%   { opacity: 1; }
    50%  { opacity: .25; }
    100% { opacity: .25; }
}
.need-pct {
    flex: 0 0 44px;
    width: 44px;
    text-align: right;
}

/* ---- emotion chips and mood badge ------------------------------------ */
.emotion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 10px 0;
}
.emotion-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    font-family: var(--px-chrome);
    font-size: 9px;
    color: #F2EFE6;
    background: #10132A;
    border: 3px solid #5FB3B3;
    box-shadow: 3px 3px 0 0 #1A1C25;
}
.mood-badge {
    display: inline-block;
    padding: 8px 10px;
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #2B1B2E;
    border: 3px solid #1A1C25;
    box-shadow: 3px 3px 0 0 #1A1C25;
}
.mood-positive { background: #6BCB77; }
.mood-negative { background: #FF6B6B; }

/* ---- dialog boxes ---------------------------------------------------- */
.px-dialog {
    position: relative;
    margin: 18px 0 20px;
    padding: 12px 16px;
    font-family: var(--px-body);
    font-size: 20px;
    line-height: 1.1;
    color: #F2EFE6;
    background: #10132A;
    border: 3px solid #F2EFE6;
    box-shadow: 0 0 0 3px #10132A, 6px 6px 0 3px #1A1C25;
}
.px-dialog-thought::before {
    content: "";
    position: absolute;
    top: -15px;
    left: 50%;
    width: 6px;
    height: 6px;
    background: #F2EFE6;
    box-shadow: -8px -8px 0 0 #F2EFE6, -14px -18px 0 0 #F2EFE6;
}
.px-dialog-action::before {
    content: "";
    position: absolute;
    top: -9px;
    left: 24px;
    width: 12px;
    height: 6px;
    background: #F2EFE6;
    box-shadow: 3px -6px 0 0 #F2EFE6;
}
.px-dialog-action .action-title {
    margin: 0 0 8px;
    font-family: var(--px-chrome);
    font-size: 11px;
    line-height: 1.8;
    letter-spacing: 1px;
    color: #FF8FAB;
}
.px-dialog-action .action-reasoning {
    margin: 0 0 8px;
    color: #A9B0C3;
}
.px-dialog-action .action-lessons {
    margin: 0 0 8px;
    color: #F2EFE6;
}
.satisfaction-delta {
    display: inline-block;
    padding: 6px 8px;
    font-family: var(--px-chrome);
    font-size: 9px;
    color: #2B1B2E;
    border: 2px solid #1A1C25;
}
.delta-positive { background: #6BCB77; }
.delta-negative { background: #FF6B6B; }
.delta-neutral  { background: #A9B0C3; }

/* ---- icons ----------------------------------------------------------- */
.px-icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    vertical-align: middle;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
}
.px-icon-missing {
    background: transparent;
}
"""
