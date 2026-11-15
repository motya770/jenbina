"""The host owns one live mind; its clock, runner and database are local fakes."""

import os
import sqlite3
import tempfile
import threading
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from core.auth.user_db import UserDatabase
from core.heartbeat.being import BeingStateError
from core.heartbeat.host import _PROCESS_HOST, JenbinaHost, NotHostingError, process_host
from core.heartbeat.rhythm import (
    ASLEEP, AWAKE, BEAT, FALL_ASLEEP, SLEEP_TICK, WAIT, WAKE, RhythmConfig, Step,
)
from core.person.person import Message, Person
from core.heartbeat.store import BeingStore


NOW = datetime(2026, 11, 15, 12, 0)
ANN = {"id": 1, "display_name": "Ann"}
BOB = {"id": 2, "display_name": "Bob"}
STALE = timedelta(seconds=120)


class HostCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.db_path = os.path.join(temporary.name, "users.db")
        self.user_db = UserDatabase(self.db_path)
        self.store = BeingStore(self.db_path)
        for user in (ANN, BOB):
            created = self.user_db.create_or_update_user(
                firebase_uid=f"user-{user['id']}", email=f"user-{user['id']}@example.test",
                display_name=user["display_name"],
            )
            self.assertEqual(created["id"], user["id"])
        self.now = NOW
        self.owner = "test:1:aa"
        self.llm, self.llm_json_mode, self.insight_llm = MagicMock(), MagicMock(), MagicMock()
        self.calls = []
        self.failures_left = 0
        self.overrides = {}
        self.location = None
        self.host = self.make_host()
        self.assertTrue(self.host.start(threads=False))
        self.host.person.suspend_until(self.now)

    def make_host(self, **kwargs):
        options = dict(
            clock=lambda: self.now, iteration_fn=self.iteration,
            meta_cognitive_system=MagicMock(), owner=self.owner,
        )
        options.update(kwargs)
        host = JenbinaHost(self.store, self.user_db, self.llm, self.llm_json_mode,
                           self.insight_llm, **options)
        self.addCleanup(host.stop)
        return host

    def iteration(self, **kwargs):
        self.calls.append(kwargs)
        if self.failures_left:
            self.failures_left -= 1
            raise RuntimeError("fake beat failed")
        person, context = kwargs["person"], kwargs["context"]
        person.update_all_needs(now=self.now)
        context["status"].stage("deciding…")
        context["debug_iterations"].append({"iteration": kwargs["iteration"] + 1})
        if self.location is not None:
            context["jenbina_location"] = self.location
        result = dict(
            needs_response={"raw": "assessment"}, world_description={"weather": "clear"},
            action_decision={"chosen_action": "Read a book"}, state_response={"mood": "content"},
            person_dict={"maslow_needs": {"overall_satisfaction": 70}, "emotions": {"joy": 30}},
            world_summary={"location": {"name": "Home"}, "time": {"time_of_day": "afternoon"}},
            iteration_duration=2.5, satisfaction_delta=3.0, matched_action="read",
            fell_asleep=False, proactive_sent_to=None,
        )
        result.update(self.overrides)
        self.overrides = {}
        return result

    def advance(self, **delta):
        self.now += timedelta(**delta)

    def live(self, hours=0, minutes=0, until=None):
        until = until or self.now + timedelta(hours=hours, minutes=minutes)
        steps = []
        while self.now < until:
            self.now = min(until, self.now + timedelta(minutes=5))
            steps.append(self.host.tick())
        return steps

    def put_to_sleep(self, at, sleep_need=None, hunger=None):
        self.now = at
        # Establish a live pass at the setup time before entering sleep.
        self.host.tick()
        self.host.person.suspend_until(at)
        for name, value in (("sleep", sleep_need), ("hunger", hunger)):
            if value is not None:
                self.host.person.maslow_needs.needs[name].satisfaction = value
        with self.host.lock:
            self.host._fall_asleep(at, "chose")

    def next_result(self, **overrides):
        self.overrides = overrides

    def fail_next(self, n):
        self.failures_left = n

    def event_kinds(self):
        return [event["kind"] for event in self.store.get_events()]


