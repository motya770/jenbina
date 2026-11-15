"""Portrait and state renderers for Jenbina's UI."""
import html
import math
import os
import re

import streamlit as st

from core.ui.pixel_theme import PLACEHOLDER, portrait_caption_html


# Painterly portraits, one per state (``jenbina_<state>.png``). They are
# always shown exactly as drawn: no filter, tint or overlay.
IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "portraits"
)
PORTRAIT_WIDTH = 256


def _get_image_path(name):
    """Get absolute path to a Jenbina image."""
    return os.path.join(IMAGES_DIR, name)


def get_jenbina_image_for_action(chosen_action):
    """Determine which Jenbina image to show based on the chosen action."""
    action_lower = chosen_action.lower() if chosen_action else ""

    # Action-based mapping
    action_map = [
        (["eat", "food", "cook", "meal", "snack", "breakfast", "lunch", "dinner", "hungry"], "jenbina_eat.png"),
        (["drink", "water", "thirst", "hydrat", "beverage", "tea", "coffee"], "jenbina_drink.png"),
        (["walk", "move", "explor", "travel", "wander", "go to", "visit", "roam", "stroll"], "jenbina_walks.png"),
        (["sleep", "rest", "nap", "bed", "doze"], "jenbina_sleep.png"),
        (["talk", "chat", "convers", "speak", "social", "friend", "greet", "discuss"], "jenbina_talk.png"),
        (["read", "study", "learn", "book", "research", "reflect", "meditat", "think", "journal"], "jenbina_read.png"),
    ]

    for keywords, image_name in action_map:
        for kw in keywords:
            if kw in action_lower:
                return _get_image_path(image_name)

    return None  # No action-specific image matched


def get_jenbina_image_for_emotion(person):
    """Determine which Jenbina image to show based on dominant emotion."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return _get_image_path("jenbina_base.png")

    top_emotion = dominant[0]["name"].lower()
    intensity = dominant[0]["intensity"]

    if top_emotion == "joy" and intensity > 30:
        return _get_image_path("jenbina_smile.png")
    elif top_emotion == "sadness" and intensity > 30:
        return _get_image_path("jenbina_sad.png")
    elif top_emotion == "anger" and intensity > 30:
        return _get_image_path("jenbina_angry.png")
    elif top_emotion == "fear" and intensity > 30:
        return _get_image_path("jenbina_scary.png")
    elif top_emotion == "surprise" and intensity > 30:
        return _get_image_path("jenbina_surprised.png")

    return _get_image_path("jenbina_base.png")


def _portrait_path(state):
    """The portrait file for ``state``, the ``base`` portrait if that is missing, else None."""
    for candidate in (state, "base"):
        path = os.path.join(IMAGES_DIR, f"jenbina_{candidate}.png")
        if os.path.isfile(path):
            return path
    return None


def display_jenbina_image(image_path, caption=None, width=PORTRAIT_WIDTH):
    """Show the painterly portrait for the state named by ``image_path``,
    unaltered in a thin frame, with the caption in a name strip underneath.

    The state is the file name without ``jenbina_`` and ``.png``, so legacy
    paths keep working; unknown names fall back to ``base``. Without any
    portrait on disk a text placeholder stands in for the image.
    """
    name = os.path.basename(str(image_path or ""))
    state = name[len("jenbina_"):] if name.startswith("jenbina_") else name
    if state.endswith(".png"):
        state = state[:-4]
    portrait = _portrait_path(state)
    if portrait:
        st.image(portrait, width=width)
    else:
        st.markdown(f'<span class="px-placeholder">{PLACEHOLDER}</span>', unsafe_allow_html=True)
    if caption:
        st.markdown(portrait_caption_html(caption), unsafe_allow_html=True)


# Weather keyword -> icon name; the first match wins, so specific words come first.
_WEATHER_ICONS = {
    "storm": "storm",
    "snow": "snow",
    "rain": "rain",
    "fog": "fog",
    "wind": "wind",
    "sunny": "sunny",
    "clear": "sunny",
    "cloudy": "cloudy",
    "overcast": "cloudy",
}
_DEFAULT_WEATHER_ICON = "cloudy"


def _weather_icon(description):
    text = (description or "").lower()
    for keyword, icon in _WEATHER_ICONS.items():
        if keyword in text:
            return icon
    return _DEFAULT_WEATHER_ICON


def render_needs_bars(person):
    """Render Maslow needs as thin bars; a need below 30% is marked critical."""
    # (css key, label, need in MaslowNeedsSystem): the css key names the row's
    # class; Esteem and Growth show one representative need of their level.
    needs_config = [
        ("hunger", "Hunger", "hunger"),
        ("sleep", "Sleep", "sleep"),
        ("security", "Safety", "security"),
        ("love", "Social", "love"),
        ("esteem", "Esteem", "self_esteem"),
        ("self_actualization", "Growth", "personal_growth"),
    ]

    rows = []
    for need_name, label, need_key in needs_config:
        satisfaction = person.maslow_needs.get_need_satisfaction(need_key)
        if satisfaction is None or (isinstance(satisfaction, float) and math.isnan(satisfaction)):
            satisfaction = 0
        pct = max(0, min(100, satisfaction))

        if pct < 30:
            level = " need-critical"
        elif pct < 60:
            level = " need-mid"
        else:
            level = ""
        rows.append(
            f'<div class="need-row need-{need_name}{level}" data-pct="{pct:.0f}">'
            f'<span class="need-label">{label}</span>'
            f'<div class="need-bar"><span class="need-fill" style="width:{pct:.0f}%"></span></div>'
            f'<span class="need-pct">{pct:.0f}%</span></div>'
        )

    st.markdown("".join(rows), unsafe_allow_html=True)


def _css_token(name):
    """Lower-case ``name`` reduced to [a-z0-9_] so it is safe inside a class attribute."""
    return re.sub(r"[^a-z0-9_]", "", str(name).lower())


def render_emotion_chips(person):
    """Render the strongest emotions (above 15, at most four) as text chips;
    the strongest one is marked ``emotion-dominant``."""
    all_emotions = person.emotion_system.get_emotional_state_summary().get("emotions", {})
    visible = sorted(
        [(name, val) for name, val in all_emotions.items() if val > 15],
        key=lambda x: x[1],
        reverse=True,
    )[:4]

    if not visible:
        return

    chips = "".join(
        f'<span class="emotion-chip emotion-{_css_token(name)}{" emotion-dominant" if index == 0 else ""}">'
        f'{html.escape(name.capitalize())} {intensity:.0f}</span>'
        for index, (name, intensity) in enumerate(visible)
    )
    st.markdown(f'<div class="emotion-chips">{chips}</div>', unsafe_allow_html=True)


POSITIVE_EMOTIONS = {"joy", "trust", "anticipation", "surprise"}


def render_mood_indicator(person):
    """Render a badge with Jenbina's dominant mood, styled positive or negative."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return

    emotion_name = str(dominant[0]["name"]).lower()
    intensity = int(dominant[0]["intensity"])
    polarity = "mood-positive" if emotion_name in POSITIVE_EMOTIONS else "mood-negative"

    st.markdown(
        f'<span class="mood-badge {polarity}">{html.escape(emotion_name.capitalize())} {intensity}</span>',
        unsafe_allow_html=True,
    )
