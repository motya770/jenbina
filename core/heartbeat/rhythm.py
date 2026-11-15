"""Pure timing rules for Jenbina's continuous life, driven by a supplied clock."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from typing import Mapping


AWAKE, ASLEEP = "awake", "asleep"
HOME = "Jenbina's House"
WAIT, BEAT, SLEEP_TICK, FALL_ASLEEP, WAKE = "wait", "beat", "sleep_tick", "fall_asleep", "wake"

_DATETIME_FIELDS = (
    "phase_since", "awake_since", "last_beat_at", "last_sleep_tick_at",
    "last_chat_at", "interrupted_sleep_started_at", "woken_by_message_at",
)


@dataclass(frozen=True)
class RhythmConfig:
    beat_interval: timedelta = timedelta(minutes=15)
    max_beats_per_day: int = 80
    attention_window: timedelta = timedelta(minutes=3)
    failures_before_backoff: int = 3
    max_backoff: timedelta = timedelta(hours=1)
    max_awake: timedelta = timedelta(hours=20)
    max_sleep: timedelta = timedelta(hours=9)
    min_sleep: timedelta = timedelta(hours=6)
    resleep_window: timedelta = timedelta(hours=1)
    sleep_recovery_per_hour: float = 12.0
    low_sleep_need: float = 30.0
    lost_time_intervals: int = 3
    sleep_enabled: bool = True
    loop_period_seconds: float = 5.0
    lease_stale_after: timedelta = timedelta(seconds=120)
    history_limit: int = 12
    debug_limit: int = 20

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> RhythmConfig:
        """Read supported overrides, retaining defaults for invalid values."""
        defaults = cls()
        interval = defaults.beat_interval
        cap = defaults.max_beats_per_day
        try:
            parsed = timedelta(minutes=float(env.get("JENBINA_BEAT_MINUTES", "")))
            if parsed > timedelta(0):
                interval = parsed
        except (ValueError, OverflowError):
            pass
        try:
            parsed_cap = int(env.get("JENBINA_MAX_BEATS_PER_DAY", ""))
            if parsed_cap > 0:
                cap = parsed_cap
        except ValueError:
            pass
        return cls(
            beat_interval=interval,
            max_beats_per_day=cap,
            sleep_enabled=env.get("JENBINA_DISABLE_SLEEP") != "1",
        )


@dataclass
class Situation:
    phase: str = AWAKE
    phase_since: datetime | None = None
    awake_since: datetime | None = None
    location: str = HOME
    last_beat_at: datetime | None = None
    last_sleep_tick_at: datetime | None = None
    beats_day: str = ""
    beats_count: int = 0
    consecutive_failures: int = 0
    last_chat_at: datetime | None = None
    beat_index: int = 0
    interrupted_sleep_started_at: datetime | None = None
    woken_by_message_at: datetime | None = None
    history: list = field(default_factory=list)
    last_responses: dict = field(default_factory=dict)

    @classmethod
    def fresh(cls, now: datetime) -> Situation:
        return cls(phase_since=now, awake_since=now)

    def to_dict(self) -> dict:
        data = asdict(self)
        for name in _DATETIME_FIELDS:
            value = getattr(self, name)
            data[name] = value.isoformat() if value is not None else None
        return data

    @classmethod
    def from_dict(cls, data: dict, now: datetime) -> Situation:
        """Restore valid fields independently; old or malformed fields default."""
        situation = cls.fresh(now)
        if not isinstance(data, dict):
            data = {}
        for name in _DATETIME_FIELDS:
            try:
                value = datetime.fromisoformat(data.get(name))
            except (TypeError, ValueError):
                continue
            setattr(situation, name, value)
        if data.get("phase") in (AWAKE, ASLEEP):
            situation.phase = data["phase"]
        if isinstance(data.get("location"), str):
            situation.location = data["location"]
        try:
            situation.beats_day = date.fromisoformat(data.get("beats_day")).isoformat()
        except (TypeError, ValueError):
            pass
        for name in ("beats_count", "consecutive_failures", "beat_index"):
            value = data.get(name)
            if type(value) is int and value >= 0:
                setattr(situation, name, value)
        if isinstance(data.get("history"), list):
            situation.history = data["history"]
        if isinstance(data.get("last_responses"), dict):
            situation.last_responses = data["last_responses"]
        return situation


@dataclass(frozen=True)
class Step:
    kind: str
    reason: str = ""


def _elapsed(now: datetime, then: datetime | None) -> timedelta:
    return max(timedelta(0), now - then) if then is not None else timedelta(0)


def is_night(now: datetime) -> bool:
    return now.hour >= 21 or now.hour < 6


def beats_today(s: Situation, now: datetime) -> int:
    return s.beats_count if s.beats_day == now.date().isoformat() else 0


def effective_interval(cfg: RhythmConfig, failures: int) -> timedelta:
    if failures < cfg.failures_before_backoff:
        return cfg.beat_interval
    interval = cfg.beat_interval
    for _ in range(failures - cfg.failures_before_backoff + 1):
        # Stop at the cap before doubling can overflow on a long failure streak.
        if interval >= cfg.max_backoff / 2:
            return max(cfg.beat_interval, cfg.max_backoff)
        interval *= 2
    return interval


def next_beat_at(s: Situation, now: datetime, cfg: RhythmConfig) -> datetime | None:
    """Earliest due time, including attention postponement and failure back-off."""
    if s.phase == ASLEEP or beats_today(s, now) >= cfg.max_beats_per_day:
        return None
    due = now
    if s.last_beat_at is not None:
        due = max(due, s.last_beat_at + effective_interval(cfg, s.consecutive_failures))
    if s.last_chat_at is not None:
        due = max(due, s.last_chat_at + cfg.attention_window)
    return due


def decide(s: Situation, now: datetime, cfg: RhythmConfig) -> Step:
    """Choose one action without mutating the situation or consulting the clock."""
    if s.phase == ASLEEP:
        slept = _elapsed(now, s.phase_since)
        if slept >= cfg.max_sleep:
            return Step(WAKE, "slept_enough")
        if not is_night(now) and slept >= cfg.min_sleep:
            return Step(WAKE, "morning")
        if _elapsed(now, s.last_sleep_tick_at or s.phase_since) >= cfg.beat_interval:
            return Step(SLEEP_TICK)
        return Step(WAIT, "asleep")

    if s.last_chat_at is not None and _elapsed(now, s.last_chat_at) < cfg.attention_window:
        return Step(WAIT, "attention")
    if cfg.sleep_enabled and _elapsed(now, s.awake_since) >= cfg.max_awake:
        return Step(FALL_ASLEEP, "exhausted")
    if beats_today(s, now) >= cfg.max_beats_per_day:
        return Step(WAIT, "daily_cap")
    if s.last_beat_at is None or _elapsed(now, s.last_beat_at) >= effective_interval(cfg, s.consecutive_failures):
        return Step(BEAT)
    return Step(WAIT, "backoff" if s.consecutive_failures >= cfg.failures_before_backoff else "interval")


def should_fall_asleep(
    action_key: str | None, time_of_day: str, sleep_need: float, cfg: RhythmConfig,
) -> bool:
    return (
        cfg.sleep_enabled
        and action_key == "sleep"
        and (time_of_day == "night" or sleep_need < cfg.low_sleep_need)
    )


def lost_time(previous_alive_at: datetime | None, now: datetime, cfg: RhythmConfig) -> timedelta | None:
    if previous_alive_at is None:
        return None
    gap = _elapsed(now, previous_alive_at)
    return gap if gap > cfg.lost_time_intervals * cfg.beat_interval else None