class TestOwnership(HostCase):
    def test_second_host_does_not_host_or_load_state(self):
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            other = self.make_host(owner="other:1:zz")
            with patch.object(self.store, "load_state", wraps=self.store.load_state) as load:
                self.assertFalse(other.start(threads=False))
                load.assert_not_called()
        self.assertFalse(other.hosting)
        self.assertEqual(other.status().holder, self.owner)
        self.assertEqual(other.tick(), Step(WAIT, "not_hosting"))
        self.assertEqual(other.step_once(), "not_hosting")

    def test_losing_the_lease_stops_the_heart(self):
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.assertFalse(self.host.pulse())
        self.assertFalse(self.host.hosting)
        self.assertEqual(self.host.tick(), Step(WAIT, "not_hosting"))

    def test_a_tick_checks_ownership_before_starting_a_new_beat(self):
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.assertEqual(self.host.tick(), Step(WAIT, "not_hosting"))
        self.assertFalse(self.host.hosting)
        self.assertEqual(self.calls, [])

    def test_a_manual_beat_checks_ownership_before_starting(self):
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.assertEqual(self.host.step_once(), "not_hosting")
        self.assertEqual(self.calls, [])

    def test_a_chat_checks_ownership_before_exposing_the_mind(self):
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        with self.assertRaisesRegex(RuntimeError, "not living in this process"):
            with self.host.chat_turn(ANN):
                self.fail("A host without a lease must not begin a chat")
        self.assertIsNone(self.host.situation.last_chat_at)

    def test_a_greeting_checks_ownership_before_exposing_the_mind(self):
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        with self.host.greeting_turn(ANN) as turn:
            self.assertIsNone(turn)
        self.assertFalse(self.host.hosting)

    def test_save_is_fenced_after_another_owner_takes_over(self):
        self.host.save()
        before = self.store.load_state()
        self.store.release_lease(self.owner)
        self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.host.person.name = "Must not overwrite her"
        self.host.save()
        self.assertFalse(self.host.hosting)
        self.host.stop()
        self.assertEqual(self.store.load_state(), before)

    def test_a_storage_error_while_renewing_does_not_stop_the_heart(self):
        with patch.object(self.store, "renew_lease", side_effect=sqlite3.OperationalError("database is locked")):
            self.assertTrue(self.host.pulse())
        self.assertTrue(self.host.hosting)
        self.assertEqual(self.host.tick(), Step(BEAT))

    def test_an_impatient_stop_abandons_a_beat_in_flight_and_frees_the_lease(self):
        self.host.tick()
        saved = self.store.load_state()
        holding, release = threading.Event(), threading.Event()

        def hold_the_mind():
            with self.host.lock:
                self.host.person.name = "changed mid-beat"
                holding.set()
                release.wait()

        thread = threading.Thread(target=hold_the_mind)
        thread.start()
        try:
            holding.wait()
            self.host.stop(patience=0)
            self.assertFalse(self.host.hosting)
            self.assertEqual(self.store.load_state(), saved)
            with patch("core.heartbeat.store.owner_is_dead", return_value=False):
                other = self.store.acquire_lease("other:1:zz", self.now, timedelta(seconds=120))
            self.assertTrue(other.acquired)
        finally:
            release.set()
            thread.join()
        self.host.save()                                      # the abandoned beat's save is a no-op
        self.assertEqual(self.store.load_state(), saved)

    def test_stop_saves_renews_and_releases_the_lease_only_once(self):
        self.host.person.name = "Saved Jenbina"
        self.advance(minutes=2)
        self.host.stop()
        saved = self.store.load_state()
        self.assertEqual(Person.deserialize(saved[0]).name, "Saved Jenbina")
        self.assertFalse(self.host.hosting)
        self.advance(minutes=1)
        self.host.stop()
        lease = self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.assertTrue(lease.acquired)
        self.assertEqual(lease.previous_renewed_at, NOW + timedelta(minutes=2))
        self.assertEqual(self.store.load_state(), saved)

    def test_only_one_caller_at_a_time_is_inside_start(self):
        # Two tabs reconnecting at once: the second caller must not be able to
        # stop the threads the first one has just started.
        seen = []
        with patch.object(self.host, "_start", side_effect=lambda threads: seen.append(
                self.host._start_lock.locked()) or True):
            self.assertTrue(self.host.start())
        self.assertEqual(seen, [True])
        self.assertFalse(self.host._start_lock.locked())

    def test_the_process_has_one_host_however_often_it_is_asked_for(self):
        import sys
        saved = sys.__dict__.pop(_PROCESS_HOST, None)
        try:
            build = MagicMock(side_effect=lambda: object())
            first = process_host(build)
            self.assertIs(process_host(build), first)
            self.assertEqual(build.call_count, 1)
        finally:
            sys.__dict__.pop(_PROCESS_HOST, None)
            if saved is not None:
                sys.__dict__[_PROCESS_HOST] = saved

    def test_a_chat_on_a_host_that_lost_her_raises_the_named_error(self):
        self.host.stop()
        with self.assertRaises(NotHostingError):
            with self.host.chat_turn(ANN):
                pass

    def test_start_is_idempotent_and_can_retry_after_refusal(self):
        person = self.host.person
        self.assertTrue(self.host.start(threads=False))
        self.assertIs(self.host.person, person)
        other = self.make_host(owner="other:1:zz")
        self.assertFalse(other.start(threads=False))
        self.host.stop()
        self.assertTrue(other.start(threads=False))
        self.assertIsNone(other.status().holder)

    def test_start_and_stop_manage_two_daemon_threads(self):
        self.host.stop()
        host = self.make_host()
        with patch("core.heartbeat.host.threading.Thread") as thread:
            self.assertTrue(host.start())
            host.start()
            self.assertEqual(thread.call_count, 2)
            self.assertTrue(all(call.kwargs["daemon"] for call in thread.call_args_list))
            self.assertEqual(thread.return_value.start.call_count, 2)
            host.stop()
            self.assertEqual(thread.return_value.join.call_count, 2)

    def test_run_forever_runs_the_heart_in_the_caller_and_stops(self):
        with patch("core.heartbeat.host.threading.Thread") as thread:
            def tick_and_stop():
                self.host.stop()
                return Step(WAIT)
            with patch.object(self.host, "tick", side_effect=tick_and_stop) as tick, \
                    patch.object(self.host._stop, "wait", side_effect=[False, True]):
                self.host.run_forever()
            tick.assert_called_once()
            self.assertEqual(thread.call_count, 1)
            self.assertTrue(thread.call_args.kwargs["daemon"])
            thread.return_value.join.assert_called_once()
        self.assertFalse(self.host.hosting)


