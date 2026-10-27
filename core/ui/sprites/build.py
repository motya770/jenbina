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
