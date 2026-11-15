#!/usr/bin/env python3
"""The home screen's building blocks are exported from core.ui and the old
Chat page is gone."""

import os
import sys
import unittest
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

ROOT = Path(__file__).resolve().parent.parent


class TestUiExports(unittest.TestCase):
    def test_home_screen_building_blocks_are_exported(self):
        import core.ui as ui
        for name in (
            "render_full_sidebar", "inject_pixel_css", "render_status_rail", "render_heartbeat_card",
            "render_mind_card", "build_timeline", "render_timeline", "handle_user_input", "ensure_greeting",
            "require_auth", "init_llm", "init_session_state", "save_person_state", "get_host",
        ):
            self.assertTrue(hasattr(ui, name), name)
        for gone in ("run_single_iteration", "run_simulation_loop", "render_run_controls",
                     "ensure_outreach", "get_event_log", "get_person_dict", "render_chat_interface"):
            self.assertFalse(hasattr(ui, gone), gone)

    def test_nothing_makes_her_act_on_page_open(self):
        app = (ROOT / "core" / "app.py").read_text()
        for gone in ("simulation_auto_started", "run_simulation_loop", "render_run_controls", "Run N"):
            self.assertNotIn(gone, app)
        self.assertIn("st.fragment", app)
        self.assertIn("chat_turn", app)

    def test_heartbeat_package_has_no_streamlit(self):
        for path in (ROOT / "core" / "heartbeat").glob("*.py"):
            self.assertNotIn("streamlit", path.read_text(), str(path))

    def test_chat_page_is_gone(self):
        self.assertFalse(any(p.name.endswith("Chat.py") for p in (ROOT / "core" / "pages").iterdir()))


if __name__ == "__main__":
    unittest.main()