class TestBeats(HostCase):
    def test_first_tick_beats_and_saves_her_situation(self):
        self.assertEqual(self.host.tick(), Step(BEAT))
        self.assertEqual(len(self.calls), 1)
        call = self.calls[0]
        self.assertEqual(call["iteration"], 0)
        self.assertIs(call["person"], self.host.person)
        self.assertIs(call["llm_json_mode"], self.llm_json_mode)
        self.assertIs(call["meta_cognitive_system"], self.host.meta_cognitive_system)
        context = call["context"]
        self.assertIs(context["event_log"], self.host.event_log)
        self.assertIs(context["simulation_history"], self.host.situation.history)
        self.assertIs(context["debug_iterations"], self.host.debug_iterations)
        self.assertIs(context["user_db"], self.user_db)
        self.assertEqual(context["sleep_config"], RhythmConfig())
        self.host.stop()
        again = self.make_host()
        self.assertTrue(again.start(threads=False))
        self.assertEqual(again.situation.beat_index, 1)
        self.assertEqual(again.situation.beats_count, 1)
        self.assertEqual(again.situation.history[-1], {
            "iteration": 1, "timestamp": NOW.isoformat(), "duration_seconds": 2.5,
            "action_decision": {"chosen_action": "Read a book"},
            "needs_state": {"overall_satisfaction": 70}, "emotions_state": {"joy": 30},
            "world_summary": {"location": {"name": "Home"}, "time": {"time_of_day": "afternoon"}},
            "satisfaction_delta": 3.0,
        })
        self.assertEqual(again.situation.last_responses, {
            "needs_response": {"overall_satisfaction": 70}, "world_description": {"weather": "clear"},
            "action_decision": {"chosen_action": "Read a book"}, "state_response": {"mood": "content"},
        })

    def test_no_second_beat_before_the_interval(self):
        self.host.tick()
        self.advance(minutes=14)
        self.assertEqual(self.host.tick(), Step(WAIT, "interval"))
        self.advance(minutes=1)
        self.assertEqual(self.host.tick(), Step(BEAT))
        self.assertEqual(len(self.calls), 2)

    def test_a_failing_beat_does_not_stop_the_loop_and_backs_off(self):
        self.fail_next(3)
        with self.assertLogs("jenbina.heartbeat", level="ERROR"):
            for _ in range(3):
                self.assertEqual(self.host.tick(), Step(BEAT))
                self.advance(minutes=15)
        self.assertTrue(self.host.hosting)
        self.assertEqual(self.host.situation.consecutive_failures, 3)
        self.assertEqual(self.host.situation.beats_count, 3)
        self.assertEqual(self.store.load_state()[1]["consecutive_failures"], 3)
        self.assertEqual(self.host.status().note, "backoff")
        self.assertEqual(self.host.tick(), Step(WAIT, "backoff"))
        self.advance(minutes=15)
        self.assertEqual(self.host.tick(), Step(BEAT))
        self.assertEqual(self.host.situation.consecutive_failures, 0)
        self.assertEqual(self.host.status().note, "")

    def test_history_and_debug_are_bounded(self):
        self.host.tick()
        self.live(hours=3, minutes=30)
        self.assertEqual(len(self.calls), 15)
        self.assertEqual(len(self.host.situation.history), 12)
        self.assertEqual(self.host.situation.history[0]["iteration"], 4)
        self.live(hours=2, minutes=30)
        self.assertEqual(len(self.calls), 25)
        self.assertEqual(len(self.host.debug_iterations), 20)
        self.assertEqual(self.host.debug_iterations[0]["iteration"], 6)

    def test_location_survives_a_restart(self):
        self.location = "Coupa Cafe"
        self.host.tick()
        self.host.stop()
        again = self.make_host()
        again.start(threads=False)
        self.assertEqual(again.situation.location, "Coupa Cafe")

    def test_status_reports_progress_without_taking_the_mind_lock(self):
        original = self.host.iteration_fn
        seen = []
        def iteration(**kwargs):
            kwargs["context"]["status"].stage("thinking…")
            seen.append(self.host.status())
            return original(**kwargs)
        self.host.iteration_fn = iteration
        self.host.tick()
        self.assertTrue(seen[0].busy)
        self.assertEqual(seen[0].stage, "thinking…")
        status = self.host.status()
        self.assertFalse(status.busy)
        self.assertEqual(status.stage, "idle")
        self.assertEqual(status.next_beat_at, NOW + timedelta(minutes=15))

    def test_unexpected_pass_error_is_logged_and_the_next_tick_can_run(self):
        with patch("core.heartbeat.host.decide", side_effect=ValueError("bad pass")):
            with self.assertLogs("jenbina.heartbeat", level="ERROR"):
                self.assertEqual(self.host.tick(), Step(WAIT, "error"))
        self.assertEqual(self.host.tick(), Step(BEAT))

    def test_daily_counter_resets_on_the_next_calendar_day(self):
        self.host.situation.beats_day = (NOW - timedelta(days=1)).date().isoformat()
        self.host.situation.beats_count = 80
        self.assertEqual(self.host.tick(), Step(BEAT))
        self.assertEqual(self.host.situation.beats_count, 1)
        self.assertEqual(self.host.situation.beats_day, "2026-11-15")


