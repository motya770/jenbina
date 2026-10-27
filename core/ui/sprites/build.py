"""Pillow compositor and build CLI for the pixel sprites.

Run ``python -m core.ui.sprites.build`` to regenerate ``assets/sprites``.
"""

from __future__ import annotations

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - exercised only without Pillow
    raise ImportError(
        "Pillow is required to build the pixel sprites "
        "(it ships with Streamlit; pip install pillow)"
    ) from exc

from core.ui.sprites.palette import PALETTE, Layer

TRANSPARENT = (0, 0, 0, 0)


def compose(
    layers: list[Layer],
    size: tuple[int, int] = (48, 48),
    dy: int = 0,
) -> Image.Image:
    """Draw ``layers`` in order onto a transparent RGBA canvas.

    A ``"."`` pixel leaves what is underneath. ``dy`` shifts the whole result
    vertically (negative is up); rows exposed by the shift are transparent.
    Raises ``ValueError`` for a key not in ``PALETTE`` or a row that runs past
    the canvas.
    """
    width, height = size
    img = Image.new("RGBA", size, TRANSPARENT)
    for x0, y0, rows in layers:
        if y0 < 0 or y0 + len(rows) > height:
            raise ValueError(f"layer at ({x0}, {y0}) with {len(rows)} rows overflows height {height}")
        for row_index, row in enumerate(rows):
            if x0 < 0 or x0 + len(row) > width:
                raise ValueError(f"row {row_index} of layer at ({x0}, {y0}) overflows width {width}")
            for col_index, key in enumerate(row):
                if key == ".":
                    continue
                if key not in PALETTE:
                    raise ValueError(f"unknown palette key {key!r}")
                img.putpixel((x0 + col_index, y0 + row_index), PALETTE[key])
    if dy:
        shifted = Image.new("RGBA", size, TRANSPARENT)
        shifted.paste(img, (0, dy))
        img = shifted
    return img


# --------------------------------------------------------------------------
# Frames and sheets
# --------------------------------------------------------------------------
from core.ui.sprites.art import BODY, HAIR, FACES, PROPS, EFFECTS, STATE_FRAMES, ICON_ART  # noqa: E402
from core.ui.sprites.palette import FrameSpec  # noqa: E402

FRAME_SIZE = (48, 48)
SHEET_SIZE = (96, 48)


def frame_layers(spec: FrameSpec) -> list[Layer]:
    """Body, hair, face, props, effects — in drawing order."""
    layers: list[Layer] = [BODY, HAIR, FACES[spec["face"]]]
    layers.extend(PROPS[name] for name in spec.get("props", []))
    layers.extend(EFFECTS[name] for name in spec.get("effects", []))
    return layers


def render_frame(spec: FrameSpec) -> Image.Image:
    """One 48x48 frame."""
    return compose(frame_layers(spec), size=FRAME_SIZE, dy=spec.get("dy", 0))


def render_sheet(state: str) -> Image.Image:
    """The 96x48 two-frame sheet for ``state``; unknown state raises KeyError."""
    frame0, frame1 = STATE_FRAMES[state]
    sheet = Image.new("RGBA", SHEET_SIZE, TRANSPARENT)
    sheet.paste(render_frame(frame0), (0, 0))
    sheet.paste(render_frame(frame1), (48, 0))
    return sheet


ICON_SIZE = (8, 8)


def render_icon(name: str) -> Image.Image:
    """One 8x8 icon; unknown name raises KeyError."""
    return compose([(0, 0, ICON_ART[name])], size=ICON_SIZE)
