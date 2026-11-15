"""Pure heartbeat decisions on a fixed clock, with no services or waiting."""

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from core.heartbeat.rhythm import (
    ASLEEP,
    AWAKE,
    BEAT,
    FALL_ASLEEP,
    HOME,
    SLEEP_TICK,
    WAIT,
    WAKE,
    RhythmConfig,
    Situation,
    Step,
    beats_today,
    decide,
    effective_interval,
    is_night,
    lost_time,
    next_beat_at,
    should_fall_asleep,
)


CFG = RhythmConfig()
NOON = datetime(2026, 11, 15, 12, 0, 0)


def awake(now=NOON, **overrides):
    situation = Situation.fresh(now - timedelta(hours=2))
    for name, value in overrides.items():
        setattr(situation, name, value)
    return situation


def asleep(started, **overrides):
    situation = Situation.fresh(started)
    situation.phase = ASLEEP
    situation.last_sleep_tick_at = started
    for name, value in overrides.items():
        setattr(situation, name, value)
    return situation


class TestAwake(unittest.TestCase):
    def test_first_beat_is_immediate(self):
        self.assertEqual(decide(awake(), NOON, CFG), Step(BEAT))

    def test_waits_for_the_interval_then_beats(self):
        situation = awake(last_beat_at=NOON - timedelta(minutes=14, seconds=59))
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "interval"))
        situation.last_beat_at = NOON - timedelta(minutes=15)
        self.assertEqual(decide(situation, NOON, CFG), Step(BEAT))

    def test_conversation_postpones_the_beat(self):
        situation = awake(
            last_beat_at=NOON - timedelta(hours=1),
            last_chat_at=NOON - timedelta(minutes=2, seconds=59),
        )
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "attention"))
        situation.last_chat_at = NOON - timedelta(minutes=3)
        self.assertEqual(decide(situation, NOON, CFG), Step(BEAT))

    def test_daily_cap_holds_until_the_next_day(self):
        situation = awake(
            last_beat_at=NOON - timedelta(hours=1),
            beats_day="2026-11-15",
            beats_count=80,
        )
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "daily_cap"))
        tomorrow = NOON + timedelta(days=1)
        situation.awake_since = tomorrow - timedelta(hours=2)
        self.assertEqual(beats_today(situation, tomorrow), 0)
        self.assertEqual(decide(situation, tomorrow, CFG), Step(BEAT))

    def test_backoff_doubles_from_the_third_failure_up_to_an_hour(self):
        for failures, minutes in ((0, 15), (2, 15), (3, 30), (4, 60), (9, 60), (10000, 60)):
            with self.subTest(failures=failures):
                self.assertEqual(effective_interval(CFG, failures), timedelta(minutes=minutes))
        situation = awake(last_beat_at=NOON - timedelta(minutes=20), consecutive_failures=3)
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "backoff"))
        self.assertEqual(decide(situation, NOON + timedelta(minutes=10), CFG), Step(BEAT))
        situation.consecutive_failures = 0
        self.assertEqual(decide(situation, NOON, CFG), Step(BEAT))

    def test_backoff_never_beats_more_often_than_configured(self):
        slow = RhythmConfig(beat_interval=timedelta(hours=2))
        for failures in (3, 9):
            with self.subTest(failures=failures):
                self.assertEqual(effective_interval(slow, failures), timedelta(hours=2))
                situation = awake(last_beat_at=NOON - timedelta(hours=1), consecutive_failures=failures)
                self.assertEqual(decide(situation, NOON, slow), Step(WAIT, "backoff"))
                self.assertEqual(next_beat_at(situation, NOON, slow), NOON + timedelta(hours=1))

    def test_twenty_hours_awake_forces_sleep(self):
        situation = awake(awake_since=NOON - timedelta(hours=20) + timedelta(seconds=1))
        self.assertEqual(decide(situation, NOON, CFG), Step(BEAT))
        situation.awake_since -= timedelta(seconds=1)
        self.assertEqual(decide(situation, NOON, CFG), Step(FALL_ASLEEP, "exhausted"))
        self.assertEqual(decide(situation, NOON, RhythmConfig(sleep_enabled=False)), Step(BEAT))

    def test_attention_precedes_exhaustion_and_exhaustion_precedes_the_cap(self):
        situation = awake(
            awake_since=NOON - timedelta(hours=20),
            beats_day="2026-11-15",
            beats_count=80,
            last_chat_at=NOON,
        )
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "attention"))
        situation.last_chat_at = NOON - timedelta(minutes=3)
        self.assertEqual(decide(situation, NOON, CFG), Step(FALL_ASLEEP, "exhausted"))
        situation.awake_since = NOON
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "daily_cap"))

    def test_forced_sleep_waits_for_the_conversation_to_end(self):
        situation = awake(
            awake_since=NOON - timedelta(hours=20),
            last_chat_at=NOON - timedelta(minutes=1),
        )
        self.assertEqual(decide(situation, NOON, CFG), Step(WAIT, "attention"))
        situation.last_chat_at = NOON - timedelta(minutes=3)
        self.assertEqual(decide(situation, NOON, CFG), Step(FALL_ASLEEP, "exhausted"))

    def test_clock_moving_backwards_neither_crashes_nor_beats(self):
        future = NOON + timedelta(hours=1)
        for values in (
            {"last_beat_at": future},
            {"last_chat_at": future},
            {"last_beat_at": future, "last_chat_at": future, "awake_since": future},
        ):
            with self.subTest(values=values):
                self.assertEqual(decide(awake(**values), NOON, CFG).kind, WAIT)