class TestSleep(HostCase):
    def test_choosing_sleep_at_night_puts_her_to_sleep_and_stops_llm_work(self):
        self.now = datetime(2026, 11, 15, 23, 40)
        self.next_result(fell_asleep=True)
        self.host.tick()
        self.assertEqual(self.host.situation.phase, ASLEEP)
        self.assertEqual(self.store.get_events()[-1]["kind"], "sleep")
        steps = self.live(hours=6)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual({step.kind for step in steps}, {WAIT, SLEEP_TICK})
        for llm in (self.llm, self.llm_json_mode, self.insight_llm):
            llm.invoke.assert_not_called()

    def test_sleep_recovers_twelve_points_an_hour_and_she_wakes_hungry(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0), sleep_need=20.0, hunger=80.0)
        self.live(hours=2)
        needs = self.host.person.maslow_needs
        self.assertAlmostEqual(needs.get_need_satisfaction("sleep"), 44.0, delta=0.5)
        self.assertAlmostEqual(needs.get_need_satisfaction("hunger"), 64.0, delta=3.5)

    def test_morning_wake_is_recorded_with_its_length_and_saved(self):
        self.put_to_sleep(datetime(2026, 11, 15, 22, 20))
        steps = self.live(until=datetime(2026, 11, 16, 6, 0))
        self.assertEqual(steps[-1], Step(WAKE, "morning"))
        self.assertNotIn(WAKE, [step.kind for step in steps[:-1]])
        self.assertEqual(self.store.get_events()[-1]["title"], "Woke after 7h 40m")
        self.assertEqual(self.host.situation.phase, AWAKE)
        self.assertEqual(self.store.load_state()[1]["phase"], AWAKE)

    def test_nine_hours_wakes_her_at_night(self):
        self.put_to_sleep(datetime(2026, 11, 15, 13, 0))
        # Every pass is at night for this deliberately unusual sleep schedule.
        with patch("core.heartbeat.rhythm.is_night", return_value=True):
            steps = self.live(hours=9)
        self.assertEqual(steps[-1], Step(WAKE, "slept_enough"))

    def test_twenty_hours_awake_forces_sleep_without_a_beat(self):
        self.host.situation.awake_since = self.now - timedelta(hours=20)
        self.assertEqual(self.host.tick(), Step(FALL_ASLEEP, "exhausted"))
        self.assertEqual(self.calls, [])
        self.assertEqual(self.store.get_events()[-1]["detail"]["reason"], "exhausted")

    def test_a_message_wakes_her_and_resleep_within_the_hour_is_the_same_sleep(self):
        start = datetime(2026, 11, 15, 23, 0)
        self.put_to_sleep(start)
        self.live(until=datetime(2026, 11, 16, 2, 10))
        with self.host.chat_turn(ANN) as turn:
            self.assertTrue(turn.woken)
        self.assertEqual(self.store.get_events()[-1]["title"], "Woken by a message after 3h 10m")
        self.assertIn("a message just woke me", self.host.person.working_memory.format_for_prompt())
        events_before = len(self.store.get_events())
        self.advance(minutes=20)
        self.next_result(fell_asleep=True)
        self.host.tick()
        self.assertEqual(self.host.situation.phase, ASLEEP)
        self.assertEqual(self.host.situation.phase_since, start)
        self.assertNotIn("sleep", [e["kind"] for e in self.store.get_events()[events_before:]])
        self.live(until=datetime(2026, 11, 16, 6, 0))
        self.assertEqual(self.store.get_events()[-1]["title"], "Woke after 7h 0m")

    def test_sleep_after_the_resleep_window_is_a_new_sleep(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0))
        with self.host.chat_turn(ANN):
            pass
        self.live(hours=1)
        self.advance(minutes=1)
        self.next_result(fell_asleep=True)
        self.host.step_once()
        self.assertEqual(self.host.situation.phase_since, self.now)
        self.assertEqual(self.event_kinds().count("sleep"), 2)

    def test_a_greeting_never_wakes_her_or_changes_state(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0))
        before = (self.host.person.serialize(), deepcopy(self.host.situation.to_dict()),
                  self.store.people(), self.store.get_events())
        with self.host.greeting_turn(ANN) as turn:
            self.assertIsNone(turn)
        self.assertEqual((self.host.person.serialize(), self.host.situation.to_dict(),
                          self.store.people(), self.store.get_events()), before)

    def test_message_wake_accounts_for_the_partial_sleep_interval(self):
        self.put_to_sleep(self.now, sleep_need=20.0)
        self.advance(minutes=10)
        with self.host.chat_turn(ANN):
            pass
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("sleep"), 22.0)
        self.assertEqual(self.host.situation.awake_since, self.now)


