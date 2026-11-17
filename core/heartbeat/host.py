"""Own the single live mind, its process lease, and its continuous rhythm."""

from __future__ import annotations

import atexit
import logging
import sys
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Iterator

from core.cognition.meta_cognition import MetaCognitiveSystem
from core.heartbeat.adoption import adopt_existing
from core.heartbeat.being import build_person
from core.heartbeat.outreach import choose_outreach_target
from core.heartbeat.rhythm import (
    ASLEEP, AWAKE, BEAT, FALL_ASLEEP, SLEEP_TICK, WAIT, WAKE,
    RhythmConfig, Situation, Step, beats_today, decide, lost_time, next_beat_at,
)
from core.heartbeat.store import BeingStore, make_owner_id
from core.person.person import Person
from core.simulation_runner import run_single_iteration_headless
from core.timeline import LifeEventLog, format_duration, make_gap, make_sleep, make_wake


logger = logging.getLogger("jenbina.heartbeat")

# How long interpreter exit waits for the mind lock before abandoning a beat.
EXIT_PATIENCE_SECONDS = 3.0


class NotHostingError(RuntimeError):
    """She is not (or no longer) living in this process."""


_PROCESS_HOST = "_jenbina_process_host"


def process_host(build: Callable[[], "JenbinaHost"]) -> "JenbinaHost":
    """The one host of this process, built on first use.

    Kept on ``sys`` rather than in a module global or a Streamlit cache: both
    of those are dropped by a hot reload or a cache clear while the first
    host's threads keep running and holding the lease, which would leave the
    replacement host locked out of its own process.
    """
    lock = sys.__dict__.setdefault(_PROCESS_HOST + "_lock", threading.Lock())
    with lock:
        host = sys.__dict__.get(_PROCESS_HOST)
        if host is None:
            host = build()
            sys.__dict__[_PROCESS_HOST] = host
        return host


@dataclass
class ChatTurn:
    person_key: str
    user_id: int
    woken: bool
    last_responses: dict
    history: list
    event_log: LifeEventLog


@dataclass
class HeartStatus:
    hosting: bool
    holder: str | None
    phase: str
    phase_since: datetime
    last_beat_at: datetime | None
    next_beat_at: datetime | None
    note: str
    busy: bool
    stage: str


class _StatusSink:
    def __init__(self, host):
        self.host = host

    def stage(self, text: str) -> None:
        self.host._stage = text