class TestAsleep(unittest.TestCase):
    NIGHT = datetime(2026, 11, 15, 23, 40, 0)

    def test_no_beats_while_asleep_only_ticks(self):
        situation = asleep(self.NIGHT)
        self.assertEqual(decide(situation, self.NIGHT + timedelta(minutes=14), CFG), Step(WAIT, "asleep"))
        self.assertEqual(decide(situation, self.NIGHT + timedelta(minutes=15), CFG), Step(SLEEP_TICK))
        situation.last_sleep_tick_at = self.NIGHT + timedelta(minutes=15)
        self.assertEqual(decide(situation, self.NIGHT + timedelta(minutes=29), CFG), Step(WAIT, "asleep"))

    def test_missing_tick_time_uses_the_sleep_start(self):
        situation = asleep(self.NIGHT, last_sleep_tick_at=None)
        self.assertEqual(decide(situation, self.NIGHT + timedelta(minutes=15), CFG), Step(SLEEP_TICK))

    def test_wakes_in_the_morning_after_six_hours(self):
        situation = asleep(self.NIGHT, last_sleep_tick_at=self.NIGHT + timedelta(hours=6, minutes=15))
        self.assertEqual(decide(situation, datetime(2026, 11, 16, 5, 59), CFG), Step(WAIT, "asleep"))
        self.assertEqual(decide(situation, datetime(2026, 11, 16, 6, 0), CFG), Step(WAKE, "morning"))

    def test_does_not_wake_in_daylight_before_six_hours(self):
        situation = asleep(datetime(2026, 11, 16, 4, 0))
        self.assertEqual(decide(situation, datetime(2026, 11, 16, 9, 59), CFG), Step(SLEEP_TICK))
        self.assertEqual(decide(situation, datetime(2026, 11, 16, 10, 0), CFG), Step(WAKE, "morning"))

    def test_nine_hours_wakes_her_even_at_night(self):
        situation = asleep(datetime(2026, 11, 15, 13, 0))
        self.assertEqual(decide(situation, datetime(2026, 11, 15, 22, 0), CFG), Step(WAKE, "slept_enough"))

    def test_clock_moving_backwards_does_not_tick_or_wake(self):
        situation = asleep(self.NIGHT)
        self.assertEqual(decide(situation, self.NIGHT - timedelta(hours=1), CFG), Step(WAIT, "asleep"))


