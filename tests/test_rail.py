#!/usr/bin/env python3
"""Tests for the status rail (core.ui.rail): the Now card handles, the run
controls and the mind card."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.ui.rail import NullRail, StatusRail, env_line_html, render_mind_card, render_run_controls
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
        self.assertIn('alt="rain"', html_)
        self.assertIn("Jenbina&#x27;s House · Night · light rain, 15°C", html_)
        self.assertEqual(env_line_html(None), "Jenbina's House")


class TestControlsAndMind(unittest.TestCase):
    def test_run_controls_keys_and_labels(self):
        with patch("core.ui.rail.st") as st:
            st.number_input.side_effect = [5, 3]
            st.button.side_effect = [False, True]
            controls = render_run_controls()
        self.assertEqual(controls, {"num_iterations": 5, "delay_seconds": 3, "run_loop": True, "single_run": False})
        self.assertEqual([c.args[0] for c in st.button.call_args_list], ["Step once", "Run 5"])

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


if __name__ == "__main__":
    unittest.main()
