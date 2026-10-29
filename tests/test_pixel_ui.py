"""Tests for the pixel theme helpers (core.ui.pixel_theme) and the pixel markup
emitted by the simulation page renderers (core.ui.simulation)."""

import os
import unittest
from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from core.interaction.chat_handler import handle_chat_interaction

from core.ui.simulation import (
    display_jenbina_image,
    render_emotion_chips,
    render_mood_indicator,
    render_needs_bars,
)
from core.ui.pixel_theme import (
    PLACEHOLDER,
    action_icon,
    delta_badge_html,
    dialog_html,
    event_html,
    icon_html,
    inject_pixel_css,
    marker_html,
    sprite_html,
    stage_pill_html,
)


class TestSpriteHtml(unittest.TestCase):
    def test_blink_and_motion_classes(self):
        self.assertIn("px-anim-blink", sprite_html("smile"))
        self.assertIn("px-anim-motion", sprite_html("walks"))

    def test_embeds_png_data_uri_and_escapes_caption(self):
        html_ = sprite_html("base", caption="Jen <3 & co")
        self.assertIn("data:image/png;base64,", html_)
        self.assertIn("Jen &lt;3 &amp; co", html_)

    def test_half_size_sprite_gets_its_own_classes(self):
        small = sprite_html("base", caption="Jenbina", scale=2)
        self.assertIn("px-sprite-2x", small)
        self.assertIn("px-wrap-2x", small)
        self.assertNotIn("px-sprite-2x", sprite_html("base"))

    def test_unknown_state_uses_base_sheet(self):
        self.assertEqual(sprite_html("nope"), sprite_html("base"))

    def test_missing_sheet_falls_back_to_placeholder(self):
        with patch("core.ui.pixel_theme.sprite_path", return_value="/nonexistent/jenbina_base.png"):
            self.assertIn(PLACEHOLDER, sprite_html("base"))


class TestIconAndDialog(unittest.TestCase):
    def test_icon_html_and_missing_icon(self):
        self.assertIn('class="px-icon"', icon_html("joy", alt="Joy"))
        self.assertIn("px-icon-missing", icon_html("curiosity"))

    def test_icon_html_rejects_names_outside_the_icon_set(self):
        out = icon_html("../jenbina_base")
        self.assertIn("px-icon-missing", out)
        self.assertNotIn("data:image", out)

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
                       ".need-seg", ".px-dialog", "steps(1", ".px-sprite-2x", ".px-wrap-2x",
                       # candy arcade palette: screen, accent, device body, panel, and the six need colors
                       "#4FC3F7", "#FF3E8A", "#FF6B9D", "#FFF6D5",
                       ".need-hunger", ".need-sleep", ".need-security", ".need-love", ".need-esteem",
                       ".need-self_actualization", ".emotion-joy"]:
            self.assertIn(needle, css)
        self.assertEqual(css.count("linear-gradient("), 1)   # only the scanline overlay
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


def _row(html_, key):
    """The markup of one needs-bar row, from its class to the next row."""
    start = html_.index(f'need-row need-{key}')
    end = html_.find('<div class="need-row', start + 1)
    return html_[start:end if end != -1 else len(html_)]


