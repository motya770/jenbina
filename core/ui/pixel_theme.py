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

from core.ui.sprites import ICONS, MOTION_STATES, icon_path, sprite_path

PLACEHOLDER = "[Jenbina]"

_DIALOG_KINDS = ("thought", "action")


@functools.lru_cache(maxsize=None)
def _data_uri(path: str) -> str:
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


def inject_pixel_css() -> None:
    """Inject the pixel theme. Call once per page, right after ``st.set_page_config``."""
    st.markdown(f"<style>{PIXEL_CSS}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# The theme: "candy arcade". Colors are the revision-2 table in the spec; no
# gradients (except the scanline overlay), no blur, no border radius.
# --------------------------------------------------------------------------
PIXEL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

:root {
    --px-chrome: 'Press Start 2P', 'Courier New', Courier, monospace;
    --px-body: 'VT323', 'Courier New', Courier, monospace;
    --px-page: #22184A;
    --px-device: #FF6B9D;
    --px-bezel-hi: #FFA8C9;
    --px-bezel-lo: #B3285C;
    --px-screen: #4FC3F7;
    --px-ink: #1E1B3A;
    --px-muted: #4A4670;
    --px-panel: #FFF6D5;
    --px-panel-2: #E8DCC0;
    --px-pad: #2A1F5E;
    --px-accent: #FF3E8A;
    --px-accent-deep: #C2185B;
    --px-yellow: #FFD93D;
    --px-green: #5BE36A;
    --px-purple: #9B6BFF;
    --px-orange: #FF8C42;
    --px-teal: #2EC4B6;
    --px-blue: #3A86FF;
    --px-red: #FF4757;
    --px-frame: 192px;
}

/* ---- page and device ------------------------------------------------- */
.stApp {
    background: #22184A;
    color: #1E1B3A;
}
.stApp [data-testid="stHeader"] {
    background: #22184A;
}
.stApp [data-testid="stHeader"] *,
.stApp [data-testid="stToolbar"] * {
    color: #FFF6D5;
}
.stApp .block-container {
    position: relative;
    max-width: 46rem;
    margin: 4.5rem auto 4rem;
    padding: 1.25rem 1.25rem 5rem;
    background: #4FC3F7;
    border: 14px solid #FF6B9D;
    outline: 4px solid #B3285C;
    box-shadow:
        inset 0 0 0 2px #FFFFFF,
        0 0 0 8px #FFA8C9,
        12px 12px 0 8px #B3285C;
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
    color: #FFF6D5;
}
.stApp .block-container::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(0deg, rgba(0,0,0,.06) 0 1px, transparent 1px 3px);
    pointer-events: none;
    z-index: 1;
}

/* ---- type ------------------------------------------------------------ */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stHeading"] {
    font-family: var(--px-chrome);
    color: #FF3E8A;
    letter-spacing: 1px;
    line-height: 1.6;
    text-shadow: 3px 3px 0 #1E1B3A;
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
    color: #1E1B3A;
}
.stApp label, .stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stCaptionContainer"] p {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
    color: #1E1B3A;
}
.stApp a {
    color: #C2185B;
    text-decoration: none;
    border-bottom: 2px solid #C2185B;
}
.stApp a:hover {
    color: #FF3E8A;
    border-bottom-color: #FF3E8A;
}
.stApp code, .stApp pre, .stApp [data-testid="stCode"] pre, .stApp [data-testid="stJson"] {
    font-family: var(--px-body);
    font-size: 18px;
    border-radius: 0;
    background: #FFF6D5;
    color: #1E1B3A;
}
.stApp hr {
    border: 0;
    border-top: 3px solid #1E1B3A;
    margin: 1rem 0;
}

