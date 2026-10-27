"""Tests for the pixel sprite pipeline (core.ui.sprites)."""

import unittest

from core.ui.sprites.palette import PALETTE
from core.ui.sprites.build import compose


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


if __name__ == "__main__":
    unittest.main()