class TestRules(unittest.TestCase):
    def test_falling_asleep(self):
        self.assertTrue(should_fall_asleep("sleep", "night", 90.0, CFG))
        self.assertTrue(should_fall_asleep("sleep", "afternoon", 29.9, CFG))
        self.assertFalse(should_fall_asleep("sleep", "afternoon", 30.0, CFG))
        self.assertFalse(should_fall_asleep("rest", "night", 10.0, CFG))
        self.assertFalse(should_fall_asleep(None, "night", 10.0, CFG))
        self.assertFalse(should_fall_asleep("sleep", "night", 10.0, RhythmConfig(sleep_enabled=False)))

    def test_night_is_21_to_6(self):
        self.assertTrue(is_night(datetime(2026, 1, 1, 21, 0)))
        self.assertTrue(is_night(datetime(2026, 1, 1, 5, 59)))
        self.assertFalse(is_night(datetime(2026, 1, 1, 6, 0)))
        self.assertFalse(is_night(datetime(2026, 1, 1, 20, 59)))

    def test_lost_time_needs_more_than_three_intervals(self):
        self.assertIsNone(lost_time(None, NOON, CFG))
        self.assertIsNone(lost_time(NOON - timedelta(minutes=45), NOON, CFG))
        self.assertEqual(lost_time(NOON - timedelta(minutes=46), NOON, CFG), timedelta(minutes=46))
        self.assertIsNone(lost_time(NOON + timedelta(hours=1), NOON, CFG))
        fast = RhythmConfig(beat_interval=timedelta(minutes=5))
        self.assertIsNone(lost_time(NOON - timedelta(minutes=15), NOON, fast))
        self.assertEqual(lost_time(NOON - timedelta(minutes=16), NOON, fast), timedelta(minutes=16))

    def test_config_from_env(self):
        cfg = RhythmConfig.from_env({
            "JENBINA_BEAT_MINUTES": "5",
            "JENBINA_MAX_BEATS_PER_DAY": "10",
            "JENBINA_DISABLE_SLEEP": "1",
        })
        self.assertEqual((cfg.beat_interval, cfg.max_beats_per_day, cfg.sleep_enabled),
                         (timedelta(minutes=5), 10, False))
        self.assertEqual(RhythmConfig.from_env({"JENBINA_BEAT_MINUTES": "2.5"}).beat_interval,
                         timedelta(minutes=2, seconds=30))
        self.assertEqual(RhythmConfig.from_env({}), CFG)
        with patch.dict("os.environ", {"JENBINA_BEAT_MINUTES": "7.5"}, clear=True):
            self.assertEqual(RhythmConfig.from_env().beat_interval, timedelta(minutes=7, seconds=30))
        for flag in ("0", "true", "yes", ""):
            with self.subTest(flag=flag):
                self.assertTrue(RhythmConfig.from_env({"JENBINA_DISABLE_SLEEP": flag}).sleep_enabled)

    def test_config_from_env_ignores_bad_values(self):
        for value in ("0", "-2", "abc", "", "nan", "inf", "1e100", "0.00000000001"):
            with self.subTest(interval=value):
                self.assertEqual(RhythmConfig.from_env({"JENBINA_BEAT_MINUTES": value}).beat_interval,
                                 timedelta(minutes=15))
        for value in ("0", "-1", "abc", "", "1.5"):
            with self.subTest(cap=value):
                self.assertEqual(RhythmConfig.from_env({"JENBINA_MAX_BEATS_PER_DAY": value}).max_beats_per_day, 80)

    def test_next_beat_time_for_the_card(self):
        situation = awake(last_beat_at=NOON - timedelta(minutes=4))
        self.assertEqual(next_beat_at(situation, NOON, CFG), NOON + timedelta(minutes=11))
        self.assertEqual(next_beat_at(awake(), NOON, CFG), NOON)
        situation.last_beat_at = NOON - timedelta(hours=1)
        self.assertEqual(next_beat_at(situation, NOON, CFG), NOON)
        situation.last_chat_at = NOON - timedelta(minutes=1)
        self.assertEqual(next_beat_at(situation, NOON, CFG), NOON + timedelta(minutes=2))
        situation.consecutive_failures = 4
        situation.last_beat_at = NOON - timedelta(minutes=20)
        self.assertEqual(next_beat_at(situation, NOON, CFG), NOON + timedelta(minutes=40))

    def test_next_beat_is_absent_while_asleep_or_capped(self):
        self.assertIsNone(next_beat_at(asleep(NOON), NOON, CFG))
        situation = awake(beats_day="2026-11-15", beats_count=80)
        self.assertIsNone(next_beat_at(situation, NOON, CFG))
        tomorrow = NOON + timedelta(days=1)
        self.assertEqual(next_beat_at(situation, tomorrow, CFG), tomorrow)


