"""Tests for the pixel theme helpers (core.ui.pixel_theme) and the pixel markup
emitted by the simulation page renderers (core.ui.simulation)."""

import unittest
from unittest.mock import patch

from core.ui.pixel_theme import (
    PLACEHOLDER,
    dialog_html,
    icon_html,
    inject_pixel_css,
    sprite_html,
)


class TestSpriteHtml(unittest.TestCase):
    def test_blink_and_motion_classes(self):
        self.assertIn("px-anim-blink", sprite_html("smile"))
        self.assertIn("px-anim-motion", sprite_html("walks"))

    def test_embeds_png_data_uri_and_escapes_caption(self):
        html_ = sprite_html("base", caption="Jen <3 & co")
        self.assertIn("data:image/png;base64,", html_)
        self.assertIn("Jen &lt;3 &amp; co", html_)

    def test_unknown_state_uses_base_sheet(self):
        self.assertEqual(sprite_html("nope"), sprite_html("base"))

    def test_missing_sheet_falls_back_to_placeholder(self):
        with patch("core.ui.pixel_theme.sprite_path", return_value="/nonexistent/jenbina_base.png"):
            self.assertIn(PLACEHOLDER, sprite_html("base"))


class TestIconAndDialog(unittest.TestCase):
    def test_icon_html_and_missing_icon(self):
        self.assertIn('class="px-icon"', icon_html("joy", alt="Joy"))
        self.assertIn("px-icon-missing", icon_html("curiosity"))

    def test_dialog_escapes_and_breaks_lines(self):
        out = dialog_html("a < b\nc & d", kind="action")
        self.assertIn("px-dialog-action", out)
        self.assertIn("a &lt; b<br>c &amp; d", out)


class TestInjectCss(unittest.TestCase):
    @patch("core.ui.pixel_theme.st")
    def test_injects_once_with_fonts_and_sprite_rules(self, st):
        inject_pixel_css()
        st.markdown.assert_called_once()
        css, kwargs = st.markdown.call_args[0][0], st.markdown.call_args[1]
        self.assertTrue(kwargs.get("unsafe_allow_html"))
        for needle in ["Press+Start+2P", "VT323", ".px-sprite", "image-rendering: pixelated",
                       ".need-seg", ".px-dialog", "steps(1", "#1B1F3B", "#FF8FAB"]:
            self.assertIn(needle, css)
        self.assertNotRegex(css, r"border-radius:\s*[1-9]")   # only `border-radius: 0` overrides are allowed
        self.assertNotIn("linear-gradient(135", css)


if __name__ == "__main__":
    unittest.main()
