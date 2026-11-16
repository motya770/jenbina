#!/usr/bin/env python3
"""Tests for the Now, heartbeat and mind cards."""

import os
import sys
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.heartbeat.host import HeartStatus
from core.ui.rail import (
    NullRail, StatusRail, env_line_html, heartbeat_lines,
    render_heartbeat_card, render_mind_card,
)
from tests.test_pixel_ui import FakePerson


class TestStatusRail(unittest.TestCase):
    def test_stage_writes_pill(self):
        slot = MagicMock()
        with patch("core.ui.rail.st") as st, patch("core.ui.chat.st") as chat_st:
            st.session_state = {}
            chat_st.session_state = {"_stage_placeholder": slot}
            StatusRail(slot, MagicMock(), MagicMock()).stage("thinking…")
        html_ = slot.markdown.call_args.args[0]
        self.assertIn("px-stage", html_)
        self.assertIn("thinking…", html_)

    def test_refresh_renders_needs_into_vitals_slot(self):
        vitals = MagicMock()
        with patch("core.ui.rail.st") as st, patch("core.ui.simulation.st") as sim_st:
            StatusRail(MagicMock(), MagicMock(), vitals).refresh(FakePerson({"hunger": 50}, {"joy": 40}))
        vitals.container.assert_called()
        self.assertTrue(any("need-row" in c.args[0] for c in sim_st.markdown.call_args_list))

    def test_live_row_writes_into_live_slot(self):
        live = MagicMock()
        with patch("core.ui.rail.st") as st:
            StatusRail(MagicMock(), MagicMock(), MagicMock(), live_slot=live).live_row("<div>x</div>")
        self.assertIn("<div>x</div>", st.markdown.call_args.args[0])

    def test_null_rail_is_silent(self):
        rail = NullRail()
        rail.stage("x")
        rail.portrait("jenbina_base.png")
        rail.refresh(FakePerson({}, {}))
        rail.live_row("y")

    def test_env_line(self):
        ws = {
            "location": {"name": "Jenbina's House"},
            "time": {"time_of_day": "night"},
            "weather": {"description": "light rain", "temperature": 15.1},
        }
        html_ = env_line_html(ws)
        self.assertNotIn("px-icon", html_)
        self.assertIn("Jenbina&#x27;s House · Night · light rain, 15°C", html_)
        self.assertEqual(env_line_html(None), "Jenbina's House")


NOW = datetime(2026, 11, 15, 7, 23)


def status(**kw):
    base = dict(
        hosting=True, holder=None, phase="awake", phase_since=datetime(2026, 11, 15, 7, 12),
        last_beat_at=NOW - timedelta(minutes=4), next_beat_at=NOW + timedelta(minutes=11),
        note="", busy=False, stage="idle",
    )
    base.update(kw)
    return HeartStatus(**base)


class TestHeartbeatAndMind(unittest.TestCase):
    def test_heartbeat_lines_awake(self):
        self.assertEqual(heartbeat_lines(status(), NOW), [
            "● awake · since 07:12", "last moment 4 min ago · next in 11 min",
        ])

    def test_heartbeat_lines_asleep(self):
        self.assertEqual(heartbeat_lines(status(
            phase="asleep", phase_since=datetime(2026, 11, 14, 23, 40), next_beat_at=None,
        ), NOW), ["● asleep · since 23:40"])

    def test_heartbeat_lines_notes(self):
        capped = heartbeat_lines(status(note="daily_cap", next_beat_at=None), NOW)
        self.assertEqual(capped[1], "last moment 4 min ago")
        self.assertIn("daily limit reached · resting until tomorrow", capped)
        self.assertIn("heart is retrying after errors", heartbeat_lines(status(note="backoff"), NOW))
        self.assertEqual(heartbeat_lines(status(busy=True, stage="deciding…"), NOW)[1], "deciding…")
        self.assertEqual(heartbeat_lines(status(last_beat_at=None, next_beat_at=NOW), NOW)[1],
                         "no moment yet · next in 0 min")

    def test_clock_correction_and_overdue_beat_never_show_negative_minutes(self):
        self.assertEqual(heartbeat_lines(status(
            last_beat_at=NOW + timedelta(minutes=2), next_beat_at=NOW - timedelta(minutes=2),
        ), NOW)[1], "last moment 0 min ago · next in 0 min")

    def test_step_once_is_for_admins_and_disabled_while_asleep(self):
        with patch("core.ui.rail.st") as st:
            st.button.return_value = False
            self.assertFalse(render_heartbeat_card(status(), admin=False, now=NOW))
            st.button.assert_not_called()
            self.assertFalse(render_heartbeat_card(status(), admin=True, now=NOW))
            self.assertEqual(st.button.call_args.args[0], "Step once")
            self.assertEqual(st.button.call_args.kwargs["type"], "primary")
            self.assertFalse(st.button.call_args.kwargs["disabled"])
            render_heartbeat_card(status(phase="asleep"), admin=True, now=NOW)
            self.assertTrue(st.button.call_args.kwargs["disabled"])
            render_heartbeat_card(status(note="daily_cap"), admin=True, now=NOW)
            self.assertTrue(st.button.call_args.kwargs["disabled"])
            st.button.return_value = True
            self.assertTrue(render_heartbeat_card(status(), admin=True, now=NOW))

    def test_mind_card_lists_goals_or_empty_text(self):
        person = SimpleNamespace(
            goal_system=SimpleNamespace(get_goal_stats=lambda: {"goals": [{"description": "feel connected", "progress": 0.1}]}),
            planning_system=None,
            learning_system=None,
            social_cognition=None,
        )
        with patch("core.ui.rail.st") as st:
            st.tabs.return_value = [MagicMock() for _ in range(4)]
            render_mind_card(person, "Matt")
        written = " ".join(str(c.args[0]) for c in st.write.call_args_list + st.markdown.call_args_list)
        self.assertIn("feel connected · 10%", written)
        self.assertIn("No plan.", written)
        self.assertIn("Nothing learned yet.", written)
        self.assertIn("Nothing known yet.", written)


class TestRequestedStep(unittest.TestCase):
    def test_a_requested_moment_is_shown_and_cannot_be_asked_for_twice(self):
        from datetime import datetime, timedelta
        from core.heartbeat.host import HeartStatus
        from core.ui.rail import heartbeat_lines, render_heartbeat_card
        now = datetime(2026, 11, 15, 7, 23)
        status = HeartStatus(True, None, "awake", datetime(2026, 11, 15, 7, 12), now - timedelta(minutes=4),
                             now + timedelta(minutes=11), "", False, "idle", step_requested=True)
        self.assertEqual(heartbeat_lines(status, now)[1], "a moment is coming…")
        with patch("core.ui.rail.st") as st:
            st.button.return_value = False
            render_heartbeat_card(status, admin=True, now=now)
            self.assertTrue(st.button.call_args.kwargs["disabled"])


class TestAboutYouIsReadOnly(unittest.TestCase):
    def test_drawing_never_creates_a_social_model(self):
        from core.person.person import Person
        from core.ui.rail import _about_you_lines
        person = Person()
        person.init_social_cognition()
        with patch("core.ui.rail.st") as st:
            _about_you_lines(person, "Stranger")
            st.write.assert_called_once_with("Nothing known yet.")
        self.assertEqual(person.social_cognition.models, {})


if __name__ == "__main__":
    unittest.main()