/* ---- sidebar: the control pad ---------------------------------------- */
.stApp [data-testid="stSidebar"] {
    background: #2A1F5E;
    border-right: 4px solid #140E33;
    box-shadow: inset -4px 0 0 0 #3D2F7A;
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stSidebar"] label,
.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
    color: #FFF6D5;
}
.stApp [data-testid="stSidebar"] h1, .stApp [data-testid="stSidebar"] h2, .stApp [data-testid="stSidebar"] h3 {
    font-size: 11px;
    color: #FFD93D;
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 0;
}
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
.stApp [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: #140E33;
    box-shadow: inset 4px 0 0 0 #FF3E8A;
}
.stApp [data-testid="stSidebar"] hr {
    border: 0;
    border-top: 3px solid #140E33;
    box-shadow: 0 3px 0 0 #3D2F7A;
}
.stApp [data-testid="stSidebar"] [data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div {
    border-color: #FFF6D5;
}

/* ---- buttons --------------------------------------------------------- */
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"],
.stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"],
.stApp [data-testid="stFormSubmitButton"] button {
    font-family: var(--px-chrome);
    font-size: 10px;
    border-radius: 0;
    border: 3px solid #1E1B3A;
    padding: 10px 12px;
    color: #1E1B3A;
    background: #FF3E8A;
    box-shadow: inset 3px 3px 0 0 rgba(255,255,255,.4), inset -3px -3px 0 0 rgba(0,0,0,.25), 4px 4px 0 0 #1E1B3A;
    transition: none;
}
.stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"] {
    background: #5BE36A;
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
    color: #1E1B3A;
    border-color: #1E1B3A;
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
    background: #FFF6D5;
    border-color: #1E1B3A;
}
.stApp [data-testid="stNumberInput"] [data-baseweb="input"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"],
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"],
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 3px solid #1E1B3A;
}
.stApp [data-testid="stNumberInput"] input,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea,
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] * {
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #1E1B3A;
    background: #FFF6D5;
    border-radius: 0;
}
.stApp [data-testid="stNumberInput"] button {
    border-radius: 0;
    background: #FF3E8A;
    color: #1E1B3A;
    border-left: 3px solid #1E1B3A;
}
.stApp [data-testid="stNumberInput"] button:hover {
    background: #FFD93D;
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
    border: 3px solid #1E1B3A;
    border-radius: 0;
    background: #FFF6D5;
    box-shadow: 4px 4px 0 0 #1E1B3A;
}
.stApp [data-testid="stExpander"] summary {
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #1E1B3A;
    border-radius: 0;
}
.stApp [data-testid="stExpander"] summary:hover {
    color: #C2185B;
}
.stApp [data-testid="stExpander"] summary p,
.stApp [data-testid="stExpander"] summary span {
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
}
.stApp [data-testid="stAlert"] {
    border-radius: 0;
    border: 3px solid #1E1B3A;
    background: #FFF6D5;
    color: #1E1B3A;
}
.stApp [data-testid="stMetricLabel"] p {
    font-family: var(--px-chrome);
    font-size: 9px;
}
.stApp [data-testid="stMetricValue"] {
    font-family: var(--px-chrome);
    font-size: 16px;
    color: #C2185B;
}
.stApp [data-testid="stPageLink"] a,
.stApp [data-testid="stPageLink"] span {
    font-family: var(--px-chrome);
    font-size: 10px;
    border-radius: 0;
}

/* ---- the portrait window (st.image) ---------------------------------- */
.stApp [data-testid="stImage"] {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 10px 0 18px;
}
.stApp [data-testid="stImage"] img {
    image-rendering: auto;
    border: 4px solid #1E1B3A;
    background: #FFF6D5;
    box-shadow: 0 0 0 4px #FFF6D5, 8px 8px 0 4px #1E1B3A;
}