class TestSituation(unittest.TestCase):
    def test_non_dict_situation_loads_fresh(self):
        for data in (None, [], ["phase"], "awake", 42):
            with self.subTest(data=data):
                self.assertEqual(Situation.from_dict(data, NOON), Situation.fresh(NOON))

    def test_fresh_starts_awake_at_home_with_independent_history(self):
        situation = Situation.fresh(NOON)
        self.assertEqual((situation.phase, situation.phase_since, situation.awake_since, situation.location),
                         (AWAKE, NOON, NOON, HOME))
        self.assertEqual(Situation.from_dict({}, NOON), situation)
        situation.history.append({"iteration": 1})
        situation.last_responses["action_decision"] = {}
        other = Situation.fresh(NOON)
        self.assertEqual((other.history, other.last_responses), ([], {}))

    def test_situation_round_trips_through_json(self):
        situation = asleep(
            NOON,
            awake_since=NOON - timedelta(hours=10),
            location="Coupa Cafe",
            last_beat_at=NOON - timedelta(minutes=15),
            beats_day="2026-11-15",
            beats_count=7,
            consecutive_failures=2,
            last_chat_at=NOON - timedelta(hours=3),
            beat_index=42,
            interrupted_sleep_started_at=NOON - timedelta(hours=1),
            woken_by_message_at=NOON - timedelta(minutes=30),
            history=[{"iteration": 1, "timestamp": "2026-11-15T11:45:00"}],
            last_responses={"action_decision": {"chosen_action": "Sleep"}},
        )
        data = json.loads(json.dumps(situation.to_dict()))
        self.assertEqual(data["phase_since"], "2026-11-15T12:00:00")
        self.assertEqual(Situation.from_dict(data, NOON + timedelta(days=1)), situation)
        fresh = Situation.fresh(NOON)
        self.assertIsNone(fresh.to_dict()["last_beat_at"])
        self.assertEqual(Situation.from_dict(json.loads(json.dumps(fresh.to_dict())), NOON), fresh)

    def test_situation_tolerates_missing_and_unparseable_fields(self):
        situation = Situation.from_dict({"location": "Coupa Cafe", "phase_since": "not a date", "future_field": 1}, NOON)
        expected = Situation.fresh(NOON)
        expected.location = "Coupa Cafe"
        self.assertEqual(situation, expected)
        malformed = {
            "phase": "dreaming", "phase_since": None, "awake_since": 1,
            "location": [], "last_beat_at": "broken", "last_sleep_tick_at": {},
            "beats_day": "not a day", "beats_count": "seven", "consecutive_failures": -1,
            "last_chat_at": 5, "beat_index": True, "interrupted_sleep_started_at": "broken",
            "woken_by_message_at": [], "history": {}, "last_responses": [],
        }
        self.assertEqual(Situation.from_dict(malformed, NOON), Situation.fresh(NOON))


if __name__ == "__main__":
    unittest.main()
