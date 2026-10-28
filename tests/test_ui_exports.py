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
            "inject_pixel_css", "run_single_iteration", "run_simulation_loop", "render_status_rail",
            "render_run_controls", "render_mind_card", "build_timeline", "render_timeline",
            "handle_user_input", "ensure_outreach", "get_event_log",
        ):
            self.assertTrue(hasattr(ui, name), name)
        self.assertFalse(hasattr(ui, "render_chat_interface"))

    def test_chat_page_is_gone(self):
        self.assertFalse(any(p.name.endswith("Chat.py") for p in (ROOT / "core" / "pages").iterdir()))


if __name__ == "__main__":
    unittest.main()
