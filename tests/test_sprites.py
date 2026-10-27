"""Tests for the pixel sprite pipeline (core.ui.sprites)."""

import tempfile
import unittest
from pathlib import Path

from core.ui.sprites.palette import PALETTE
from core.ui.sprites.art import BODY, HAIR, FACES, PROPS, EFFECTS, STATE_FRAMES, ICON_ART
from core.ui.sprites import STATES, MOTION_STATES, ICONS, SPRITES_DIR, sprite_path
from core.ui.sprites.build import (
    compose, render_frame, render_sheet, render_icon, render_all, png_bytes, write_all, check,
)

EMOTION_STATES = ["base", "smile", "sad", "angry", "scary", "surprised", "thinking"]
ACTION_STATES = ["eat", "drink", "read", "sleep", "talk", "walks"]
ICON_NAMES = ["hunger", "sleep", "security", "love", "esteem", "self_actualization",
              "joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation",
              "sunny", "cloudy", "rain", "storm", "snow", "fog", "wind", "player"]


def all_layers():
    layers = {"body": BODY, "hair": HAIR}
    layers.update({f"face:{k}": v for k, v in FACES.items()})
    layers.update({f"prop:{k}": v for k, v in PROPS.items()})
    layers.update({f"effect:{k}": v for k, v in EFFECTS.items()})
    return layers


class TestPalette(unittest.TestCase):
    def test_has_seventeen_keys_with_transparent_dot(self):
        self.assertEqual(len(PALETTE), 17)
        self.assertEqual(PALETTE["."], (0, 0, 0, 0))
        self.assertEqual(PALETTE["B"], (0xFF, 0x8F, 0xAB, 255))


class TestCompose(unittest.TestCase):
    def test_later_layer_overwrites_but_dot_is_transparent(self):
        img = compose([(0, 0, ["SS", "SS"]), (0, 0, [".K", ".."])], size=(2, 2))
        self.assertEqual(img.getpixel((0, 0)), PALETTE["S"])
        self.assertEqual(img.getpixel((1, 0)), PALETTE["K"])

    def test_offset_layer(self):
        img = compose([(1, 1, ["K"])], size=(2, 2))
        self.assertEqual(img.getpixel((1, 1)), PALETTE["K"])
        self.assertEqual(img.getpixel((0, 0)), (0, 0, 0, 0))

    def test_dy_shifts_up_and_exposes_transparent_row(self):
        img = compose([(0, 0, ["..", "KK"])], size=(2, 2), dy=-1)
        self.assertEqual(img.getpixel((0, 0)), PALETTE["K"])
        self.assertEqual(img.getpixel((0, 1)), (0, 0, 0, 0))

    def test_unknown_key_raises(self):
        with self.assertRaises(ValueError):
            compose([(0, 0, ["Z"])], size=(1, 1))

    def test_overflow_raises(self):
        with self.assertRaises(ValueError):
            compose([(1, 0, ["KK"])], size=(2, 1))


class TestArtLayers(unittest.TestCase):
    def test_every_layer_fits_the_canvas_and_uses_palette_keys(self):
        for name, (x, y, rows) in all_layers().items():
            for row in rows:
                self.assertLessEqual(x + len(row), 48, name)
                self.assertTrue(set(row) <= set(PALETTE), name)
            self.assertLessEqual(y + len(rows), 48, name)

    def test_faces_sit_in_the_face_region(self):
        for name, (x, y, rows) in FACES.items():
            self.assertEqual((x, y), (16, 14), name)
            self.assertEqual((len(rows), len(rows[0])), (10, 16), name)


class TestEmotionSheets(unittest.TestCase):
    def test_sheets_are_96x48_rgba(self):
        for s in EMOTION_STATES:
            self.assertEqual((render_sheet(s).size, render_sheet(s).mode), ((96, 48), "RGBA"), s)

    def test_frame_one_differs_from_frame_zero(self):
        for s in EMOTION_STATES:
            sheet = render_sheet(s)
            self.assertNotEqual(sheet.crop((0, 0, 48, 48)).tobytes(), sheet.crop((48, 0, 96, 48)).tobytes(), s)

    def test_each_state_differs_from_base(self):
        base = render_sheet("base").crop((0, 0, 48, 48)).tobytes()
        for s in EMOTION_STATES[1:]:
            self.assertNotEqual(render_sheet(s).crop((0, 0, 48, 48)).tobytes(), base, s)

    def test_unknown_state_raises(self):
        with self.assertRaises(KeyError):
            render_sheet("dancing")


class TestActionSheets(unittest.TestCase):
    def test_all_thirteen_states_present_in_spec_order(self):
        self.assertEqual(list(STATE_FRAMES), EMOTION_STATES + ACTION_STATES)

    def test_action_sheets_render_and_animate(self):
        for s in ACTION_STATES:
            sheet = render_sheet(s)
            self.assertEqual(sheet.size, (96, 48), s)
            self.assertNotEqual(sheet.crop((0, 0, 48, 48)).tobytes(), sheet.crop((48, 0, 96, 48)).tobytes(), s)

    def test_walks_frame_one_is_shifted_up(self):
        self.assertEqual(STATE_FRAMES["walks"][1]["dy"], -1)
        self.assertEqual(render_frame(STATE_FRAMES["walks"][1]).getpixel((24, 47)), (0, 0, 0, 0))


class TestIcons(unittest.TestCase):
    def test_exactly_the_spec_icons(self):
        self.assertEqual(sorted(ICON_ART), sorted(ICON_NAMES))

    def test_icons_are_8x8_and_not_empty(self):
        for name in ICON_NAMES:
            img = render_icon(name)
            self.assertEqual((img.size, img.mode), ((8, 8), "RGBA"), name)
            self.assertTrue(any(px[3] for px in img.getdata()), name)

    def test_unknown_icon_raises(self):
        with self.assertRaises(KeyError):
            render_icon("banana")


class TestBuild(unittest.TestCase):
    def test_render_all_has_every_output(self):
        out = render_all()
        self.assertEqual(
            sorted(out),
            sorted([f"jenbina_{s}.png" for s in STATES] + ["jenbina_avatar.png"] + [f"icons/{i}.png" for i in ICONS]),
        )
        self.assertEqual(out["jenbina_avatar.png"].size, (48, 48))

    def test_png_bytes_is_deterministic(self):
        self.assertEqual(png_bytes(render_sheet("base")), png_bytes(render_sheet("base")))

    def test_write_then_check_is_clean_and_edit_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            out, fav = Path(d) / "sprites", Path(d) / "favicon.png"
            write_all(out, fav)
            self.assertEqual(check(out, fav), [])
            (out / "icons" / "joy.png").write_bytes(b"corrupt")
            self.assertEqual(check(out, fav), ["icons/joy.png"])

    def test_committed_assets_are_fresh(self):
        self.assertEqual(check(Path(SPRITES_DIR), Path(SPRITES_DIR).parent / "favicon.png"), [])


class TestPaths(unittest.TestCase):
    def test_sprite_path_falls_back_to_base(self):
        self.assertTrue(sprite_path("nope").endswith("jenbina_base.png"))
        self.assertTrue(sprite_path("eat").endswith("jenbina_eat.png"))

    def test_motion_states(self):
        self.assertEqual(MOTION_STATES, frozenset({"scary", "thinking", "eat", "drink", "sleep", "talk", "walks"}))

    def test_constants_match_the_art(self):
        self.assertEqual(STATES, tuple(STATE_FRAMES))
        self.assertEqual(sorted(ICONS), sorted(ICON_ART))


if __name__ == "__main__":
    unittest.main()
