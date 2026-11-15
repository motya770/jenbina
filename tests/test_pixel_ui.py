"""Tests for the theme helpers (core.ui.pixel_theme, now the Blade Runner 2049
hologram skin) and the markup emitted by the simulation page renderers
(core.ui.simulation)."""

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
    nav_icon_css,
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
    def test_injects_once_with_fonts_and_theme_rules(self, st):
        inject_pixel_css()
        st.markdown.assert_called_once()
        css, kwargs = st.markdown.call_args[0][0], st.markdown.call_args[1]
        self.assertTrue(kwargs.get("unsafe_allow_html"))
        for needle in ["IBM+Plex+Sans", "IBM+Plex+Mono", "Rajdhani",
                       # hologram palette: smoke, haze, her pink, ice, periwinkle, rust
                       "#0A0710", "#140D1C", "#FF5FC1", "#62D2DA", "#8C96FF", "#FF7850",
                       ".need-bar", ".need-fill", ".need-critical", ".emotion-dominant",
                       ".px-event-tag", ".px-marker", ".px-stage", ".px-portrait-cap",
                       "radial-gradient(", "prefers-reduced-motion",
                       # legacy helpers keep working on pages that still use them
                       ".px-sprite", ".px-sprite-2x", ".px-dialog", ".px-icon"]:
            self.assertIn(needle, css)
        for gone in ["Press+Start+2P", "VT323", "#FF6B9D", "#4FC3F7", "repeating-linear-gradient"]:
            self.assertNotIn(gone, css)

    @patch("core.ui.pixel_theme.st")
    def test_portraits_are_never_filtered(self, st):
        inject_pixel_css()
        css = st.markdown.call_args[0][0]
        image_rules = [block for block in css.split("}") if "stImage" in block or "AvatarCustom" in block]
        self.assertTrue(image_rules)
        for block in image_rules:
            for word in ("filter", "mix-blend", "sepia", "hue-rotate", "opacity"):
                self.assertNotIn(word, block)


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
    def test_six_rows_with_clamped_fill_widths(self):
        html_ = rendered(render_needs_bars, FakePerson(
            {"hunger": 60, "sleep": 43, "security": 80, "love": 0, "self_esteem": 120, "personal_growth": -5}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        for need in ["hunger", "sleep", "security", "love", "esteem", "self_actualization"]:
            self.assertIn(f'class="need-row need-{need}', html_)
        self.assertEqual(html_.count('class="need-fill"'), 6)
        for key, width in [("hunger", 60), ("sleep", 43), ("security", 80), ("love", 0),
                           ("esteem", 100), ("self_actualization", 0)]:
            self.assertIn(f'style="width:{width}%"', _row(html_, key))
        self.assertNotIn("px-icon", html_)

    def test_esteem_and_growth_rows_read_the_real_needs(self):
        from core.person.person import Person
        html_ = rendered(render_needs_bars, Person())
        self.assertIn('need-pct">50%', _row(html_, "esteem"))            # self_esteem starts at 50
        self.assertIn('need-pct">30%', _row(html_, "self_actualization"))  # personal_growth starts at 30

    def test_non_finite_need_value_renders_as_empty_bar(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": float("nan"), "sleep": float("inf")}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        self.assertIn('style="width:0%"', _row(html_, "hunger"))     # nan counts as 0
        self.assertIn('style="width:100%"', _row(html_, "sleep"))    # inf clamps to 100

    def test_critical_only_below_thirty(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": 29, "sleep": 30}, {}))
        self.assertEqual(html_.count("need-critical"), 1 + 4)   # hunger, plus the four needs missing from the dict (0%)


class TestChipsMoodRibbon(unittest.TestCase):
    def test_chips_cap_at_four_skip_low_and_survive_unknown_emotion(self):
        html_ = rendered(render_emotion_chips, FakePerson(
            {}, {"joy": 90, "trust": 80, "fear": 70, "curiosity": 60, "anger": 50, "sadness": 15}))
        self.assertEqual(html_.count('<span class="emotion-chip'), 4)
        self.assertIn('class="emotion-chip emotion-joy emotion-dominant"', html_)
        self.assertIn('class="emotion-chip emotion-curiosity"', html_)
        self.assertEqual(html_.count("emotion-dominant"), 1)
        self.assertNotIn("px-icon", html_)
        self.assertNotIn("Sadness", html_)

    def test_mood_badge_polarity(self):
        self.assertIn("mood-positive", rendered(render_mood_indicator, FakePerson({}, {"joy": 50})))
        self.assertIn("mood-negative", rendered(render_mood_indicator, FakePerson({}, {"anger": 50})))


class TestActionAndSprite(unittest.TestCase):
    def test_display_jenbina_image_derives_state_from_any_path(self):
        def portrait(path):
            with patch("core.ui.simulation.st") as st:
                display_jenbina_image(path)
                return st.image.call_args[0][0]
        self.assertTrue(portrait("/old/src/images/jenbina_eat.png").endswith("jenbina_eat.png"))
        self.assertEqual(portrait("whatever.png"), portrait("jenbina_base.png"))


class TestPortrait(unittest.TestCase):
    def test_display_shows_portrait_and_caption_without_sprite(self):
        with patch("core.ui.simulation.st") as st:
            display_jenbina_image("/old/src/images/jenbina_eat.png", "Jen <3")
            (path,), kwargs = st.image.call_args
            self.assertTrue(path.endswith(os.path.join("assets", "portraits", "jenbina_eat.png")), path)
            self.assertEqual(kwargs.get("width"), 256)
            caption = st.markdown.call_args[0][0]
            self.assertIn('class="px-portrait-cap"', caption)
            self.assertIn("Jen &lt;3", caption)
            self.assertNotIn("px-sprite", caption)

    def test_no_caption_means_no_caption_strip(self):
        with patch("core.ui.simulation.st") as st:
            display_jenbina_image("jenbina_base.png")
            st.markdown.assert_not_called()

    def test_unknown_state_uses_base_portrait(self):
        with patch("core.ui.simulation.st") as st:
            display_jenbina_image("whatever.png")
            self.assertTrue(st.image.call_args[0][0].endswith("jenbina_base.png"))

    def test_missing_portraits_fall_back_to_placeholder(self):
        with patch("core.ui.simulation.st") as st, patch("core.ui.simulation.IMAGES_DIR", "/nonexistent"):
            display_jenbina_image("jenbina_base.png")
            st.image.assert_not_called()
            self.assertIn(PLACEHOLDER, st.markdown.call_args[0][0])


class TestChatHandlerAvatars(unittest.TestCase):
    @patch("core.interaction.chat_handler.check_injection", return_value=(True, "blocked"))
    def test_live_turn_rows_get_portrait_and_default_user_avatars(self, _):
        st = MagicMock()
        handle_chat_interaction(st, None, None, None, None, user_input="hi", memory_manager=None)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertEqual(len(avatars), 2)
        self.assertIsNone(avatars[0])
        self.assertTrue(avatars[1].endswith(os.path.join("portraits", "jenbina_base.png")))



class TestNavIcon(unittest.TestCase):
    def test_home_link_gets_portrait_icon(self):
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css()
            css = st.markdown.call_args[0][0]
        self.assertIn('[data-testid="stSidebarNav"] li:first-child a::before', css)
        self.assertIn("data:image/png;base64,", css)

    def test_missing_icon_file_adds_no_rule(self):
        with patch("core.ui.pixel_theme.NAV_ICON_PATH", "/nonexistent/jenbina_nav.png"):
            self.assertEqual(nav_icon_css(), "")


class TestWideShell(unittest.TestCase):
    def test_wide_flag_widens_device(self):
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css(wide=True)
            self.assertIn("max-width: 64rem", "".join(c.args[0] for c in st.markdown.call_args_list))
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css()
            # The page width rule only: the 2049 theme's background gradient
            # also uses 64rem and is present in both modes.
            self.assertNotIn("max-width: 64rem", "".join(c.args[0] for c in st.markdown.call_args_list))


class TestEventHtml(unittest.TestCase):
    def test_classes_tag_and_escaping(self):
        html_ = event_html("mood", "Mood <lifted>", meta="23:41")
        self.assertIn('class="px-event px-event-mood"', html_)
        self.assertIn("Mood &lt;lifted&gt;", html_)
        self.assertIn('<span class="px-event-tag">MOOD</span>', html_)
        self.assertNotIn("px-icon", html_)
        self.assertIn('<span class="px-event-meta">23:41</span>', html_)
        self.assertNotIn("<details", html_)

    def test_details_badge_and_ignored_icon(self):
        html_ = event_html("action", "t", details=("why?", "a & b\nc"), badge="<b>B</b>", icon="hunger")
        self.assertIn("<summary>why?</summary>", html_)
        self.assertIn("a &amp; b<br>c", html_)
        self.assertIn("<b>B</b>", html_)
        self.assertIn('<span class="px-event-tag">ACT</span>', html_)
        self.assertNotIn("hunger", html_)

    def test_unknown_kind_uses_generic_tag_and_safe_class(self):
        html_ = event_html("we!rd", "t")
        self.assertIn('px-event-werd"', html_)
        self.assertIn('<span class="px-event-tag">EVENT</span>', html_)

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