/* ---- chat: the device's bottom bar and dialog rows ------------------- */
.stApp [data-testid="stBottom"] > div,
.stApp [data-testid="stBottomBlockContainer"] {
    background: #FF6B9D;
}
.stApp [data-testid="stBottomBlockContainer"] {
    border-top: 4px solid #B3285C;
    box-shadow: inset 0 4px 0 0 #FFA8C9;
    max-width: 46rem;
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
}
.stApp [data-testid="stChatInput"] {
    border: 3px solid #1E1B3A;
    border-radius: 0;
    background: #FFF6D5;
    box-shadow: 4px 4px 0 0 #1E1B3A;
}
.stApp [data-testid="stChatInput"] > div,
.stApp [data-testid="stChatInput"] [data-baseweb="textarea"],
.stApp [data-testid="stChatInput"] [data-baseweb="base-input"] {
    border-radius: 0;
    border: 0;
    background: #FFF6D5;
}
.stApp [data-testid="stChatInput"] textarea {
    font-family: var(--px-body);
    font-size: 20px;
    color: #1E1B3A;
    background: #FFF6D5;
    caret-color: #FF3E8A;
}
.stApp [data-testid="stChatInput"] textarea::placeholder {
    color: #4A4670;
}
.stApp [data-testid="stChatInput"] button {
    border-radius: 0;
    color: #C2185B;
}
.stApp [data-testid="stChatMessage"] {
    background: #FFF6D5;
    border: 3px solid #1E1B3A;
    border-radius: 0;
    padding: 10px 12px;
    margin-bottom: 10px;
    box-shadow: 4px 4px 0 0 #1E1B3A;
}
.stApp [data-testid="stChatMessage"] p {
    font-family: var(--px-body);
    font-size: 20px;
    color: #1E1B3A;
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
    color: #1E1B3A;
    background: #FFF6D5;
    border: 3px solid #1E1B3A;
    box-shadow: inset 0 -3px 0 0 #E8DCC0, 4px 4px 0 0 #1E1B3A;
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
.px-wrap-2x {
    flex-direction: row;
    justify-content: center;
    gap: 14px;
    margin: 0 0 16px;
    padding: 8px 14px;
    background: #FFF6D5;
    border: 3px solid #1E1B3A;
    box-shadow: 4px 4px 0 0 #1E1B3A;
}
.px-sprite {
    width: var(--px-frame);
    height: var(--px-frame);
    flex: 0 0 auto;
    background-repeat: no-repeat;
    background-size: calc(var(--px-frame) * 2) var(--px-frame);
    background-position: 0 0;
    image-rendering: crisp-edges;
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
    85%  { background-position: calc(var(--px-frame) * -1) 0; }
    100% { background-position: calc(var(--px-frame) * -1) 0; }
}
@keyframes px-motion {
    0%   { background-position: 0 0; }
    50%  { background-position: calc(var(--px-frame) * -1) 0; }
    100% { background-position: calc(var(--px-frame) * -1) 0; }
}
.px-caption {
    margin-top: 8px;
    font-family: var(--px-chrome);
    font-size: 10px;
    line-height: 1.8;
    letter-spacing: 1px;
    color: #C2185B;
    text-align: center;
}
.px-wrap-2x .px-caption {
    margin: 0;
    text-align: left;
}
.px-placeholder {
    display: block;
    padding: 36px 0;
    font-family: var(--px-chrome);
    font-size: 12px;
    color: #1E1B3A;
}

/* ---- needs bars: one color per need ---------------------------------- */
.need-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0;
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #1E1B3A;
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
    color: #1E1B3A;
    white-space: nowrap;
    overflow: hidden;
}
.need-segs {
    display: flex;
    gap: 3px;
    flex: 1 1 auto;
    padding: 3px;
    background: #FFF6D5;
    border: 2px solid #1E1B3A;
    box-shadow: 2px 2px 0 0 #1E1B3A;
}
.need-seg {
    flex: 1 1 0;
    height: 12px;
    background: #E8DCC0;
}
.need-seg.on {
    background: #5BE36A;
}
.need-hunger .need-seg.on { background: #FF8C42; }
.need-sleep .need-seg.on { background: #9B6BFF; }
.need-security .need-seg.on { background: #2EC4B6; }
.need-love .need-seg.on { background: #FF5DA2; }
.need-esteem .need-seg.on { background: #FFD93D; }
.need-self_actualization .need-seg.on { background: #5BE36A; }
.need-critical .need-seg.on {
    background: #FF4757;
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

/* ---- emotion chips (colored tiles) and mood badge -------------------- */
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
    color: #1E1B3A;
    background: #FFF6D5;
    border: 3px solid #1E1B3A;
    box-shadow: 3px 3px 0 0 #1E1B3A;
}
.emotion-joy { background: #FFD93D; }
.emotion-sadness { background: #3A86FF; }
.emotion-anger { background: #FF4757; }
.emotion-fear { background: #9B6BFF; }
.emotion-surprise { background: #FF8C42; }
.emotion-disgust { background: #5BE36A; }
.emotion-trust { background: #2EC4B6; }
.emotion-anticipation { background: #FF5DA2; }
.mood-badge {
    display: inline-block;
    padding: 8px 10px;
    font-family: var(--px-chrome);
    font-size: 10px;
    color: #1E1B3A;
    border: 3px solid #1E1B3A;
    box-shadow: 3px 3px 0 0 #1E1B3A;
}
.mood-positive { background: #5BE36A; }
.mood-negative { background: #FF4757; }

/* ---- dialog boxes ---------------------------------------------------- */
.px-dialog {
    position: relative;
    margin: 18px 0 20px;
    padding: 12px 16px;
    font-family: var(--px-body);
    font-size: 20px;
    line-height: 1.1;
    color: #1E1B3A;
    background: #FFF6D5;
    border: 3px solid #1E1B3A;
    box-shadow: 0 0 0 3px #FFF6D5, 6px 6px 0 3px #1E1B3A;
}
.px-dialog-thought::before {
    content: "";
    position: absolute;
    top: -15px;
    left: 50%;
    width: 6px;
    height: 6px;
    background: #1E1B3A;
    box-shadow: -8px -8px 0 0 #1E1B3A, -14px -18px 0 0 #1E1B3A;
}
.px-dialog-action::before {
    content: "";
    position: absolute;
    top: -9px;
    left: 24px;
    width: 12px;
    height: 6px;
    background: #1E1B3A;
    box-shadow: 3px -6px 0 0 #1E1B3A;
}
.px-dialog-action .action-title {
    margin: 0 0 8px;
    font-family: var(--px-chrome);
    font-size: 11px;
    line-height: 1.8;
    letter-spacing: 1px;
    color: #C2185B;
}
.px-dialog-action .action-reasoning {
    margin: 0 0 8px;
    color: #4A4670;
}
.px-dialog-action .action-lessons {
    margin: 0 0 8px;
    color: #1E1B3A;
}
.satisfaction-delta {
    display: inline-block;
    padding: 6px 8px;
    font-family: var(--px-chrome);
    font-size: 9px;
    color: #1E1B3A;
    border: 2px solid #1E1B3A;
    box-shadow: 2px 2px 0 0 #1E1B3A;
}
.delta-positive { background: #5BE36A; }
.delta-negative { background: #FF4757; }
.delta-neutral  { background: #E8DCC0; }

/* ---- icons ----------------------------------------------------------- */
.px-icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    vertical-align: middle;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
}
.px-icon-missing {
    background: transparent;
}
"""
