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
        lost_rows = range(0, -dy) if dy < 0 else range(height - dy, height)
        for y in lost_rows:
            if any(img.getpixel((x, y))[3] for x in range(width)):
                raise ValueError(f"dy={dy} would shift opaque pixels in row {y} off the canvas")
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


# --------------------------------------------------------------------------
# Whole-set rendering, writing and checking
# --------------------------------------------------------------------------
import argparse  # noqa: E402
import io  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402

from core.ui.sprites import SPRITES_DIR  # noqa: E402

AVATAR_FILE = "jenbina_avatar.png"


def render_all() -> dict[str, Image.Image]:
    """Every output image, keyed by path relative to ``assets/sprites``."""
    out: dict[str, Image.Image] = {}
    for state in STATE_FRAMES:
        out[f"jenbina_{state}.png"] = render_sheet(state)
    out[AVATAR_FILE] = render_frame(STATE_FRAMES["base"][0])
    for name in ICON_ART:
        out[f"icons/{name}.png"] = render_icon(name)
    return out


def png_bytes(img: Image.Image) -> bytes:
    """PNG encoding with fixed settings and no timestamps.

    Bytes are stable for one Pillow/zlib build; ``check()`` therefore compares
    decoded pixels, which is what "differs from a fresh render" means.
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _pixels(img: Image.Image) -> tuple[tuple[int, int], bytes]:
    return img.size, img.convert("RGBA").tobytes()


def _file_matches(path: Path, img: Image.Image) -> bool:
    if not path.is_file():
        return False
    try:
        with Image.open(path) as on_disk:
            return _pixels(on_disk) == _pixels(img)
    except Exception:
        return False


def write_all(out_dir: Path, favicon: Path | None) -> list[Path]:
    """Write every sheet, the avatar and the icons under ``out_dir``.

    When ``favicon`` is given it receives a copy of the avatar bytes.
    Returns the written paths.
    """
    out_dir = Path(out_dir)
    (out_dir / "icons").mkdir(parents=True, exist_ok=True)
    renders = render_all()
    written: list[Path] = []
    for rel, img in renders.items():
        path = out_dir / rel
        path.write_bytes(png_bytes(img))
        written.append(path)
    if favicon is not None:
        favicon = Path(favicon)
        favicon.parent.mkdir(parents=True, exist_ok=True)
        favicon.write_bytes(png_bytes(renders[AVATAR_FILE]))
        written.append(favicon)
    return written


def check(out_dir: Path, favicon: Path | None) -> list[str]:
    """Relative paths under ``out_dir`` (plus the favicon) that are missing, differ
    from a fresh render, or are PNGs no render produces (orphans of a rename)."""
    out_dir = Path(out_dir)
    renders = render_all()
    stale = [rel for rel, img in renders.items() if not _file_matches(out_dir / rel, img)]
    if favicon is not None and not _file_matches(Path(favicon), renders[AVATAR_FILE]):
        stale.append(os.path.relpath(favicon, out_dir))
    present = {p.relative_to(out_dir).as_posix() for p in out_dir.rglob("*.png")} if out_dir.is_dir() else set()
    stale.extend(sorted(present - set(renders)))
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m core.ui.sprites.build",
        description="Render the pixel sprites into assets/sprites (and the favicon).",
    )
    parser.add_argument("--check", action="store_true", help="exit 1 if any committed file differs from a fresh render")
    parser.add_argument("--out", default=SPRITES_DIR, help="output directory (default: assets/sprites)")
    parser.add_argument(
        "--favicon",
        default=os.path.join(os.path.dirname(SPRITES_DIR), "favicon.png"),
        help="favicon path (default: assets/favicon.png)",
    )
    args = parser.parse_args(argv)
    out_dir, favicon = Path(args.out), Path(args.favicon)
    if args.check:
        stale = check(out_dir, favicon)
        for rel in stale:
            print(f"stale: {rel}")
        print("sprites up to date" if not stale else f"{len(stale)} file(s) differ; run python -m core.ui.sprites.build")
        return 1 if stale else 0
    written = write_all(out_dir, favicon)
    print(f"wrote {len(written)} files under {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
