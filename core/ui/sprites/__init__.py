"""Pixel sprite assets for the Jenbina UI.

Only paths and constants live here; this module never imports ``build``
(and therefore never imports Pillow) so the running app stays light.
"""

import os

from core.ui.sprites.art import ICON_ART, STATE_FRAMES

#: Sprite states, in the spec's order. File names are ``jenbina_<state>.png``.
STATES: tuple[str, ...] = tuple(STATE_FRAMES)

#: States animated with the 50/50 motion cycle; the rest blink.
MOTION_STATES: frozenset[str] = frozenset({"scary", "thinking", "eat", "drink", "sleep", "talk", "walks"})

#: Icon names. Files are ``icons/<name>.png``.
ICONS: tuple[str, ...] = tuple(ICON_ART)

#: Absolute path of the committed ``assets/sprites`` directory.
SPRITES_DIR: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "assets", "sprites")
)


def sprite_path(state: str) -> str:
    """Path of the 96x48 sheet for ``state``; unknown states get the ``base`` sheet."""
    if state not in STATES:
        state = "base"
    return os.path.join(SPRITES_DIR, f"jenbina_{state}.png")


def icon_path(name: str) -> str:
    """Path of the 8x8 icon ``name`` (may not exist for unknown names)."""
    return os.path.join(SPRITES_DIR, "icons", f"{name}.png")


def avatar_path() -> str:
    """Path of the 48x48 chat avatar (frame 0 of ``base``)."""
    return os.path.join(SPRITES_DIR, "jenbina_avatar.png")