class TestNeedsBars(unittest.TestCase):
    def test_six_rows_ten_segments_and_fill_count(self):
        html_ = rendered(render_needs_bars, FakePerson(
            {"hunger": 60, "sleep": 43, "security": 80, "love": 0, "self_esteem": 120, "personal_growth": -5}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        for need in ["hunger", "sleep", "security", "love", "esteem", "self_actualization"]:
            self.assertIn(f'class="need-row need-{need}', html_)
        self.assertEqual(html_.count('<span class="need-seg'), 60)
        self.assertEqual(html_.count('need-seg on'), 6 + 4 + 8 + 0 + 10 + 0)

    def test_esteem_and_growth_rows_read_the_real_needs(self):
        from core.person.person import Person
        html_ = rendered(render_needs_bars, Person())
        self.assertIn('need-pct">50%', _row(html_, "esteem"))            # self_esteem starts at 50
        self.assertIn('need-pct">30%', _row(html_, "self_actualization"))  # personal_growth starts at 30

    def test_half_percent_boundaries_round_up(self):
        html_ = rendered(render_needs_bars, FakePerson(
            {"hunger": 85, "sleep": 75, "security": 45, "love": 95, "self_esteem": 5, "personal_growth": 55}, {}))
        self.assertEqual(html_.count('need-seg on'), 9 + 8 + 5 + 10 + 1 + 6)

    def test_non_finite_need_value_renders_as_empty_bar(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": float("nan"), "sleep": float("inf")}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        self.assertEqual(html_.count('need-seg on'), 10)   # inf clamps to 100; nan counts as 0

    def test_critical_only_below_thirty(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": 29, "sleep": 30}, {}))
        self.assertEqual(html_.count("need-critical"), 1 + 4)   # hunger, plus the four needs missing from the dict (0%)


class TestChipsMoodRibbon(unittest.TestCase):
    def test_chips_cap_at_four_skip_low_and_survive_unknown_emotion(self):
        html_ = rendered(render_emotion_chips, FakePerson(
            {}, {"joy": 90, "trust": 80, "fear": 70, "curiosity": 60, "anger": 50, "sadness": 15}))
        self.assertEqual(html_.count('<span class="emotion-chip'), 4)
        self.assertIn('class="emotion-chip emotion-joy"', html_)
        self.assertIn('class="emotion-chip emotion-curiosity"', html_)
        self.assertIn("px-icon-missing", html_)
        self.assertNotIn("Sadness", html_)

    def test_mood_badge_polarity(self):
        self.assertIn("mood-positive", rendered(render_mood_indicator, FakePerson({}, {"joy": 50})))
        self.assertIn("mood-negative", rendered(render_mood_indicator, FakePerson({}, {"anger": 50})))


class TestActionAndSprite(unittest.TestCase):
    def test_display_jenbina_image_derives_state_from_any_path(self):
        self.assertIn("px-anim-motion", rendered(display_jenbina_image, "/old/src/images/jenbina_eat.png", "Jenbina"))
        self.assertEqual(rendered(display_jenbina_image, "whatever.png"), rendered(display_jenbina_image, "jenbina_base.png"))


class TestPortrait(unittest.TestCase):
    def test_display_shows_portrait_window_and_half_size_sprite(self):
        with patch("core.ui.simulation.st") as st:
            display_jenbina_image("/old/src/images/jenbina_eat.png", "Jenbina")
            (path,), kwargs = st.image.call_args
            self.assertTrue(path.endswith(os.path.join("assets", "portraits", "jenbina_eat.png")), path)
            self.assertEqual(kwargs.get("width"), 256)
            self.assertIn("px-sprite-2x", st.markdown.call_args[0][0])

    def test_unknown_state_uses_base_portrait(self):
        with patch("core.ui.simulation.st") as st:
            display_jenbina_image("whatever.png")
            self.assertTrue(st.image.call_args[0][0].endswith("jenbina_base.png"))

    def test_missing_portraits_fall_back_to_sprite_only(self):
        with patch("core.ui.simulation.st") as st, patch("core.ui.simulation.IMAGES_DIR", "/nonexistent"):
            display_jenbina_image("jenbina_base.png")
            st.image.assert_not_called()
            self.assertIn("px-sprite", st.markdown.call_args[0][0])


class TestChatHandlerAvatars(unittest.TestCase):
    @patch("core.interaction.chat_handler.check_injection", return_value=(True, "blocked"))
    def test_live_turn_rows_get_sprite_avatars(self, _):
        st = MagicMock()
        handle_chat_interaction(st, None, None, None, None, user_input="hi", memory_manager=None)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertEqual(len(avatars), 2)
        self.assertTrue(avatars[0].endswith("icons/player.png"))
        self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))



class TestWideShell(unittest.TestCase):
    def test_wide_flag_widens_device(self):
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css(wide=True)
            self.assertIn("max-width: 64rem", "".join(c.args[0] for c in st.markdown.call_args_list))
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css()
            self.assertNotIn("64rem", "".join(c.args[0] for c in st.markdown.call_args_list))


class TestEventHtml(unittest.TestCase):
    def test_classes_icon_and_escaping(self):
        html_ = event_html("mood", "Mood <lifted>", meta="23:41")
        self.assertIn('class="px-event px-event-mood"', html_)
        self.assertIn("Mood &lt;lifted&gt;", html_)
        self.assertIn('alt="mood"', html_)
        self.assertIn('<span class="px-event-meta">23:41</span>', html_)
        self.assertNotIn("<details", html_)

    def test_details_badge_and_icon_override(self):
        html_ = event_html("action", "t", details=("why?", "a & b\nc"), badge="<b>B</b>", icon="hunger")
        self.assertIn("<summary>why?</summary>", html_)
        self.assertIn("a &amp; b<br>c", html_)
        self.assertIn("<b>B</b>", html_)
        self.assertIn('alt="hunger"', html_)

    def test_unknown_kind_uses_generic_icon_and_safe_class(self):
        html_ = event_html("we!rd", "t")
        self.assertIn('px-event-werd"', html_)
        self.assertIn('alt="act"', html_)

    def test_action_icon_keywords(self):
        self.assertEqual(action_icon("Eat breakfast"), "hunger")
        self.assertEqual(action_icon("Attend live music at Coupa"), "love")
        self.assertEqual(action_icon("Stroll University Avenue"), "walk")
        self.assertEqual(action_icon("Contemplate"), "act")


class TestDeltaBadge(unittest.TestCase):
    def test_text_attributes_and_sign_class(self):
        html_ = delta_badge_html(83.4, 85.1)
        self.assertIn("83% → 85% (+1.7%)", html_)
        self.assertIn('data-before="83.4"', html_)
        self.assertIn('data-after="85.1"', html_)
        self.assertIn('data-delta="1.7"', html_)
        self.assertIn("delta-positive", html_)
        self.assertIn("delta-negative", delta_badge_html(50, 48.2))
        self.assertIn("delta-neutral", delta_badge_html(50, 50))
        self.assertIn("(+0.0%)", delta_badge_html(50, 50))


class TestMarkerAndPill(unittest.TestCase):
    def test_marker_and_pill(self):
        self.assertEqual(marker_html("23:38 · <home>"), '<div class="px-marker">23:38 · &lt;home&gt;</div>')
        self.assertIn('class="px-stage"', stage_pill_html("thinking…"))


if __name__ == "__main__":
    unittest.main()
