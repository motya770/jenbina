#!/usr/bin/env python3
"""Tests for the event log (core.timeline) and the chat timeline (core.ui.timeline)."""

import os
import sys
import tempfile
import unittest
from collections import namedtuple
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
from core.ui.timeline import (
    EMPTY_TEXT,
    build_timeline,
    first_sentence,
    render_timeline,
)

Msg = namedtuple("Msg", "timestamp sender content message_type")
T = datetime(2026, 10, 27, 23, 38)


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


class TestBuildTimeline(unittest.TestCase):
    def test_merges_by_time_and_detects_speakers(self):
        msgs = [Msg(T, "person", "hi", "greeting"), Msg(T + timedelta(minutes=3), "Matt", "hello", "text")]
        evs = [make_thought("x", "Quiet.")]
        evs[0].created_at = T + timedelta(minutes=1)
        kinds = [i.kind for i in build_timeline(msgs, evs)]
        self.assertEqual(kinds, ["marker", "jenbina", "thought", "user"])

    def test_meta_marks_outreach(self):
        items = build_timeline([Msg(T, "person", "hi", "proactive"), Msg(T, "person", "hi", "text")], [])
        self.assertEqual(items[1].meta, "23:38 · she reached out first")
        self.assertEqual(items[2].meta, "23:38")

    def test_markers_on_gap_and_day_change(self):
        msgs = [
            Msg(T, "Matt", "a", "text"),
            Msg(T + timedelta(minutes=61), "Matt", "b", "text"),
            Msg(T + timedelta(days=1, minutes=5), "Matt", "c", "text"),
        ]
        markers = [i.text for i in build_timeline(msgs, []) if i.kind == "marker"]
        self.assertEqual(markers[0], "23:38")
        self.assertEqual(markers[1], "00:39 · Wed 28 Oct")
        self.assertEqual(len(markers), 3)

    def test_marker_carries_world_context_of_latest_action(self):
        T0 = datetime(2026, 10, 27, 20, 0)
        act = make_action("nap", "", [], 1, 2, "Jenbina's House", "night", "Clear skies", 15.1)
        act.created_at = T0
        items = build_timeline([Msg(T0 + timedelta(hours=2), "Matt", "a", "text")], [act])
        self.assertEqual([i.kind for i in items], ["marker", "action", "marker", "user"])
        self.assertEqual(items[0].text, "20:00 · Jenbina's House · night · Clear skies, 15°C")
        self.assertEqual(items[2].text, "22:00 · Jenbina's House · night · Clear skies, 15°C")

    def test_filters(self):
        evs = [make_thought("x", "t"), make_move("a", "b"), make_goal("created", "g", 0)]
        msgs = [Msg(T, "Matt", "m", "text")]
        self.assertEqual([i.kind for i in build_timeline(msgs, evs, filter_name="Chat") if i.kind != "marker"], ["user"])
        self.assertEqual({i.kind for i in build_timeline(msgs, evs, filter_name="Her day") if i.kind != "marker"}, {"move", "goal"})
        self.assertEqual([i.kind for i in build_timeline(msgs, evs, filter_name="Thoughts") if i.kind != "marker"], ["thought"])

    def test_limit_keeps_newest(self):
        msgs = [Msg(T + timedelta(minutes=i), "Matt", str(i), "text") for i in range(10)]
        texts = [i.text for i in build_timeline(msgs, [], limit=3) if i.kind == "user"]
        self.assertEqual(texts, ["7", "8", "9"])

    def test_equal_timestamps_put_event_before_message(self):
        ev = make_move("a", "b")
        ev.created_at = T
        kinds = [i.kind for i in build_timeline([Msg(T, "person", "x", "proactive")], [ev])]
        self.assertEqual(kinds, ["marker", "move", "jenbina"])

    def test_empty_inputs_give_no_items(self):
        self.assertEqual(build_timeline([], []), [])

    def test_first_sentence(self):
        self.assertEqual(first_sentence("Quiet night. Maybe text someone."), ("Quiet night.", "Maybe text someone."))

    def test_first_sentence_without_punctuation_is_whole_text(self):
        self.assertEqual(first_sentence("maybe text someone"), ("maybe text someone", ""))


class TestRenderTimeline(unittest.TestCase):
    def test_rows_get_sprite_avatars_and_captions(self):
        items = build_timeline([Msg(T, "Matt", "hi", "text"), Msg(T, "person", "hello", "greeting")], [])
        with patch("core.ui.timeline.st") as st:
            render_timeline(items)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertTrue(avatars[0].endswith("icons/player.png"))
        self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))
        self.assertIn("she reached out first", st.caption.call_args_list[-1].args[0])

    def test_action_row_has_badge_and_details(self):
        act = make_action("Eat soup", "hungry", ["eat early"], 80, 82, "Home", "noon", "Sunny", 20)
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [act]))
        html_ = st.markdown.call_args_list[-1].args[0]
        for needle in ("px-event-action", "Jenbina decided to eat soup", "80% → 82% (+2.0%)",
                       "<summary>why?</summary>", "Lessons applied: eat early", 'alt="hunger"'):
            self.assertIn(needle, html_)

    def test_thought_row_details_only_when_longer(self):
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [make_thought("x", "Quiet night. Maybe text someone.")]))
            long_html = st.markdown.call_args_list[-1].args[0]
            render_timeline(build_timeline([], [make_thought("x", "Quiet night.")]))
            short_html = st.markdown.call_args_list[-1].args[0]
        self.assertIn("<summary>more</summary>", long_html)
        self.assertNotIn("<details", short_html)

    def test_unknown_kind_renders_title(self):
        ev = TimelineEvent(kind="mystery", title="Something happened")
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [ev]))
        self.assertIn("Something happened", st.markdown.call_args_list[-1].args[0])

    def test_empty_timeline_shows_empty_text(self):
        with patch("core.ui.timeline.st") as st:
            render_timeline([])
        self.assertIn(EMPTY_TEXT, st.markdown.call_args[0][0])


class TestCorruptRows(unittest.TestCase):
    def test_corrupt_action_detail_still_renders_title(self):
        ev = TimelineEvent(kind="action", title="Jenbina decided to nap",
                           detail={"action": "nap", "satisfaction_before": "n/a", "satisfaction_after": None})
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [ev]))
        self.assertIn("Jenbina decided to nap", st.markdown.call_args_list[-1].args[0])


if __name__ == "__main__":
    unittest.main()