class JenbinaHost:
    def __init__(
        self, store: BeingStore, user_db, llm, llm_json_mode, insight_llm, *,
        clock: Callable[[], datetime] = datetime.now,
        iteration_fn: Callable = run_single_iteration_headless,
        meta_cognitive_system=None, config: RhythmConfig | None = None,
        owner: str | None = None, adopt_user_id: int | None = None,
        world_provider=None,
    ):
        self.store = store
        self.user_db = user_db
        self.llm = llm
        self.llm_json_mode = llm_json_mode
        self.insight_llm = insight_llm
        self.clock = clock
        self.iteration_fn = iteration_fn
        self.meta_cognitive_system: Any = (
            MetaCognitiveSystem(llm_json_mode)
            if meta_cognitive_system is None else meta_cognitive_system
        )
        self.config = config if config is not None else RhythmConfig.from_env()
        self.owner = owner if owner is not None else make_owner_id()
        self.adopt_user_id = adopt_user_id
        # A real world she lives in (see core/environment/minecraft); None
        # keeps the described Palo Alto world.
        self.world_provider = world_provider
        self.person: Person
        self.situation = Situation.fresh(clock())
        self.event_log = LifeEventLog(store)
        self.lock = threading.RLock()
        self.hosting = False
        self.debug_iterations = []
        self._holder = None
        self._busy = False
        self._stage = "idle"
        self._people = {}
        self._stop = threading.Event()
        self._threads = []
        self._start_lock = threading.Lock()
        self._atexit_registered = False
        # The pulse must renew even while a beat or chat owns the mind lock.
        self._alive_lock = threading.Lock()
        self._last_alive = None
        self._pending_gap = None

    def start(self, threads: bool = True) -> bool:
        # One caller at a time: a second caller that read hosting == False just
        # before the first finished would otherwise stop the threads it started.
        with self._start_lock:
            return self._start(threads)

    def _start(self, threads: bool) -> bool:
        if not self.hosting:
            self._stop.set()
            self._join_threads()
        with self.lock:
            if self.hosting:
                return True
            now = self.clock()
            lease = self.store.acquire_lease(self.owner, now, self.config.lease_stale_after)
            if not lease.acquired:
                self._holder = lease.holder
                return False
            try:
                saved = self.store.load_state()
                if saved is None:
                    person, situation, _ = adopt_existing(
                        self.store, self.user_db, self.llm, self.llm_json_mode,
                        self.insight_llm, now, prefer_user_id=self.adopt_user_id,
                    )
                    # The copy she is adopted from may have been idle for days:
                    # her body was suspended for that time, like any lost time.
                    person.suspend_until(now)
                else:
                    person = build_person(saved[0], self.llm, self.llm_json_mode, self.insight_llm)
                    situation = Situation.from_dict(saved[1], now)
            except Exception:
                # A failed restore must never reach save(), including via stop().
                self.store.release_lease(self.owner)
                raise
            self.person = person
            self.situation = situation
            self.debug_iterations = []
            self._people = {}
            self._holder = None
            self._last_alive = lease.previous_renewed_at or now
            self._pending_gap = None
            self._stop = threading.Event()
            self.hosting = True
            if threads:
                self._register_stop()
                self._start_thread(self._heart_loop, "jenbina-heart")
                self._start_thread(self._pulse_loop, "jenbina-pulse")
            return True

    def _register_stop(self) -> None:
        if not self._atexit_registered:
            atexit.register(self.stop, EXIT_PATIENCE_SECONDS)
            self._atexit_registered = True

    def _start_thread(self, target, name: str) -> None:
        thread = threading.Thread(target=target, name=name, daemon=True)
        self._threads.append(thread)
        thread.start()

    def _join_threads(self, timeout: float | None = None) -> None:
        for thread in self._threads:
            if thread is not threading.current_thread():
                thread.join(timeout)
        self._threads = []

    def stop(self, patience: float | None = None) -> None:
        """Stop the heart, save her and release the lease.

        With ``patience`` (seconds) it does not wait for a beat in flight: that
        beat's unsaved work is abandoned and the lease is still released, so
        quitting the process never hangs behind a minute of LLM calls.
        """
        self._stop.set()
        # Never join a heart thread while holding the lock it may be waiting for.
        self._join_threads(patience)
        if not self.lock.acquire(timeout=-1 if patience is None else patience):
            if self.hosting:
                # hosting = False first, so the beat in flight cannot save.
                self.hosting = False
                try:
                    self.store.renew_lease(self.owner, self.clock())
                finally:
                    self.store.release_lease(self.owner)
            return
        try:
            if not self.hosting:
                return
            try:
                self.save()
                if self.hosting:
                    self.store.renew_lease(self.owner, self.clock())
            finally:
                self.store.release_lease(self.owner)
                self.hosting = False
        finally:
            self.lock.release()

    def run_forever(self) -> None:
        if not self.hosting:
            return
        self._register_stop()
        self._start_thread(self._pulse_loop, "jenbina-pulse")
        try:
            self._heart_loop()
        finally:
            self.stop()

    def _heart_loop(self) -> None:
        while not self._stop.wait(self.config.loop_period_seconds):
            self.tick()

    def _pulse_loop(self) -> None:
        while not self._stop.wait(self.config.loop_period_seconds):
            self.pulse()

    def _lost_lease(self) -> None:
        self.hosting = False
        self._stop.set()
        logger.error("Jenbina's host lost its process lease (%s).", self.owner)

    def pulse(self) -> bool:
        if not self.hosting:
            return False
        now = self.clock()
        try:
            renewed = self.store.renew_lease(self.owner, now)
        except Exception:
            # A storage hiccup is not proof that another process owns her. Saves
            # are fenced by the lease, so keep hosting and let the next pulse retry.
            logger.exception("Could not renew Jenbina's process lease; will retry.")
            return True
        if renewed:
            self._mark_alive(now)
            return True
        self._lost_lease()
        return False

    def _mark_alive(self, now: datetime) -> None:
        with self._alive_lock:
            gap = lost_time(self._last_alive, now, self.config)
            if gap is not None:
                self._pending_gap = (self._pending_gap or timedelta(0)) + gap
            self._last_alive = now

    def _check_lost_time(self, now: datetime) -> None:
        self._mark_alive(now)
        with self._alive_lock:
            gap, self._pending_gap = self._pending_gap, None
        if gap is not None:
            self._absorb_gap(gap, now)

    def tick(self) -> Step:
        try:
            with self.lock:
                if not self.hosting or not self.pulse():
                    return Step(WAIT, "not_hosting")
                now = self.clock()
                try:
                    self._check_lost_time(now)
                    step = decide(self.situation, now, self.config)
                    if step.kind == BEAT:
                        self._beat(now)
                    elif step.kind == SLEEP_TICK:
                        self._sleep_tick(now)
                    elif step.kind == FALL_ASLEEP:
                        self._fall_asleep(now, step.reason)
                    elif step.kind == WAKE:
                        self._wake(now, step.reason)
                    return step
                finally:
                    with self._alive_lock:
                        self._last_alive = self.clock()
        except Exception:
            logger.exception("Jenbina's heart pass failed; the next pass will retry.")
            return Step(WAIT, "error")

    def _beat(self, now: datetime) -> bool:
        s = self.situation
        s.last_beat_at = now
        today = now.date().isoformat()
        if s.beats_day != today:
            s.beats_day, s.beats_count = today, 0
        s.beats_count += 1
        self._busy = True
        succeeded = False
        try:
            context = {
                "simulation_history": s.history, "jenbina_location": s.location,
                "debug_iterations": self.debug_iterations, "user_db": self.user_db,
                "event_log": self.event_log, "status": _StatusSink(self),
                "sleep_config": self.config,
                "world_provider": self.world_provider, "world_memory": s.world,
                "proactive_target": choose_outreach_target(self.person, self.store.people(), now),
            }
            result = self.iteration_fn(
                person=self.person, llm_json_mode=self.llm_json_mode,
                meta_cognitive_system=self.meta_cognitive_system,
                iteration=s.beat_index, context=context,
            )
            finished_at = self.clock()
            record = {
                "iteration": s.beat_index + 1, "timestamp": finished_at.isoformat(),
                "duration_seconds": result["iteration_duration"],
                "action_decision": result["action_decision"],
                "needs_state": result["person_dict"]["maslow_needs"],
                "emotions_state": result["person_dict"].get("emotions", {}),
                "world_summary": result["world_summary"],
                "satisfaction_delta": result["satisfaction_delta"],
            }
            s.consecutive_failures = 0
            s.beat_index += 1
            s.history.append(record)
            del s.history[:-self.config.history_limit]
            s.last_responses = {
                "needs_response": record["needs_state"],
                "world_description": result["world_description"],
                "action_decision": result["action_decision"],
                "state_response": result["state_response"],
            }
            s.location = context["jenbina_location"]
            if result.get("fell_asleep"):
                self._fall_asleep(finished_at, "chose")
            succeeded = True
        except Exception:
            s.consecutive_failures += 1
            logger.exception("Jenbina's beat failed (%s consecutive failures).", s.consecutive_failures)
        finally:
            del self.debug_iterations[:-self.config.debug_limit]
            self._busy, self._stage = False, "idle"
            self.save()
        return succeeded

    def _record(self, event, now: datetime) -> None:
        event.created_at = now
        self.event_log.record(event)

    def _fall_asleep(self, now: datetime, reason: str) -> None:
        s = self.situation
        same_sleep = (
            s.woken_by_message_at is not None
            and max(timedelta(0), now - s.woken_by_message_at) <= self.config.resleep_window
            and s.interrupted_sleep_started_at is not None
        )
        if same_sleep:
            s.phase_since = s.interrupted_sleep_started_at
        else:
            s.phase_since = now
            self._record(make_sleep(reason), now)
        s.phase = ASLEEP
        s.last_sleep_tick_at = now
        s.interrupted_sleep_started_at = s.woken_by_message_at = None
        self.save()

    def _sleep_tick(self, now: datetime) -> None:
        s = self.situation
        since = s.last_sleep_tick_at or s.phase_since
        hours = max(0.0, (now - since).total_seconds() / 3600)
        self.person.maslow_needs.satisfy_need(
            "sleep", self.config.sleep_recovery_per_hour * hours, source="sleeping",
        )
        self.person.update_all_needs(now=now, skip_needs=("sleep",))
        s.last_sleep_tick_at = now
        self.save()

    def _wake(self, now: datetime, reason: str) -> None:
        s = self.situation
        self._sleep_tick(now)
        self._record(make_wake(max(timedelta(0), now - s.phase_since), reason), now)
        if reason == "message":
            s.interrupted_sleep_started_at = s.phase_since
            s.woken_by_message_at = now
            self.person.working_memory.add_note("I was asleep and a message just woke me.", cycles=2)
        s.phase = AWAKE
        s.phase_since = s.awake_since = now
        self.save()

    def _absorb_gap(self, gap: timedelta, now: datetime) -> None:
        self.person.suspend_until(now)
        s = self.situation
        if s.phase == ASLEEP:
            if gap > self.config.max_sleep:
                s.phase = AWAKE
                s.phase_since = s.awake_since = now
            else:
                s.last_sleep_tick_at = now
        elif s.awake_since is not None:
            # She was not awake through the gap, so it must not count toward
            # the hours-awake limit and send her to bed the moment she returns.
            s.awake_since = min(now, s.awake_since + gap)
        self._record(make_gap(gap), now)
        self.person.working_memory.add_note(
            f"I was away for {format_duration(gap)}. That time passed without me.", cycles=3,
        )
        self.save()

    def _turn(self, user: dict, woken: bool = False) -> ChatTurn:
        return ChatTurn(self.person_key(user), user["id"], woken,
                        self.situation.last_responses, self.situation.history, self.event_log)

    @contextmanager
    def chat_turn(self, user: dict) -> Iterator[ChatTurn]:
        with self.lock:
            if not self.hosting or not self.pulse():
                raise NotHostingError("Jenbina is not living in this process.")
            now = self.clock()
            self._check_lost_time(now)
            woken = self.situation.phase == ASLEEP
            if woken:
                self._wake(now, "message")
            self.situation.last_chat_at = now
            try:
                yield self._turn(user, woken)
            finally:
                self.situation.last_chat_at = self.clock()
                self.save()

    @contextmanager
    def greeting_turn(self, user: dict) -> Iterator[ChatTurn | None]:
        if not self.lock.acquire(blocking=False):
            yield None
            return
        try:
            if not self.hosting or self.situation.phase == ASLEEP:
                yield None
                return
            if not self.pulse():
                yield None
                return
            self._check_lost_time(self.clock())
            try:
                yield self._turn(user)
            finally:
                self.save()
        finally:
            self.lock.release()

    def step_once(self) -> str:
        with self.lock:
            if not self.hosting or not self.pulse():
                return "not_hosting"
            if self.situation.phase == ASLEEP:
                return "asleep"
            now = self.clock()
            if beats_today(self.situation, now) >= self.config.max_beats_per_day:
                return "daily_cap"
            self._check_lost_time(now)
            return "done" if self._beat(now) else "failed"

    def person_key(self, user: dict) -> str:
        user_id = user["id"]
        if user_id not in self._people:
            self._people[user_id] = self.store.person_key(user_id, user.get("display_name"))
        return self._people[user_id]

    def save(self) -> None:
        with self.lock:
            if self.hosting and not self.store.save_state(
                self.person.serialize(), self.situation.to_dict(), owner=self.owner,
            ):
                self._lost_lease()

    def status(self) -> HeartStatus:
        now, s = self.clock(), self.situation
        note = ""
        if beats_today(s, now) >= self.config.max_beats_per_day:
            note = "daily_cap"
        elif s.consecutive_failures >= self.config.failures_before_backoff:
            note = "backoff"
        return HeartStatus(
            self.hosting, self._holder, s.phase, s.phase_since, s.last_beat_at,
            next_beat_at(s, now, self.config), note, self._busy, self._stage,
        )
