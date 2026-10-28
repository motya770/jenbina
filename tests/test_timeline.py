#!/usr/bin/env python3
"""Tests for the event log (core.timeline) and the chat timeline (core.ui.timeline)."""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.auth.user_db import UserDatabase
from core.timeline import (
    EventLog,
    TimelineEvent,
    lessons_text,
    make_action,
    make_goal,
    make_mood,
    make_move,
    make_plan,
    make_thought,
    mood_changes,
    shorten,
)
from core.timeline.recording import (
    record_action,
    record_goal_changes,
    record_mood,
    record_move,
    record_plan_finished,
    record_plan_step,
    record_replan,
    record_thought,
    snapshot_goals,
)


class TestTitles(unittest.TestCase):
    def test_shorten_cuts_at_word_boundary_with_ellipsis(self):
        self.assertEqual(shorten("attend live music at coupa cafe tonight", 20), "attend live music…")

    def test_shorten_leaves_short_text_alone(self):
        self.assertEqual(shorten("nap", 90), "nap")

    def test_shorten_without_spaces_cuts_hard(self):
        self.assertEqual(len(shorten("x" * 300, 90)), 90)

    def test_lessons_text_joins_lists(self):
        self.assertEqual(lessons_text(["a", "b"]), "a; b")
        self.assertEqual(lessons_text("solo"), "solo")
        self.assertEqual(lessons_text(None), "")

    def test_action_title(self):
        ev = make_action("Attend Live Music at Coupa Cafe", "r", [], 83.4, 85.1, "Jenbina's House", "night", "Clear skies", 15.1)
        self.assertEqual(ev.title, "Jenbina decided to attend live music at coupa cafe")
        self.assertEqual(ev.detail["satisfaction_after"], 85.1)
        self.assertEqual(ev.detail["action"], "Attend Live Music at Coupa Cafe")
        self.assertEqual(ev.kind, "action")

    def test_mood_changes_keeps_top_three_above_one_point(self):
        changes = mood_changes(
            {"trust": 40, "joy": 35, "fear": 10, "anger": 5, "surprise": 20},
            {"trust": 44, "joy": 38, "fear": 10.5, "anger": 1, "surprise": 22},
        )
        self.assertEqual(list(changes), ["trust", "anger", "joy"])
        self.assertEqual(changes["trust"], (40, 44))

    def test_mood_changes_ignores_keys_missing_on_one_side(self):
        self.assertEqual(mood_changes({"trust": 40}, {"joy": 50}), {})

    def test_mood_title_lifted_and_dipped(self):
        self.assertEqual(make_mood({"trust": (40, 44), "joy": (35, 38)}, "chat").title, "Mood lifted: trust 40 → 44, joy 35 → 38")
        self.assertEqual(make_mood({"joy": (35.4, 30.2)}, "action").title, "Mood dipped: joy 35 → 30")
        self.assertIsNone(make_mood({}, "chat"))

    def test_goal_plan_move_titles(self):
        self.assertEqual(make_goal("created", "feel connected", 0).title, "New goal: feel connected")
        self.assertEqual(make_goal("advanced", "feel connected", 0.4).title, "Goal advanced: feel connected → 40%")
        self.assertEqual(make_goal("completed", "feel connected", 1).title, "Goal reached: feel connected")
        self.assertEqual(make_plan("step_completed", "g", "call a friend").title, "Plan step done: call a friend")
        self.assertEqual(make_plan("replanned", "g", "s1").title, "Replanned: g, first step s1")
        self.assertEqual(make_plan("completed", "g", "").title, "Plan finished: g")
        self.assertEqual(make_plan("overridden", "g", "s").title, "Plan step skipped for an urgent need")
        self.assertEqual(make_move("Jenbina's House", "Coupa Cafe").title, "Walked from Jenbina's House to Coupa Cafe")

    def test_thought_keeps_full_text(self):
        ev = make_thought("deliberation", "Quiet tonight. Maybe text someone.")
        self.assertEqual(
            (ev.title, ev.detail),
            ("Quiet tonight. Maybe text someone.", {"mode": "deliberation", "text": "Quiet tonight. Maybe text someone."}),
        )


class TestEventLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = UserDatabase(db_path=self.tmp.name)
        self.uid = self.db.create_or_update_user(
            firebase_uid="u1", email="a@b.c", display_name="A", photo_url="", provider="test"
        )["id"]

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_memory_log_round_trip_oldest_first(self):
        log = EventLog()
        log.record(make_move("a", "b"))
        log.record(make_move("b", "c"))
        self.assertEqual([e.title for e in log.recent()], ["Walked from a to b", "Walked from b to c"])

    def test_memory_log_limit_keeps_newest(self):
        log = EventLog()
        for i in range(5):
            log.record(make_goal("created", str(i), 0))
        self.assertEqual([e.detail["description"] for e in log.recent(2)], ["3", "4"])

    def test_db_log_persists_and_sets_id(self):
        log = EventLog(self.db, self.uid)
        ev = log.record(make_move("a", "b"))
        self.assertIsNotNone(ev.id)
        again = EventLog(self.db, self.uid).recent()
        self.assertEqual((again[0].kind, again[0].title, again[0].detail), ("move", "Walked from a to b", {"from": "a", "to": "b"}))

    def test_record_swallows_storage_errors(self):
        db = MagicMock()
        db.store_event.side_effect = RuntimeError("disk")
        ev = EventLog(db, 1).record(make_move("a", "b"))
        self.assertEqual(ev.title, "Walked from a to b")


class TestRecording(unittest.TestCase):
    def setUp(self):
        self.log = EventLog()

    def test_record_thought_uses_current_thought(self):
        im = SimpleNamespace(get_current_thought=lambda: SimpleNamespace(content="Quiet night.", mode="deliberation"))
        ev = record_thought(self.log, im)
        self.assertEqual((ev.kind, ev.title, ev.detail["mode"]), ("thought", "Quiet night.", "deliberation"))
        self.assertIsNone(record_thought(self.log, None))
        self.assertIsNone(record_thought(self.log, SimpleNamespace(get_current_thought=lambda: None)))

    def test_record_move_only_on_change(self):
        self.assertIsNone(record_move(self.log, "Home", "Home"))
        self.assertIsNone(record_move(self.log, "Home", None))
        self.assertEqual(record_move(self.log, "Home", "Coupa Cafe").detail, {"from": "Home", "to": "Coupa Cafe"})

    def test_record_action_reads_world_summary(self):
        ws = {"location": {"name": "Jenbina's House"}, "time": {"time_of_day": "night"},
              "weather": {"description": "Clear skies", "temperature": 15.1}}
        ev = record_action(self.log, {"chosen_action": "Nap", "reasoning": "tired", "lessons_applied": "rest early"}, 80.0, 82.5, ws)
        self.assertEqual(ev.detail["location"], "Jenbina's House")
        self.assertEqual(ev.detail["lessons"], ["rest early"])
        self.assertEqual(record_action(self.log, {"chosen_action": "Nap"}, 1, 2, {}).detail["location"], "")

    def test_record_mood_none_when_unchanged(self):
        self.assertIsNone(record_mood(self.log, {"joy": 30}, {"joy": 30.4}, "chat"))
        self.assertEqual(record_mood(self.log, {"joy": 30}, {"joy": 35}, "chat").detail["source"], "chat")

    def test_snapshot_goals(self):
        gs = SimpleNamespace(goals=[SimpleNamespace(description="a", status="active", progress=0.1)])
        self.assertEqual(snapshot_goals(gs), {"a": ("active", 0.1)})
        self.assertEqual(snapshot_goals(None), {})

    def test_goal_changes(self):
        before = {"a": ("active", 0.1), "b": ("active", 0.5), "c": ("active", 0.2)}
        after = {"a": ("active", 0.3), "b": ("completed", 1.0), "c": ("active", 0.205), "d": ("active", 0.0)}
        titles = [e.title for e in record_goal_changes(self.log, before, after)]
        self.assertEqual(titles, ["Goal advanced: a → 30%", "Goal reached: b", "New goal: d"])

    def test_plan_events(self):
        self.assertEqual(record_plan_step(self.log, "step_completed", "g", "call").title, "Plan step done: call")
        self.assertEqual(record_plan_step(self.log, "step_overridden", "g", "call").title, "Plan step skipped for an urgent need")
        self.assertIsNone(record_plan_step(self.log, None, "g", "call"))
        plan = SimpleNamespace(goal_description="g", steps=[SimpleNamespace(description="s1")])
        self.assertEqual(record_replan(self.log, plan).title, "Replanned: g, first step s1")
        self.assertIsNone(record_replan(self.log, None))
        self.assertEqual(record_plan_finished(self.log, plan).title, "Plan finished: g")


if __name__ == "__main__":
    unittest.main()
