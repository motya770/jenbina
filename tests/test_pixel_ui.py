"""Tests for the pixel theme helpers (core.ui.pixel_theme) and the pixel markup
emitted by the simulation page renderers (core.ui.simulation)."""

import unittest
from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from core.interaction.chat_handler import handle_chat_interaction
from core.ui.chat import render_chat_simple

from core.ui.simulation import (
    display_jenbina_image,
    render_action_narrative,
    render_emotion_chips,
    render_environment_ribbon,
    render_mood_indicator,
    render_needs_bars,
)
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


# --------------------------------------------------------------------------
# Simulation page renderers
# --------------------------------------------------------------------------
class FakeNeeds:
    def __init__(self, v):
        self.v = v

    def get_need_satisfaction(self, n):
        return self.v.get(n, 0)


class FakeEmotions:
    def __init__(self, e):
        self.e = e

    def get_emotional_state_summary(self):
        return {"emotions": self.e}

    def get_dominant_emotions(self, n):
        return [{"name": k, "intensity": v} for k, v in sorted(self.e.items(), key=lambda kv: -kv[1])[:n]]


class FakePerson:
    name = "Jenbina"

    def __init__(self, needs, emotions):
        self.maslow_needs, self.emotion_system = FakeNeeds(needs), FakeEmotions(emotions)


def rendered(fn, *a):
    with patch("core.ui.simulation.st") as st:
        fn(*a)
        return st.markdown.call_args[0][0]


class TestNeedsBars(unittest.TestCase):
    def test_six_rows_ten_segments_and_fill_count(self):
        html_ = rendered(render_needs_bars, FakePerson(
            {"hunger": 60, "sleep": 43, "security": 80, "love": 0, "esteem": 120, "self_actualization": -5}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        self.assertEqual(html_.count('<span class="need-seg'), 60)
        self.assertEqual(html_.count('need-seg on'), 6 + 4 + 8 + 0 + 10 + 0)

    def test_critical_only_below_thirty(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": 29, "sleep": 30}, {}))
        self.assertEqual(html_.count("need-critical"), 1 + 4)   # hunger, plus the four needs missing from the dict (0%)


class TestChipsMoodRibbon(unittest.TestCase):
    def test_chips_cap_at_four_skip_low_and_survive_unknown_emotion(self):
        html_ = rendered(render_emotion_chips, FakePerson(
            {}, {"joy": 90, "trust": 80, "fear": 70, "curiosity": 60, "anger": 50, "sadness": 15}))
        self.assertEqual(html_.count('class="emotion-chip"'), 4)
        self.assertIn("px-icon-missing", html_)
        self.assertNotIn("Sadness", html_)

    def test_mood_badge_polarity(self):
        self.assertIn("mood-positive", rendered(render_mood_indicator, FakePerson({}, {"joy": 50})))
        self.assertIn("mood-negative", rendered(render_mood_indicator, FakePerson({}, {"anger": 50})))

    def test_ribbon_weather_icon_and_fallback(self):
        ws = lambda d: {"location": {"name": "Palo Alto"}, "time": {"time_of_day": "night"},
                        "weather": {"description": d, "temperature": 18}}
        self.assertIn('alt="rain"', rendered(render_environment_ribbon, ws("light rain")))
        self.assertIn('alt="cloudy"', rendered(render_environment_ribbon, ws("volcanic ash")))


class TestActionAndSprite(unittest.TestCase):
    def test_action_card_is_a_dialog_and_escapes(self):
        html_ = rendered(render_action_narrative, {"chosen_action": "Eat <soup>", "reasoning": "a & b"}, 60.0, 68.0)
        self.assertIn("px-dialog-action", html_)
        self.assertIn("eat &lt;soup&gt;", html_)
        self.assertIn("delta-positive", html_)

    def test_display_jenbina_image_derives_state_from_any_path(self):
        self.assertIn("px-anim-motion", rendered(display_jenbina_image, "/old/src/images/jenbina_eat.png", "Jenbina"))
        self.assertEqual(rendered(display_jenbina_image, "whatever.png"), rendered(display_jenbina_image, "jenbina_base.png"))


class TestChatAvatars(unittest.TestCase):
    @patch("core.ui.chat.handle_user_input")
    @patch("core.ui.chat.send_proactive_message", return_value=None)
    @patch("core.ui.chat.check_return_greeting", return_value=None)
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_history_rows_get_sprite_avatars(self, st, *_):
        st.session_state = {"proactive_checked": True}
        Msg = namedtuple("Msg", "sender content")
        person = SimpleNamespace(name="Jenbina", send_message=lambda *a: None,
                                 get_conversation_history=lambda *a, **k: [Msg("Matt", "hi"), Msg("person", "hello")])
        render_chat_simple(person, None, None, False)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertTrue(avatars[0].endswith("icons/player.png"))
        self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))


class TestChatHandlerAvatars(unittest.TestCase):
    @patch("core.interaction.chat_handler.check_injection", return_value=(True, "blocked"))
    def test_live_turn_rows_get_sprite_avatars(self, _):
        st = MagicMock()
        handle_chat_interaction(st, None, None, None, None, user_input="hi", memory_manager=None)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertEqual(len(avatars), 2)
        self.assertTrue(avatars[0].endswith("icons/player.png"))
        self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))


if __name__ == "__main__":
    unittest.main()
