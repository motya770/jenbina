"""Tests for the pixel sprite pipeline (core.ui.sprites)."""

import unittest

from core.ui.sprites.palette import PALETTE
from core.ui.sprites.art import BODY, HAIR, FACES, PROPS, EFFECTS, STATE_FRAMES
from core.ui.sprites.build import compose, render_frame, render_sheet

EMOTION_STATES = ["base", "smile", "sad", "angry", "scary", "surprised", "thinking"]


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


if __name__ == "__main__":
    unittest.main()