class TestLostTime(HostCase):
    def test_a_long_gap_is_noticed_and_costs_her_nothing(self):
        self.host.tick()
        hunger = self.host.person.maslow_needs.get_need_satisfaction("hunger")
        self.advance(hours=5)
        self.host.tick()
        gaps = [event for event in self.store.get_events() if event["kind"] == "gap"]
        self.assertEqual([event["title"] for event in gaps], ["Was away for 5h 0m"])
        self.assertEqual(gaps[0]["created_at"], self.now)
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), hunger, delta=3.0)
        self.assertIn("I was away for 5h 0m", self.host.person.working_memory.format_for_prompt())

    def test_lost_time_does_not_count_as_time_awake(self):
        self.host.tick()
        self.host.situation.awake_since = self.now - timedelta(hours=10)
        self.advance(hours=30)
        step = self.host.tick()
        self.assertNotEqual(step.kind, FALL_ASLEEP)
        self.assertEqual(self.host.situation.phase, AWAKE)
        self.assertEqual(self.host.situation.awake_since, self.now - timedelta(hours=10))

    def test_backoff_and_the_daily_cap_are_not_lost_time(self):
        self.host.situation.beats_day = self.now.date().isoformat()
        self.host.situation.beats_count = 80
        self.live(hours=5)
        self.assertEqual(len(self.calls), 0)
        self.assertNotIn("gap", self.event_kinds())
        self.host.situation.beats_count = 0
        self.fail_next(8)
        with self.assertLogs("jenbina.heartbeat", level="ERROR"):
            self.live(hours=5)
        self.assertNotIn("gap", self.event_kinds())

    def test_gap_on_restart_is_measured_from_the_last_pulse(self):
        self.host.pulse()
        self.host.stop()
        self.advance(hours=2)
        again = self.make_host()
        again.start(threads=False)
        again.tick()
        self.assertEqual(self.store.get_events()[-1]["title"], "Was away for 2h 0m")

    def test_a_pulse_before_the_first_tick_does_not_hide_a_restart_gap(self):
        self.host.stop()
        self.advance(hours=2)
        again = self.make_host()
        again.start(threads=False)
        again.pulse()
        again.tick()
        self.assertEqual(self.event_kinds().count("gap"), 1)

    def test_pulses_during_a_long_conversation_are_not_lost_time(self):
        with self.host.chat_turn(ANN):
            for _ in range(60):
                self.advance(minutes=5)
                self.assertTrue(self.host.pulse())
        self.assertEqual(self.host.tick(), Step(WAIT, "attention"))
        self.assertNotIn("gap", self.event_kinds())

    def test_a_pulse_notices_a_runtime_gap_before_the_next_tick(self):
        self.advance(hours=5)
        self.host.pulse()
        self.host.tick()
        self.host.tick()
        self.assertEqual([event["title"] for event in self.store.get_events()
                          if event["kind"] == "gap"], ["Was away for 5h 0m"])

    def test_a_message_after_downtime_absorbs_the_gap_before_waking(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0), sleep_need=20.0, hunger=80.0)
        self.advance(hours=2)
        with self.host.chat_turn(ANN) as turn:
            self.assertTrue(turn.woken)
        self.assertEqual(self.host.person.maslow_needs.get_need_satisfaction("sleep"), 20.0)
        self.assertEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), 80.0)
        self.assertEqual(self.event_kinds()[-2:], ["gap", "wake"])

    def test_a_manual_beat_after_downtime_absorbs_the_gap_before_decay(self):
        self.host.tick()
        hunger = self.host.person.maslow_needs.get_need_satisfaction("hunger")
        self.advance(hours=5)
        self.assertEqual(self.host.step_once(), "done")
        self.assertEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), hunger)
        self.assertEqual(self.event_kinds(), ["gap"])

    def test_asleep_through_a_gap_longer_than_nine_hours_wakes_her(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0), sleep_need=20.0, hunger=80.0)
        self.advance(hours=10)
        self.host.tick()
        self.assertEqual(self.host.situation.phase, AWAKE)
        self.assertEqual(self.host.situation.awake_since, self.now)
        self.assertNotIn("wake", self.event_kinds())
        self.assertEqual(self.store.get_events()[-1]["title"], "Was away for 10h 0m")
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), 80.0)

    def test_a_shorter_sleep_gap_keeps_her_asleep_without_recovery(self):
        self.put_to_sleep(datetime(2026, 11, 15, 23, 0), sleep_need=20.0, hunger=80.0)
        self.advance(hours=2)
        self.assertEqual(self.host.tick(), Step(WAIT, "asleep"))
        self.assertEqual(self.host.situation.last_sleep_tick_at, self.now)
        self.assertEqual(self.host.person.maslow_needs.get_need_satisfaction("sleep"), 20.0)
        self.assertEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), 80.0)


