"""Palette for the pixel art. One character per color in the art strings.

This module imports nothing from the package so ``art.py`` and ``build.py``
can both import it without a cycle.
"""

# key -> RGBA
PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),              # transparent
    "K": (0x2B, 0x1B, 0x2E, 255),   # outline
    "S": (0xF5, 0xC7, 0xA1, 255),   # skin
    "s": (0xD9, 0x98, 0x6F, 255),   # skin shadow
    "B": (0xFF, 0x8F, 0xAB, 255),   # blush / coral
    "H": (0x3A, 0x2A, 0x3F, 255),   # hair
    "h": (0x5E, 0x4A, 0x66, 255),   # hair highlight
    "W": (0xFF, 0xFF, 0xFF, 255),   # white
    "E": (0x3B, 0x6E, 0xA5, 255),   # iris
    "M": (0xB5, 0x48, 0x4D, 255),   # mouth
    "A": (0xC9, 0xD1, 0xD9, 255),   # suit silver
    "a": (0x8A, 0x94, 0xA6, 255),   # suit shadow
    "T": (0x5F, 0xB3, 0xB3, 255),   # teal accent
    "Y": (0xFF, 0xD9, 0x3D, 255),   # yellow
    "G": (0x6B, 0xCB, 0x77, 255),   # green
    "R": (0xFF, 0x6B, 0x6B, 255),   # red
    "N": (0x8B, 0x5A, 0x2B, 255),   # brown
}

# (x, y, rows); each row is a string of palette keys
Layer = tuple[int, int, list[str]]

# {"face": str, "props": list[str], "effects": list[str], "dy": int}
FrameSpec = dict