class TestTurnsAndStepOnce(HostCase):
    def test_chat_holds_her_attention_until_three_minutes_after_the_turn(self):
        self.host.tick()
        self.advance(minutes=20)
        with self.host.chat_turn(ANN) as turn:
            self.assertEqual((turn.person_key, turn.user_id, turn.woken), ("Ann", 1, False))
            self.advance(minutes=10)
        self.assertEqual(self.host.situation.last_chat_at, self.now)
        self.assertEqual(self.host.tick(), Step(WAIT, "attention"))
        self.advance(minutes=3)
        self.assertEqual(self.host.tick(), Step(BEAT))

    def test_chat_turn_carries_the_last_beat_and_saves_on_exception(self):
        self.host.tick()
        with self.assertRaisesRegex(ValueError, "chat failed"):
            with self.host.chat_turn(BOB) as turn:
                self.assertEqual(turn.last_responses["action_decision"], {"chosen_action": "Read a book"})
                self.assertEqual(turn.history[-1]["iteration"], 1)
                self.assertIs(turn.event_log, self.host.event_log)
                self.host.person.receive_message(turn.person_key, "saved even on failure")
                raise ValueError("chat failed")
        saved = Person.deserialize(self.store.load_state()[0])
        self.assertEqual(saved.conversations["Bob"].messages[-1].content, "saved even on failure")

    def test_greeting_turn_yields_none_while_the_mind_is_busy_and_pulse_keeps_running(self):
        acquired, release = threading.Event(), threading.Event()
        def hold_mind():
            with self.host.lock:
                acquired.set()
                release.wait(timeout=5)
        thread = threading.Thread(target=hold_mind)
        thread.start()
        try:
            self.assertTrue(acquired.wait(timeout=2))
            with self.host.greeting_turn(ANN) as turn:
                self.assertIsNone(turn)
            self.advance(minutes=1)
            self.assertTrue(self.host.pulse())
            self.assertEqual(self.store.people(), {})
        finally:
            release.set()
            thread.join(timeout=2)
        self.assertFalse(thread.is_alive())

    def test_greeting_turn_saves_without_taking_attention(self):
        with self.host.greeting_turn(ANN) as turn:
            self.assertEqual((turn.person_key, turn.user_id, turn.woken), ("Ann", 1, False))
            self.host.person.send_message(turn.person_key, "hello", "greeting")
        self.assertIsNone(self.host.situation.last_chat_at)
        saved = Person.deserialize(self.store.load_state()[0])
        self.assertEqual(saved.conversations["Ann"].messages[-1].message_type, "greeting")

    def test_step_once_ignores_interval_attention_and_backoff_but_not_cap_or_sleep(self):
        self.host.tick()
        self.host.situation.last_chat_at = self.now
        self.host.situation.consecutive_failures = 4
        self.assertEqual(self.host.step_once(), "done")
        self.assertEqual(len(self.calls), 2)
        self.host.situation.beats_count = 80
        self.assertEqual(self.host.step_once(), "daily_cap")
        self.assertEqual(self.host.status().note, "daily_cap")
        self.assertIsNone(self.host.status().next_beat_at)
        self.put_to_sleep(self.now)
        self.assertEqual(self.host.step_once(), "asleep")

    def test_step_once_reports_a_failure_and_counts_the_attempt(self):
        self.fail_next(1)
        with self.assertLogs("jenbina.heartbeat", level="ERROR"):
            self.assertEqual(self.host.step_once(), "failed")
        self.assertEqual(self.host.situation.beats_count, 1)
        self.assertEqual(self.host.status().stage, "idle")
        self.assertFalse(self.host.status().busy)

    def test_proactive_target_is_offered_to_the_beat(self):
        with self.host.chat_turn(ANN) as turn:
            self.host.person.add_conversation(turn.person_key).messages.append(
                Message(self.now, "outsider", "hello"),
            )
        self.advance(minutes=3)
        self.host.tick()
        self.assertEqual(self.calls[-1]["context"]["proactive_target"], (1, "Ann"))

    def test_person_keys_are_cached_per_account_and_names_stay_distinct(self):
        with patch.object(self.store, "person_key", wraps=self.store.person_key) as key:
            self.assertEqual(self.host.person_key(ANN), "Ann")
            self.assertEqual(self.host.person_key({"id": 1, "display_name": "Anne"}), "Ann")
            key.assert_called_once_with(1, "Ann")
        self.assertEqual(self.host.person_key({"id": 2, "display_name": "Ann"}), "Ann (2)")


class TestUnreadableState(HostCase):
    def test_corrupt_person_state_stops_the_host_and_is_not_overwritten(self):
        self.host.stop()
        self.store.save_state("{broken", {})
        host = self.make_host()
        with self.assertRaisesRegex(BeingStateError, "saved person state"):
            host.start(threads=False)
        self.assertFalse(host.hosting)
        host.stop()
        self.assertEqual(self.store.load_state()[0], "{broken")
        self.assertTrue(self.store.acquire_lease("other:1:zz", self.now, STALE).acquired)

    def test_old_situation_without_new_fields_loads_with_defaults(self):
        self.host.stop()
        self.store.save_state(Person().serialize(), {"location": "Coupa Cafe"})
        host = self.make_host()
        self.assertTrue(host.start(threads=False))
        self.assertEqual((host.situation.location, host.situation.phase), ("Coupa Cafe", AWAKE))
        self.assertEqual(host.situation.phase_since, self.now)
        self.assertEqual(host.situation.history, [])

    def test_corrupt_situation_keeps_the_existing_person_and_uses_defaults(self):
        self.host.person.name = "Existing Jenbina"
        self.host.stop()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("UPDATE being_state SET situation_json = ?", ("{broken",))
        host = self.make_host()
        self.assertTrue(host.start(threads=False))
        self.assertEqual(host.person.name, "Existing Jenbina")
        self.assertEqual(host.situation.phase, AWAKE)
        self.assertEqual(host.situation.location, "Jenbina's House")

    def test_existing_user_state_is_adopted_once_and_the_override_is_forwarded(self):
        self.host.stop()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM being_state")
        for user in (ANN, BOB):
            self.user_db.save_person_state(user["id"], Person(name=f"From {user['display_name']}").serialize())
        host = self.make_host(adopt_user_id=2)
        self.assertTrue(host.start(threads=False))
        self.assertEqual(host.person.name, "From Bob")
        self.assertEqual(host.person.maslow_needs.last_comprehensive_update, self.now)
        host.stop()
        again = self.make_host(adopt_user_id=1)
        self.assertTrue(again.start(threads=False))
        self.assertEqual(again.person.name, "From Bob")


if __name__ == "__main__":
    unittest.main()
