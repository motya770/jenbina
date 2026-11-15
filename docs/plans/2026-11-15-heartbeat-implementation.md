# Heartbeat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One Jenbina, owned by one process, who lives on her own clock (a beat every 15 minutes, sleep at night, honest about lost time) and is the same being for every account.

**Architecture:** A new Streamlit-free package `core/heartbeat/` holds a `JenbinaHost` that owns the single live `Person`, a re-entrant mind lock, and two threads (heart and pulse). A pure rhythm function decides beat / sleep tick / wake / wait from an injectable clock. Her state moves from per-user rows to one being record guarded by a database lease. The Streamlit app obtains the host through `st.cache_resource`; `run_heartbeat.py` hosts her with no UI.

**Tech Stack:** Python 3.10+, Streamlit 1.38 (`st.cache_resource`, `st.fragment(run_every=...)`), SQLite (`sqlite3`), LangChain / `langchain_openai.ChatOpenAI`, `threading`, `unittest` run by pytest.

**Spec:** `docs/plans/2026-11-15-heartbeat-design.md`. Read it before any task; this plan argues from it and does not repeat its reasoning.

## Global Constraints

- Run Python as `PY=/Users/wizard/Desktop/programming/projects/jenbina/.venv/bin/python` (the worktree has no venv). Full suite: `$PY -m pytest tests/test_*.py -q`. It must pass at the end of every task. Baseline before Task 1: 836 passed, 1 skipped, and 1 failure that predates this work and is not part of it (`tests/test_pixel_ui.py::TestWideShell::test_wide_flag_widens_device`); leave that test alone and introduce no other failure.
- Nothing under `core/heartbeat/` may import `streamlit`. `core/heartbeat/__init__.py` contains a docstring only (no imports): `core/simulation_runner.py` imports `core.heartbeat.rhythm`, and `core/heartbeat/host.py` imports the runner, so an eager package import would be circular. Callers import submodules explicitly (`from core.heartbeat.host import JenbinaHost`).
- No test may call an LLM, open a network connection, start a thread that outlives the test, or call `time.sleep`. Clocks are injected (`clock=lambda: now`). Databases are temporary files (`tempfile.TemporaryDirectory`).
- Tests use `unittest.TestCase`, live in `tests/test_*.py`, and mock every LLM.
- Spec values, verbatim: beat interval 15 min (`JENBINA_BEAT_MINUTES`); daily cap 80 (`JENBINA_MAX_BEATS_PER_DAY`); attention window 3 min; back-off after 3 consecutive failures, doubling up to 1 hour; asleep when a sleep-mapped action is chosen at night (`time_of_day == "night"`, 21:00 to 06:00) or with the sleep need below 30; forced asleep after 20 hours awake; sleep need recovers 12 points per hour; wakes after 9 hours, or when it is not night and she has slept 6 hours, or on a message; re-sleep within 1 hour of a message wake is the same sleep; lost time is more than 3 beat intervals since the previous loop pass; proactive message to at most one person, messaged within the last 7 days, closest, not proactively messaged in the last 6 hours; subtle insights 3 per person per calendar day.
- Values this plan fixes (the spec left them to the builder): loop period 5 s; lease stale after 120 s; LLM timeout 60 s (`JENBINA_LLM_TIMEOUT_SECONDS`) with `max_retries=1`; history kept 12 iteration records; debug iterations kept 20; UI refresh every 5 s.
- The existing `user_state` and `events` tables and their rows are never modified or deleted.
- She keeps the host machine's clock. No time zones.
- Commit after each task with a conventional commit message. Never commit `.env` or anything under `jenbina_memory/`.
- After the last task run `graphify update .`.

## Review Focus

Failure modes the spec implies but does not spell out. Each has a test in the task named.

1. **The previous process died without releasing its lease** (Streamlit restart, crash). A new process on the same machine must take over at once when the holder's pid is no longer running, not wait 120 s behind "living in another process". Task 1.
2. **The clock moves backwards** (DST, NTP correction): `now` earlier than `last_beat_at`. The rhythm must neither crash nor fire a burst of beats; a negative elapsed time counts as zero. Task 2.
3. **A person changes their display name, or has none.** Their key is fixed per user id at first sight, so their history is never split or handed to someone else. Task 1.
4. **The being record cannot be read** (corrupt JSON, a field from an older version missing). Missing situation fields take defaults; an unreadable person state stops the host with a clear error and never causes a fresh Jenbina to be saved over her. Task 6.
5. **A page refreshes while a beat is changing her.** The refreshing fragments read the live `Person` without the mind lock; an exception during such a read must not put a traceback on the page. Task 9.

## File Structure

| File | Responsibility |
|------|----------------|
| `core/heartbeat/__init__.py` | Docstring only. |
| `core/heartbeat/rhythm.py` | Pure: `RhythmConfig`, `Situation`, `Step`, `decide`, sleep and lost-time rules. No I/O. |
| `core/heartbeat/store.py` | `BeingStore`: the being record, life events, lease, and the user-id to person-key registry, in the same SQLite file as `UserDatabase`. |
| `core/heartbeat/being.py` | `build_person`: deserialize or create her and initialise every subsystem. |
| `core/heartbeat/adoption.py` | One-time move of an existing per-user Jenbina into the being record. |
| `core/heartbeat/outreach.py` | `choose_outreach_target`: who, if anyone, she may message on her own. |
| `core/heartbeat/host.py` | `JenbinaHost`: the owner. Lock, lease, tick, beat, sleep, wake, lost time, chat and greeting turns, status. |
| `run_heartbeat.py` | Standalone host with no UI. Replaces `run_scheduler.py`. |
| `core/ui/admin.py` | `is_admin()`, shared by the Admin page and the heartbeat card. |
| `core/ui/live.py` | `draw_guarded`: draw a fragment body without ever showing a traceback. |

---

### Task 1: Storage for the being

**Files:**
- Create: `core/heartbeat/__init__.py`, `core/heartbeat/store.py`
- Modify: `core/timeline/events.py`, `core/timeline/__init__.py`, `core/ui/pixel_theme.py` (`EVENT_TAGS`), `core/ui/timeline.py` (`HER_DAY_KINDS`)
- Test: `tests/test_heartbeat_store.py`, `tests/test_timeline.py`

**Interfaces:**
- Produces, in `core/heartbeat/store.py`:

```python
@dataclass
class Lease:
    acquired: bool
    holder: str                               # owner id now holding the lease
    previous_renewed_at: datetime | None      # renewal time found before this call, None if there was no lease

def make_owner_id() -> str                    # f"{socket.gethostname()}:{os.getpid()}:{uuid4().hex[:8]}"
def owner_is_dead(owner: str) -> bool         # True only when the hostname matches this machine and that pid is not running

class BeingStore:
    def __init__(self, db_path: str | None = None)        # default: UserDatabase().db_path
    def load_state(self) -> tuple[str, dict] | None       # (person_state_json, situation dict)
    def save_state(self, person_state_json: str, situation: dict, owner: str | None = None) -> bool
    # with `owner`: written only while that owner holds the lease (same transaction); False when it does not
    def store_event(self, kind: str, title: str, detail: dict | None = None, created_at: datetime | None = None) -> int
    def get_events(self, limit: int = 200) -> list[dict]  # same row shape and order as UserDatabase.get_events
    def import_events(self, rows: list[dict]) -> int      # rows as returned by UserDatabase.get_events; keeps created_at
    def acquire_lease(self, owner: str, now: datetime, stale_after: timedelta) -> Lease
    def renew_lease(self, owner: str, now: datetime) -> bool   # False when another owner holds it
    def release_lease(self, owner: str) -> None
    def person_key(self, user_id: int, display_name: str | None) -> str
    def people(self) -> dict[int, str]                    # user_id -> person_key
```

- Produces, in `core/timeline/events.py` (exported from `core/timeline/__init__.py`): `SLEEP = "sleep"`, `WAKE = "wake"`, `GAP = "gap"` (added to `KINDS`); `format_duration(td: timedelta) -> str`; `make_sleep(reason: str) -> TimelineEvent`; `make_wake(slept: timedelta, reason: str) -> TimelineEvent`; `make_gap(gone: timedelta) -> TimelineEvent`; `class LifeEventLog(EventLog)` with `__init__(self, store)`, `persistent` always True, `record` and `recent` backed by `store.store_event` / `store.get_events`, never raising (same guarantee as `EventLog`).

Tables, created by `BeingStore.__init__` with `CREATE TABLE IF NOT EXISTS`:

```sql
being_state (id INTEGER PRIMARY KEY CHECK (id = 1), person_state_json TEXT NOT NULL, situation_json TEXT NOT NULL, updated_at TEXT NOT NULL)
being_events(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, title TEXT NOT NULL, detail_json TEXT, created_at TEXT NOT NULL)  -- index on created_at
being_lease (id INTEGER PRIMARY KEY CHECK (id = 1), owner TEXT NOT NULL, renewed_at TEXT NOT NULL)
being_people(user_id INTEGER PRIMARY KEY, person_key TEXT UNIQUE NOT NULL)
```

Lease rule (`acquire_lease`, inside one `BEGIN IMMEDIATE` transaction): no row, or the row's owner is empty or is `owner`, or `now - renewed_at > stale_after`, or `owner_is_dead(row.owner)` → write `(owner, now)` and return `acquired=True`. Otherwise `acquired=False, holder=row.owner`. `previous_renewed_at` is the row's value before the write in every case. `release_lease` keeps the row and its `renewed_at` and sets the owner to `""`, so the next host still learns when the heart was last alive.

Person key rule (`person_key`, revised by Task 4b): a row for `user_id` wins and is returned unchanged whatever name is passed; that lookup is a plain read with no write lock. Otherwise `base` is the stripped display name, else `f"User {user_id}"`. Use `base` if no other user holds it; else `f"{base} ({n})"` with the smallest `n >= 2` that is free. Nothing derived from an email address ever goes into a key, because keys are the names that cross between people's prompts.

Titles: `make_sleep` → `"Fell asleep"`; `make_wake(slept, reason)` → `"Woken by a message after 3h 10m"` when `reason == "message"`, otherwise `"Woke after 7h 40m"`; `make_gap` → `"Was away for 3h 10m"`. `format_duration` gives `"7h 40m"`, `"40m"` under an hour, `"0m"` for zero or negative. Detail dicts carry `reason` and `seconds`. `EVENT_TAGS` gains `"sleep": "SLEEP"`, `"wake": "WAKE"`, `"gap": "GAP"`; `HER_DAY_KINDS` gains the three kinds.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_heartbeat_store.py
T0 = datetime(2026, 11, 15, 12, 0, 0)
STALE = timedelta(seconds=120)

class TestLease(unittest.TestCase):          # setUp: self.store = BeingStore(os.path.join(tmpdir, "users.db"))
    def test_first_owner_acquires_and_second_is_refused(self):
        self.assertTrue(self.store.acquire_lease("hostA:1:aa", T0, STALE).acquired)
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            second = self.store.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=30), STALE)
        self.assertFalse(second.acquired)
        self.assertEqual(second.holder, "hostA:1:aa")
        self.assertEqual(second.previous_renewed_at, T0)

    def test_stale_lease_is_taken_over(self):
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            taken = self.store.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=121), STALE)
        self.assertTrue(taken.acquired)
        self.assertFalse(self.store.renew_lease("hostA:1:aa", T0 + timedelta(seconds=122)))

    def test_dead_holder_on_this_machine_is_taken_over_at_once(self):   # Review Focus 1
        dead = f"{socket.gethostname()}:999999999:aa"
        self.store.acquire_lease(dead, T0, STALE)
        self.assertTrue(owner_is_dead(dead))
        self.assertFalse(owner_is_dead(f"{socket.gethostname()}:{os.getpid()}:bb"))
        self.assertFalse(owner_is_dead("some-other-host:999999999:cc"))
        self.assertTrue(self.store.acquire_lease(make_owner_id(), T0 + timedelta(seconds=1), STALE).acquired)

    def test_release_lets_the_next_owner_in(self): ...   # release, then another owner acquires with previous_renewed_at == T0

class TestStateAndEvents(unittest.TestCase):
    def test_state_round_trip_and_none_when_empty(self):
        self.assertIsNone(self.store.load_state())
        self.store.save_state('{"name": "Jenbina"}', {"phase": "asleep"})
        self.store.save_state('{"name": "Jenbina"}', {"phase": "awake"})        # upsert, one row
        self.assertEqual(self.store.load_state(), ('{"name": "Jenbina"}', {"phase": "awake"}))

    def test_events_come_back_oldest_first_with_parsed_detail(self): ...
    def test_life_event_log_records_and_reads(self):
        log = LifeEventLog(self.store)
        log.record(make_wake(timedelta(hours=7, minutes=40), "morning"))
        self.assertEqual(log.recent(10)[0].title, "Woke after 7h 40m")
        self.assertEqual(log.recent(10)[0].kind, "wake")

class TestPeople(unittest.TestCase):
    def test_key_is_fixed_per_user_whatever_the_name_becomes(self):       # Review Focus 3
        self.assertEqual(self.store.person_key(1, "Alex"), "Alex")
        self.assertEqual(self.store.person_key(1, "Alexander"), "Alex")
        self.assertEqual(self.store.person_key(1, None), "Alex")

    def test_same_display_name_gets_a_distinct_key(self):
        self.store.person_key(1, "Alex")
        self.assertEqual(self.store.person_key(2, "Alex"), "Alex (2)")
        self.assertEqual(self.store.person_key(3, "Alex"), "Alex (3)")
        self.assertEqual(self.store.people(), {1: "Alex", 2: "Alex (2)", 3: "Alex (3)"})

    def test_missing_name_falls_back_to_the_user_id(self):
        self.assertEqual(self.store.person_key(4, "  "), "User 4")
        self.assertEqual(self.store.person_key(5, None), "User 5")
```

Add to `tests/test_timeline.py`: `format_duration(timedelta(minutes=40)) == "40m"`, `format_duration(timedelta(seconds=-5)) == "0m"`, `make_wake(timedelta(hours=3, minutes=10), "message").title == "Woken by a message after 3h 10m"`, `make_gap(timedelta(hours=3, minutes=10)).title == "Was away for 3h 10m"`, and `{"sleep", "wake", "gap"} <= set(KINDS)`.

- [ ] **Step 2: Run** `$PY -m pytest tests/test_heartbeat_store.py tests/test_timeline.py -q`. Expected: FAIL (`No module named 'core.heartbeat'`).
- [ ] **Step 3: Implement** the store, the event kinds, builders and `LifeEventLog`, the tags and the day-filter kinds as specified above. `owner_is_dead` uses `os.kill(pid, 0)` and treats `PermissionError` as alive.
- [ ] **Step 4: Run** the same command, then the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add storage for the single being (state, life events, lease, people)`.

---

### Task 2: The rhythm

**Files:**
- Create: `core/heartbeat/rhythm.py`
- Test: `tests/test_heartbeat_rhythm.py`

**Interfaces:**
- Produces:

```python
AWAKE, ASLEEP = "awake", "asleep"
HOME = "Jenbina's House"
WAIT, BEAT, SLEEP_TICK, FALL_ASLEEP, WAKE = "wait", "beat", "sleep_tick", "fall_asleep", "wake"

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
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "RhythmConfig"
    # JENBINA_BEAT_MINUTES (float minutes), JENBINA_MAX_BEATS_PER_DAY (int), JENBINA_DISABLE_SLEEP ("1" -> sleep_enabled False).
    # A value that does not parse or is <= 0 is ignored and the default is used.

@dataclass
class Situation:
    phase: str = AWAKE
    phase_since: datetime = None            # when the current phase began (for asleep: the sleep's start)
    awake_since: datetime = None            # when she last woke
    location: str = HOME
    last_beat_at: datetime | None = None    # the last beat attempt, successful or not
    last_sleep_tick_at: datetime | None = None
    beats_day: str = ""                     # ISO date beats_count belongs to
    beats_count: int = 0
    consecutive_failures: int = 0
    last_chat_at: datetime | None = None
    beat_index: int = 0                     # total beats ever; the runner's `iteration`
    interrupted_sleep_started_at: datetime | None = None
    woken_by_message_at: datetime | None = None
    history: list = field(default_factory=list)          # iteration records, newest last
    last_responses: dict = field(default_factory=dict)   # needs_response, world_description, action_decision, state_response

    @classmethod
    def fresh(cls, now: datetime) -> "Situation"         # awake, phase_since == awake_since == now
    def to_dict(self) -> dict                            # datetimes as ISO strings
    @classmethod
    def from_dict(cls, data: dict, now: datetime) -> "Situation"   # missing or unparseable fields take the fresh(now) value

@dataclass(frozen=True)
class Step:
    kind: str
    reason: str = ""

def is_night(now: datetime) -> bool                       # now.hour >= 21 or now.hour < 6
def beats_today(s: Situation, now: datetime) -> int       # 0 when s.beats_day != now.date().isoformat()
def effective_interval(cfg: RhythmConfig, failures: int) -> timedelta
def next_beat_at(s: Situation, now: datetime, cfg: RhythmConfig) -> datetime | None   # None while asleep or at the daily cap
def decide(s: Situation, now: datetime, cfg: RhythmConfig) -> Step
def should_fall_asleep(action_key: str | None, time_of_day: str, sleep_need: float, cfg: RhythmConfig) -> bool
def lost_time(previous_alive_at: datetime | None, now: datetime, cfg: RhythmConfig) -> timedelta | None
```

`decide`, in this order. Every elapsed time is `max(timedelta(0), now - then)`.

Asleep:
1. slept ≥ `max_sleep` → `Step(WAKE, "slept_enough")`.
2. not `is_night(now)` and slept ≥ `min_sleep` → `Step(WAKE, "morning")`.
3. time since `last_sleep_tick_at` (or `phase_since`) ≥ `beat_interval` → `Step(SLEEP_TICK)`.
4. else `Step(WAIT, "asleep")`.

Awake (order revised by Task 4b so forced sleep never interrupts a conversation):
1. `last_chat_at` within `attention_window` → `Step(WAIT, "attention")`.
2. `sleep_enabled` and time since `awake_since` ≥ `max_awake` → `Step(FALL_ASLEEP, "exhausted")`.
3. `beats_today(s, now) >= max_beats_per_day` → `Step(WAIT, "daily_cap")`.
4. `last_beat_at is None`, or time since it ≥ `effective_interval(cfg, s.consecutive_failures)` → `Step(BEAT)`.
5. else `Step(WAIT, "backoff")` when `consecutive_failures >= failures_before_backoff`, otherwise `Step(WAIT, "interval")`.

`effective_interval`: `beat_interval` below 3 failures; from 3 on, `max(beat_interval, min(max_backoff, beat_interval * 2 ** (failures - 2)))`, so back-off never beats more often than the configured interval (3 failures → 30 min, 4 → 60 min, 5 → 60 min at the default interval).

`should_fall_asleep`: `cfg.sleep_enabled and action_key == "sleep" and (time_of_day == "night" or sleep_need < cfg.low_sleep_need)`.

`lost_time`: the gap when `previous_alive_at` is set and `now - previous_alive_at > lost_time_intervals * beat_interval`, else `None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_heartbeat_rhythm.py
CFG = RhythmConfig()
NOON = datetime(2026, 11, 15, 12, 0, 0)

def awake(now=NOON, **kw):
    s = Situation.fresh(now - timedelta(hours=2)); [setattr(s, k, v) for k, v in kw.items()]; return s
def asleep(started, **kw):
    s = Situation.fresh(started); s.phase = ASLEEP; s.last_sleep_tick_at = started
    [setattr(s, k, v) for k, v in kw.items()]; return s

class TestAwake(unittest.TestCase):
    def test_first_beat_is_immediate(self):
        self.assertEqual(decide(awake(), NOON, CFG), Step(BEAT))
    def test_waits_for_the_interval_then_beats(self):
        s = awake(last_beat_at=NOON - timedelta(minutes=14, seconds=59))
        self.assertEqual(decide(s, NOON, CFG), Step(WAIT, "interval"))
        s.last_beat_at = NOON - timedelta(minutes=15)
        self.assertEqual(decide(s, NOON, CFG), Step(BEAT))
    def test_conversation_postpones_the_beat(self):
        s = awake(last_beat_at=NOON - timedelta(hours=1), last_chat_at=NOON - timedelta(minutes=2, seconds=59))
        self.assertEqual(decide(s, NOON, CFG), Step(WAIT, "attention"))
        s.last_chat_at = NOON - timedelta(minutes=3)
        self.assertEqual(decide(s, NOON, CFG), Step(BEAT))
    def test_daily_cap_holds_until_the_next_day(self):
        s = awake(last_beat_at=NOON - timedelta(hours=1), beats_day="2026-11-15", beats_count=80)
        self.assertEqual(decide(s, NOON, CFG), Step(WAIT, "daily_cap"))
        self.assertEqual(decide(s, NOON + timedelta(days=1), CFG), Step(BEAT))
    def test_backoff_doubles_from_the_third_failure_up_to_an_hour(self):
        self.assertEqual(effective_interval(CFG, 2), timedelta(minutes=15))
        self.assertEqual(effective_interval(CFG, 3), timedelta(minutes=30))
        self.assertEqual(effective_interval(CFG, 4), timedelta(hours=1))
        self.assertEqual(effective_interval(CFG, 9), timedelta(hours=1))
        s = awake(last_beat_at=NOON - timedelta(minutes=20), consecutive_failures=3)
        self.assertEqual(decide(s, NOON, CFG), Step(WAIT, "backoff"))
    def test_twenty_hours_awake_forces_sleep(self):
        s = awake(awake_since=NOON - timedelta(hours=20))
        self.assertEqual(decide(s, NOON, CFG), Step(FALL_ASLEEP, "exhausted"))
    def test_clock_moving_backwards_neither_crashes_nor_beats(self):     # Review Focus 2
        s = awake(last_beat_at=NOON + timedelta(hours=1), last_chat_at=NOON + timedelta(hours=1))
        self.assertEqual(decide(s, NOON, CFG).kind, WAIT)

class TestAsleep(unittest.TestCase):
    NIGHT = datetime(2026, 11, 15, 23, 40, 0)
    def test_no_beats_while_asleep_only_ticks(self):
        s = asleep(self.NIGHT)
        self.assertEqual(decide(s, self.NIGHT + timedelta(minutes=14), CFG), Step(WAIT, "asleep"))
        self.assertEqual(decide(s, self.NIGHT + timedelta(minutes=15), CFG), Step(SLEEP_TICK))
    def test_wakes_in_the_morning_after_six_hours(self):
        s = asleep(self.NIGHT, last_sleep_tick_at=self.NIGHT + timedelta(hours=6, minutes=15))
        self.assertEqual(decide(s, datetime(2026, 11, 16, 5, 59), CFG).kind, WAIT)          # 6h19m slept, still night
        self.assertEqual(decide(s, datetime(2026, 11, 16, 6, 0), CFG), Step(WAKE, "morning"))
    def test_does_not_wake_in_daylight_before_six_hours(self):
        s = asleep(datetime(2026, 11, 16, 4, 0))
        self.assertNotEqual(decide(s, datetime(2026, 11, 16, 9, 59), CFG).kind, WAKE)
        self.assertEqual(decide(s, datetime(2026, 11, 16, 10, 0), CFG), Step(WAKE, "morning"))
    def test_nine_hours_wakes_her_even_at_night(self):
        s = asleep(datetime(2026, 11, 15, 13, 0))
        self.assertEqual(decide(s, datetime(2026, 11, 15, 22, 0), CFG), Step(WAKE, "slept_enough"))

class TestRules(unittest.TestCase):
    def test_falling_asleep(self):
        self.assertTrue(should_fall_asleep("sleep", "night", 90.0, CFG))
        self.assertTrue(should_fall_asleep("sleep", "afternoon", 29.9, CFG))
        self.assertFalse(should_fall_asleep("sleep", "afternoon", 30.0, CFG))     # a nap
        self.assertFalse(should_fall_asleep("rest", "night", 10.0, CFG))
        self.assertFalse(should_fall_asleep("sleep", "night", 10.0, RhythmConfig(sleep_enabled=False)))
    def test_night_is_21_to_6(self):
        self.assertTrue(is_night(datetime(2026, 1, 1, 21, 0))); self.assertTrue(is_night(datetime(2026, 1, 1, 5, 59)))
        self.assertFalse(is_night(datetime(2026, 1, 1, 6, 0))); self.assertFalse(is_night(datetime(2026, 1, 1, 20, 59)))
    def test_lost_time_needs_more_than_three_intervals(self):
        self.assertIsNone(lost_time(None, NOON, CFG))
        self.assertIsNone(lost_time(NOON - timedelta(minutes=45), NOON, CFG))
        self.assertEqual(lost_time(NOON - timedelta(minutes=46), NOON, CFG), timedelta(minutes=46))
    def test_config_from_env_ignores_bad_values(self):
        cfg = RhythmConfig.from_env({"JENBINA_BEAT_MINUTES": "5", "JENBINA_MAX_BEATS_PER_DAY": "10", "JENBINA_DISABLE_SLEEP": "1"})
        self.assertEqual((cfg.beat_interval, cfg.max_beats_per_day, cfg.sleep_enabled), (timedelta(minutes=5), 10, False))
        bad = RhythmConfig.from_env({"JENBINA_BEAT_MINUTES": "0", "JENBINA_MAX_BEATS_PER_DAY": "abc"})
        self.assertEqual((bad.beat_interval, bad.max_beats_per_day), (timedelta(minutes=15), 80))
    def test_situation_round_trips_and_tolerates_missing_fields(self):
        s = Situation.fresh(NOON); s.phase = ASLEEP; s.beats_count = 7; s.history = [{"iteration": 1}]
        self.assertEqual(Situation.from_dict(s.to_dict(), NOON), s)
        self.assertEqual(Situation.from_dict({"location": "Coupa Cafe", "phase_since": "not a date"}, NOON).phase_since, NOON)
    def test_next_beat_time_for_the_card(self):
        s = awake(last_beat_at=NOON - timedelta(minutes=4))
        self.assertEqual(next_beat_at(s, NOON, CFG), NOON + timedelta(minutes=11))
        self.assertIsNone(next_beat_at(asleep(NOON), NOON, CFG))
```

- [ ] **Step 2: Run** `$PY -m pytest tests/test_heartbeat_rhythm.py -q`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement** `core/heartbeat/rhythm.py` as specified. The module imports only the standard library.
- [ ] **Step 4: Run** the same command, then the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add the pure heartbeat rhythm (beats, sleep, back-off, lost time)`.

---

### Task 3: Make her state fit one being

Small changes to existing classes that the host and the chat path rely on. Every new parameter has a default so existing callers and tests keep working.

**Files:**
- Modify: `core/connect.py`, `core/needs/maslow_needs.py:222-231`, `core/person/person.py`, `core/working_memory/working_memory_system.py`, `core/social/social_cognition.py`, `core/insights/insight_system.py`, `core/interaction/chat_handler.py` (insight calls only)
- Test: `tests/test_connect.py`, `tests/test_maslow_needs.py`, `tests/test_person.py`, `tests/test_working_memory.py`, `tests/test_social_cognition.py`, `tests/test_insight_system.py`

**Interfaces:**
- Produces:
  - `core/connect.py`: `LLM_TIMEOUT_SECONDS: float` read from `JENBINA_LLM_TIMEOUT_SECONDS` (default `60.0`); every `ChatOpenAI(...)` in `get_llm` and `get_json_llm` gets `timeout=LLM_TIMEOUT_SECONDS, max_retries=1`.
  - `MaslowNeedsSystem.update_all_needs(self, time_delta: timedelta = None, skip: tuple[str, ...] = (), now: datetime | None = None)`: needs named in `skip` are not decayed. `now` (default `datetime.now()`) is used both to measure the elapsed time and to stamp `last_comprehensive_update` and each need's `last_updated` (`MaslowNeed.update` gains the same optional `now`). `EmotionSystem.update_all(self, now: datetime | None = None)` likewise. This is what lets the host's injected clock drive decay in tests.
  - `Person.last_decay_at: Optional[datetime] = None`, serialized as `"last_decay_at"`.
  - `Person.update_all_needs(self, now: datetime | None = None, skip_needs: tuple[str, ...] = ())`: needs (passing `skip=skip_needs, now=now`) and emotions (passing `now`) as today; lessons and goals decay by the real hours since `last_decay_at` (`0.0` when it is `None` or in the future), then `last_decay_at = now or datetime.now()`. The fixed `hours=0.5` is gone.
  - `Person.suspend_until(self, now: datetime) -> None`: sets `maslow_needs.last_comprehensive_update`, every need's `last_updated`, `emotion_system.last_update` and `last_decay_at` to `now`, so the time before `now` causes no decay.
  - `Person.get_current_state(self, partner: str | None = None)`: `state["social_cognition"]` is `social_cognition.get_stats(only=partner)` when `partner` is given, and `{"tracked_entities": n, "entities": {}}` when it is not.
  - `SocialCognitionSystem.get_stats(self, only: str | None = None)`: `entities` holds just `only`'s model when given (empty if unknown); unchanged when `None`.
  - `PersonModel.last_visit_time: Optional[datetime] = None`, `PersonModel.last_proactive_at: Optional[datetime] = None`, both in `to_dict` / `from_dict` as ISO strings or `None`.
  - `WorkingMemorySystem.add_note(self, content: str, cycles: int = 3) -> None`; `self.notes: list[dict]` (`{"content", "cycles_left"}`) serialized in `to_dict` / `from_dict`. `format_for_prompt()` starts with `"Keep in mind: <note>; <note>"` on its own line whenever there are notes (and returns only that line when the buffer is empty). Each `update()` lowers `cycles_left` by one and drops notes at zero.
  - `InsightSystem`: per-person state `self.people: dict[str, dict]` (`{"first_impression_delivered": bool, "day": "YYYY-MM-DD", "count": int}`) serialized under `"people"`; `max_per_day = 3`. Signatures gain a trailing `person_key: str = "User"`, and the two subtle-insight methods also `today: date | None = None`: `should_generate_first_impression(dossier, person_key="User")`, `generate_first_impression(dossier, first_message, person_key="User")`, `should_generate_insight(message_count, person_key="User", today=None)`, `generate_insight(dossier, recent_messages, emotional_state, self_narrative, person_key="User", today=None)`. The count resets when `day` differs from `today`. `from_dict` keeps a legacy top-level `first_impression_delivered` readable as `self.legacy_first_impression_delivered` (used by the adoption in Task 5) and does not apply it to any person. `insights_delivered`, `max_per_session` and `reset_session` are removed.
  - `handle_chat_interaction` passes `person_key=conversation_partner_name` to all four insight calls.

- [ ] **Step 1: Write the failing tests** (one per bullet; the assertions that pin spec values):

```python
# tests/test_person.py
def test_lessons_and_goals_decay_by_real_elapsed_hours(self):
    p = Person(); p.learning_system = MagicMock(); p.goal_system = MagicMock()
    t0 = datetime(2026, 11, 15, 12, 0)
    p.update_all_needs(now=t0)                              # first call: nothing to measure from
    p.learning_system.decay_all_lessons.assert_called_with(hours=0.0)
    p.update_all_needs(now=t0 + timedelta(hours=2))
    p.learning_system.decay_all_lessons.assert_called_with(hours=2.0)
    p.goal_system.decay_all_goals.assert_called_with(hours=2.0)

def test_last_decay_time_survives_serialization(self):
    p = Person(); t0 = datetime(2026, 11, 15, 12, 0); p.update_all_needs(now=t0)
    self.assertEqual(Person.deserialize(p.serialize()).last_decay_at, t0)

def test_needs_decay_follows_the_clock_it_is_given(self):
    p = Person(); t0 = datetime(2030, 1, 1, 12, 0); p.suspend_until(t0)
    p.maslow_needs.needs["hunger"].satisfaction = 80.0
    p.update_all_needs(now=t0 + timedelta(hours=2))            # hunger decays 8 per hour, give or take 20%
    self.assertAlmostEqual(p.maslow_needs.get_need_satisfaction("hunger"), 64.0, delta=3.5)
    self.assertEqual(p.maslow_needs.last_comprehensive_update, t0 + timedelta(hours=2))

def test_suspend_until_removes_the_gap_from_every_clock(self):
    p = Person(); hunger_before = p.maslow_needs.get_need_satisfaction("hunger")
    p.maslow_needs.last_comprehensive_update = datetime.now() - timedelta(hours=10)
    p.suspend_until(datetime.now()); p.update_all_needs()
    self.assertAlmostEqual(p.maslow_needs.get_need_satisfaction("hunger"), hunger_before, delta=0.5)

def test_current_state_shows_only_the_partners_social_model(self):
    p = Person(); p.init_social_cognition()
    p.social_cognition.get_or_create_model("Ann").beliefs.append("ANN-SECRET")
    p.social_cognition.get_or_create_model("Bob").beliefs.append("BOB-SECRET")
    self.assertNotIn("ANN-SECRET", json.dumps(p.get_current_state(partner="Bob"), default=str))
    self.assertIn("BOB-SECRET", json.dumps(p.get_current_state(partner="Bob"), default=str))
    self.assertNotIn("SECRET", json.dumps(p.get_current_state(), default=str))

# tests/test_maslow_needs.py
def test_skipped_needs_do_not_decay(self):
    needs = MaslowNeedsSystem(); needs.needs["sleep"].satisfaction = 50.0; needs.needs["hunger"].satisfaction = 50.0
    needs.update_all_needs(timedelta(hours=2), skip=("sleep",))
    self.assertEqual(needs.get_need_satisfaction("sleep"), 50.0)
    self.assertLess(needs.get_need_satisfaction("hunger"), 50.0)

# tests/test_working_memory.py
def test_notes_reach_the_prompt_and_expire(self):
    wm = WorkingMemorySystem(); wm.add_note("I was away for 3h 10m", cycles=2)
    self.assertTrue(wm.format_for_prompt().startswith("Keep in mind: I was away for 3h 10m"))
    self.assertIn("I was away", WorkingMemorySystem.from_dict(wm.to_dict()).format_for_prompt())
    wm.update(needs={}, emotions={}); self.assertIn("I was away", wm.format_for_prompt())
    wm.update(needs={}, emotions={}); self.assertNotIn("I was away", wm.format_for_prompt())

# tests/test_insight_system.py
def test_first_impression_and_daily_limit_are_per_person(self):
    s = InsightSystem(llm_returning("You hide it well."))
    s.generate_first_impression({"job": "x"}, "hi", person_key="Ann")
    self.assertFalse(s.should_generate_first_impression({"job": "x"}, person_key="Ann"))
    self.assertTrue(s.should_generate_first_impression({"job": "x"}, person_key="Bob"))
    day = date(2026, 11, 15)
    for _ in range(3): s.generate_insight({}, [], {}, "", person_key="Ann", today=day)
    self.assertFalse(s.should_generate_insight(5, person_key="Ann", today=day))
    self.assertTrue(s.should_generate_insight(5, person_key="Bob", today=day))
    self.assertTrue(s.should_generate_insight(5, person_key="Ann", today=day + timedelta(days=1)))
    restored = InsightSystem.from_dict(s.to_dict(), llm=None)
    self.assertFalse(restored.should_generate_insight(5, person_key="Ann", today=day))

# tests/test_connect.py
self.assertEqual(call_kwargs.kwargs["timeout"], 60.0); self.assertEqual(call_kwargs.kwargs["max_retries"], 1)   # get_llm and get_json_llm

# tests/test_social_cognition.py
model.last_visit_time = datetime(2026, 11, 15, 9, 0); model.last_proactive_at = datetime(2026, 11, 15, 10, 0)
self.assertEqual(PersonModel.from_dict(model.to_dict()).last_visit_time, datetime(2026, 11, 15, 9, 0))
self.assertEqual(list(system.get_stats(only="Bob")["entities"]), ["Bob"])
```

- [ ] **Step 2: Run** those six test files. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** each bullet. Update the existing insight tests that used `insights_delivered`, `max_per_session` or `reset_session` to the per-person API.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: per-person visit and insight state, real-time decay, LLM timeouts`.

---

### Task 4: One iteration, the headless one

Port what only the UI copy does into `run_single_iteration_headless`, and give it the hooks the host needs.

**Files:**
- Create: `core/heartbeat/outreach.py`
- Modify: `core/simulation_runner.py`
- Test: `tests/test_simulation_runner.py` (headless classes), `tests/test_heartbeat_outreach.py`

**Interfaces:**
- Consumes: `should_fall_asleep`, `RhythmConfig` (Task 2); `PersonModel.last_proactive_at` (Task 3).
- Produces:
  - `choose_outreach_target(person, people: dict[int, str], now: datetime) -> tuple[int, str] | None` in `core/heartbeat/outreach.py`. Candidates are entries of `people` whose conversation (`person.conversations[key]`) has a message with `timestamp >= now - 7 days` and whose social model's `last_proactive_at` is `None` or older than `now - 6 hours`. Returns the candidate with the highest `relationship.closeness`; ties go to the most recent message. `None` when there is no candidate or no social cognition.
  - New keys read from `context` by `run_single_iteration_headless`, all optional:
    - `"status"`: an object with `stage(text: str)`. Called once at the start of each of the five stages (`"sensing the world…"`, `"thinking…"`, `"deciding…"`, `"reflecting…"`, `"learning…"`). An exception from the sink is swallowed.
    - `"sleep_config"`: a `RhythmConfig`. When present and `should_fall_asleep(matched_action, world_summary["time"]["time_of_day"], sleep need before the action, cfg)` is true, the `sleep` action effect is **not** applied and the result's `fell_asleep` is `True`.
    - `"proactive_target"`: `(user_id, person_key)`. The proactive block runs only when it is present; the keys `display_name` and `user_id` are no longer read for this. Triggers are checked for `person_key`; the message is generated with `generate_proactive_message(..., display_name=person_key, ...)`, sent with `person.send_message(person_key, message, "proactive")`, stored with `user_db.store_message(user_id, "Jenbina", message, "proactive_message")`, and `model.last_proactive_at` is set.
  - New keys in the returned dict: `"matched_action": str | None`, `"fell_asleep": bool`, `"proactive_sent_to": str | None`.
  - Ported from `core/ui/simulation.py`: recording simulated social actions in `person.social_interaction_tracker` with the tone map (`:565-577`, including `_SOCIAL_ACTION_KEYS` and `_tone_map` moved to module level); appending `"\n" + person.social_interaction_tracker.format_for_prompt()` to the monologue's `world_context_str` (`:446-454`); `curiosity_stats` and `social_interaction_stats` in the debug entry.
  - `context["event_log"]` is required to be passed by the host; the fallback construction stays for other callers.

- [ ] **Step 1: Write the failing tests.** Reuse this file's existing `build_env` fixture for the headless runner.

```python
# tests/test_simulation_runner.py
class TestHeadlessParity(unittest.TestCase):
    def test_social_action_is_recorded_in_the_tracker(self):       # chosen_action "Chat with the neighbor"
        self.assertEqual(person.social_interaction_tracker.interactions[-1].interaction_type, "simulated_social")
    def test_social_day_reaches_the_monologue(self):
        self.assertIn("Social interactions today", think_kwargs["world_context_str"])
    def test_status_sink_gets_five_stages_and_may_fail(self):
        self.assertEqual(len(sink.stage.call_args_list), 5)          # and a sink whose stage() raises does not break the iteration

class TestSleepGate(unittest.TestCase):
    def test_sleep_at_night_is_not_an_instant_refill(self):           # chosen "Go to bed and sleep", time_of_day "night", sleep need 60
        self.assertTrue(result["fell_asleep"]); self.assertEqual(result["matched_action"], "sleep")
        self.assertLessEqual(person.maslow_needs.get_need_satisfaction("sleep"), 60.0)
    def test_daytime_sleep_is_a_nap_as_before(self):                  # time_of_day "afternoon", sleep need 60
        self.assertFalse(result["fell_asleep"]); self.assertGreater(person.maslow_needs.get_need_satisfaction("sleep"), 60.0)
    def test_without_sleep_config_nothing_changes(self):              # no "sleep_config" key, night
        self.assertFalse(result["fell_asleep"]); self.assertGreater(person.maslow_needs.get_need_satisfaction("sleep"), 60.0)

class TestHeadlessProactive(unittest.TestCase):                       # replaces TestHeadlessProactiveContext
    def test_message_goes_to_the_target_with_proactive_type(self):   # context["proactive_target"] = (7, "Ann"), triggers firing
        self.assertEqual(person.conversations["Ann"].messages[-1].message_type, "proactive")
        user_db.store_message.assert_called_once_with(7, "Jenbina", "Still there?", "proactive_message")
        self.assertIsNotNone(person.social_cognition.get_or_create_model("Ann").last_proactive_at)
        self.assertEqual(result["proactive_sent_to"], "Ann")
    def test_no_target_means_no_proactive_check(self):
        generate_proactive_message.assert_not_called(); self.assertIsNone(result["proactive_sent_to"])

# tests/test_heartbeat_outreach.py
NOW = datetime(2026, 11, 15, 12, 0)
def test_picks_the_closest_recent_person(self):        # Ann closeness 70 (message 2 days ago), Bob 40 (1 hour ago), Cy 90 (8 days ago)
    self.assertEqual(choose_outreach_target(person, {1: "Ann", 2: "Bob", 3: "Cy"}, NOW), (1, "Ann"))
def test_skips_anyone_messaged_proactively_in_the_last_six_hours(self):   # Ann.last_proactive_at = NOW - 5h59m
    self.assertEqual(choose_outreach_target(person, {1: "Ann", 2: "Bob"}, NOW), (2, "Bob"))
def test_nobody_recent_means_nobody(self):
    self.assertIsNone(choose_outreach_target(person, {3: "Cy"}, NOW)); self.assertIsNone(choose_outreach_target(person, {}, NOW))
```

- [ ] **Step 2: Run** `$PY -m pytest tests/test_simulation_runner.py tests/test_heartbeat_outreach.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** the runner changes and `choose_outreach_target`. Leave `core/ui/simulation.py` untouched in this task.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: make the headless iteration complete (social tracking, sleep gate, targeted outreach)`.

---

### Task 4b: Fixes from the review of Tasks 1 to 3

A review of the committed Tasks 1 to 3 found ten defects. This task fixes them; the text of Tasks 1, 2, 5 and 6 above already describes the corrected behaviour.

**Files:**
- Modify: `core/heartbeat/store.py`, `core/heartbeat/rhythm.py`, `core/connect.py`, `core/emotions/emotion_system.py`, `core/needs/maslow_needs.py`, `core/ui/shared_init.py:61-68`
- Test: `tests/test_heartbeat_store.py`, `tests/test_heartbeat_rhythm.py`, `tests/test_connect.py`, `tests/test_emotions.py`, `tests/test_maslow_needs.py`, `tests/test_insight_system.py`

**Interfaces:**
- Produces (changed): `BeingStore.person_key(self, user_id: int, display_name: str | None) -> str`; `BeingStore.save_state(self, person_state_json: str, situation: dict, owner: str | None = None) -> bool`; `make_owner_id()` and `owner_is_dead()` as below.

Fixes, one per finding:

1. **Insight state wiped on session load** (`core/ui/shared_init.py`). Replace the `old_fi` / `init_insight_system` / flag lines with: rebuild on the plain LLM keeping all state, `InsightSystem.from_dict(person.insight_system.to_dict(), insight_llm)` when there is one, `init_insight_system(insight_llm)` when there is none.
2. **A key exposed part of an email address.** `person_key` drops its `email` parameter and follows the rule now written in Task 1: display name, else `User {id}`; on collision `Name (2)`, `Name (3)`.
3. **A process that lost the lease could still save.** `save_state(..., owner=...)` checks, inside one `BEGIN IMMEDIATE` transaction, that `being_lease.owner == owner` and writes only then; returns whether it wrote. Without `owner` it writes as before and returns `True`.
4. **Same hostname, different PID namespace counted as dead.** The machine part of an owner id becomes `f"{socket.gethostname()}|{pid_namespace}"`, where `pid_namespace` is `os.readlink("/proc/self/ns/pid")` when that link exists and `""` otherwise. `owner_is_dead` returns `True` only when the whole machine part equals this process's and the pid is not running. Owner ids are still split with `rsplit(":", 2)`.
5. **Back-off could shorten the interval.** `effective_interval` never returns less than `cfg.beat_interval`.
6. **Unreadable situation crashed the start.** `load_state` returns `{}` for a `situation_json` that does not parse or is not an object; `Situation.from_dict` treats non-dict `data` as `{}`.
7. **A bad `JENBINA_LLM_TIMEOUT_SECONDS` broke every import.** Parse it in a helper that returns `60.0` when the value is missing, empty, unparseable, not finite, or `<= 0`.
8. **`person_key` took the write lock to read.** Look the user up with a plain `SELECT` first; open `BEGIN IMMEDIATE` only to insert, re-checking inside the transaction.
9. **Forced sleep could interrupt a conversation.** In `decide`, the attention rule comes before the 20-hours-awake rule (order as now written in Task 2).
10. **A clock stepping back moved decay stamps backwards.** `EmotionSystem.update_all` and `MaslowNeedsSystem.update_all_needs` never set their stamp (`last_update`, `last_comprehensive_update`) earlier than its current value. `Person.suspend_until` still sets the stamps directly.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_heartbeat_store.py
def test_save_is_refused_once_the_lease_is_lost(self):
    self.store.acquire_lease("hostA|:1:aa", T0, STALE)
    self.assertTrue(self.store.save_state('{"v": 1}', {}, owner="hostA|:1:aa"))
    with patch("core.heartbeat.store.owner_is_dead", return_value=False):
        self.store.acquire_lease("hostB|:2:bb", T0 + timedelta(seconds=121), STALE)
    self.assertFalse(self.store.save_state('{"v": 2}', {}, owner="hostA|:1:aa"))
    self.assertEqual(self.store.load_state()[0], '{"v": 1}')
    self.assertTrue(self.store.save_state('{"v": 3}', {}))                 # unfenced callers (adoption, tests) still write
def test_no_email_ever_reaches_a_key(self): ...                            # TestPeople cases as rewritten in Task 1
def test_known_user_lookup_takes_no_write_lock(self):
    self.store.person_key(1, "Alex")
    blocker = sqlite3.connect(self.store.db_path); blocker.execute("BEGIN IMMEDIATE")
    try: self.assertEqual(self.store.person_key(1, "Alex"), "Alex")       # would raise 'database is locked' if it wrote
    finally: blocker.rollback(); blocker.close()
def test_other_pid_namespace_is_never_assumed_dead(self):
    with patch("core.heartbeat.store._pid_namespace", return_value="pid:[1]"):
        mine = make_owner_id()
    with patch("core.heartbeat.store._pid_namespace", return_value="pid:[2]"):
        self.assertFalse(owner_is_dead(mine.rsplit(":", 2)[0] + ":999999999:aa"))
def test_unreadable_situation_loads_as_empty(self):                        # write situation_json = "{broken" and "null" directly with sqlite3
    self.assertEqual(self.store.load_state()[1], {})

# tests/test_heartbeat_rhythm.py
def test_backoff_never_beats_more_often_than_configured(self):
    slow = RhythmConfig(beat_interval=timedelta(hours=2))
    self.assertEqual(effective_interval(slow, 3), timedelta(hours=2)); self.assertEqual(effective_interval(slow, 9), timedelta(hours=2))
def test_forced_sleep_waits_for_the_conversation_to_end(self):
    s = awake(awake_since=NOON - timedelta(hours=20), last_chat_at=NOON - timedelta(minutes=1))
    self.assertEqual(decide(s, NOON, CFG), Step(WAIT, "attention"))
    s.last_chat_at = NOON - timedelta(minutes=3); self.assertEqual(decide(s, NOON, CFG), Step(FALL_ASLEEP, "exhausted"))
def test_non_dict_situation_loads_fresh(self):
    self.assertEqual(Situation.from_dict(None, NOON), Situation.fresh(NOON)); self.assertEqual(Situation.from_dict([], NOON), Situation.fresh(NOON))

# tests/test_connect.py
def test_bad_timeout_values_fall_back_to_sixty_seconds(self):
    for bad in ("", "60s", "0", "-5", "nan", "inf"): self.assertEqual(timeout_from_env({"JENBINA_LLM_TIMEOUT_SECONDS": bad}), 60.0)
    self.assertEqual(timeout_from_env({"JENBINA_LLM_TIMEOUT_SECONDS": "30"}), 30.0); self.assertEqual(timeout_from_env({}), 60.0)

# tests/test_emotions.py and tests/test_maslow_needs.py
def test_a_clock_stepping_back_does_not_move_the_stamp(self):
    system.last_update = T; system.update_all(now=T - timedelta(hours=1)); self.assertEqual(system.last_update, T)
    needs.last_comprehensive_update = T; needs.update_all_needs(now=T - timedelta(hours=1)); self.assertEqual(needs.last_comprehensive_update, T)

# tests/test_insight_system.py
def test_rebuilding_on_another_llm_keeps_every_persons_state(self):       # the shared_init rebuild: from_dict(old.to_dict(), new_llm)
    rebuilt = InsightSystem.from_dict(s.to_dict(), other_llm)
    self.assertIs(rebuilt.llm, other_llm); self.assertFalse(rebuilt.should_generate_first_impression({"x": 1}, person_key="Ann"))
```

(`timeout_from_env(env: Mapping[str, str] = os.environ) -> float` is the helper for fix 7; `_pid_namespace() -> str` the one for fix 4.) Update the Task 1 and Task 2 tests that pinned the old behaviour: the email-based keys, and any test that expected forced sleep ahead of attention.

- [ ] **Step 2: Run** `$PY -m pytest tests/test_heartbeat_store.py tests/test_heartbeat_rhythm.py tests/test_connect.py tests/test_emotions.py tests/test_maslow_needs.py tests/test_insight_system.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** the ten fixes.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `fix: review findings in the being's storage, rhythm and state plumbing`.

---

### Task 5: Building her, and moving the existing Jenbina

**Files:**
- Create: `core/heartbeat/being.py`, `core/heartbeat/adoption.py`
- Modify: `core/auth/user_db.py` (one read method)
- Test: `tests/test_heartbeat_adoption.py`, `tests/test_user_db.py`

**Interfaces:**
- Consumes: `BeingStore` (Task 1), `Situation` (Task 2), per-person fields (Task 3).
- Produces:
  - `UserDatabase.list_person_states(self) -> list[dict]`: `[{"user_id": int, "person_state_json": str}]` ordered by `user_id`.
  - `core/heartbeat/being.py`: `class BeingStateError(Exception)`; `build_person(state_json: str | None, llm, llm_json_mode, insight_llm) -> Person`. With `None` it creates a new `Person` and calls `update_all_needs()`. Otherwise `Person.deserialize(state_json, llm_json_mode)`, raising `BeingStateError` (chained) if that fails. In both cases every subsystem that is `None` is initialised (learning, goal, planning with `llm_json_mode`; inner monologue with `llm`; social cognition, self narrative, curiosity, social interaction tracker), and the insight system is always rebuilt on `insight_llm` keeping its state (`InsightSystem.from_dict(old.to_dict(), insight_llm)`, or `init_insight_system(insight_llm)` when there was none). This replaces `_load_or_create_person` in `core/ui/shared_init.py` and `load_person` in `run_scheduler.py`.
  - `core/heartbeat/adoption.py`:

```python
@dataclass
class AdoptionReport:
    adopted_user_id: int | None        # None: nobody to adopt, she starts new
    experiences: int
    imported_user_ids: list[int]
    events_copied: int

def choose_user_to_adopt(states: list[dict], prefer_user_id: int | None = None) -> int | None
def adopt_existing(store: BeingStore, user_db, llm, llm_json_mode, insight_llm, now: datetime,
                   prefer_user_id: int | None = None) -> tuple[Person, Situation, AdoptionReport]
```

`choose_user_to_adopt`: the user whose state JSON has the most `learning_system.experiences` (a state that does not parse counts as −1 and is never chosen); ties go to the lowest `user_id`; `prefer_user_id` wins when it has a readable state and raises `ValueError` when it does not; `None` for an empty list.

`adopt_existing`, called only when `store.load_state()` is `None`:
1. Read `user_db.list_person_states()` and choose. With nobody to adopt, return `build_person(None, ...)`, `Situation.fresh(now)` and an empty report.
2. Build her from the chosen JSON. Register the chosen user first (`store.person_key(user_id, display_name)` from `user_db.get_user_by_id`), so they keep their plain display name.
3. For the chosen user's key: move the legacy `person.last_visit_time` to that social model's `last_visit_time`, and the legacy `insight_system.legacy_first_impression_delivered` to that person's insight state.
4. Copy the chosen user's life events: `store.import_events(user_db.get_events(user_id, limit=100000))`.
5. For every other user with a readable state, parse the JSON (no `Person` needed) and, using that user's own display name `D` and their registered key `K`: copy `conversations[D]` into `person.conversations[K]` (with `outsider_name = K`), copy `social_cognition.models[D]` into `person.social_cognition.models[K]`, set that model's `last_visit_time` from their `last_visit_time`, and their insight first-impression flag from their `insight_system.first_impression_delivered`. Missing parts are skipped. Nothing of theirs is merged into any other key.
6. `store.save_state(person.serialize(), situation.to_dict())`, log the report with `logging.getLogger("jenbina.heartbeat")`, and return. `user_state` and `events` are only read.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_heartbeat_adoption.py  (setUp: temp db; UserDatabase and BeingStore on the same path; users Ann (id 1), Bob (id 2), a second "Ann" (id 3))
def test_most_experiences_wins_ties_to_lowest_id(self):
    self.assertEqual(choose_user_to_adopt([state(1, experiences=4), state(2, experiences=9), state(3, experiences=9)]), 2)
    self.assertEqual(choose_user_to_adopt([state(1, experiences=4), state(2, experiences=9)], prefer_user_id=1), 1)
    self.assertIsNone(choose_user_to_adopt([]))
    self.assertEqual(choose_user_to_adopt([{"user_id": 1, "person_state_json": "{broken"}, state(2, experiences=0)]), 2)
    with self.assertRaises(ValueError): choose_user_to_adopt([state(1, experiences=4)], prefer_user_id=8)

def test_adoption_keeps_her_and_imports_everyone_elses_history(self):
    # Bob's state: 9 experiences, conversation "Bob" [bob-hello], last_visit_time T, first impression delivered, 2 life events
    # Ann's state: 4 experiences, conversation "Ann" [ann-hello], model "Ann" with dossier {"job": "ANN-JOB"}
    person, situation, report = adopt_existing(self.store, self.user_db, MagicMock(), MagicMock(), MagicMock(), NOW)
    self.assertEqual((report.adopted_user_id, report.experiences, report.imported_user_ids, report.events_copied), (2, 9, [1, 3], 2))
    self.assertEqual(len(person.learning_system.experiences), 9)                             # her mind is Bob's copy
    self.assertEqual(person.conversations["Ann"].messages[0].content, "ann-hello")
    self.assertEqual(person.social_cognition.models["Ann"].user_dossier, {"job": "ANN-JOB"})
    self.assertEqual(person.social_cognition.models["Bob"].last_visit_time, T)
    self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, person_key="Bob"))
    self.assertTrue(person.insight_system.should_generate_first_impression({"x": 1}, person_key="Ann"))
    self.assertEqual(len(self.store.get_events()), 2)
    self.assertIsNotNone(self.store.load_state())
    self.assertEqual(situation.phase, "awake")

def test_two_accounts_with_one_name_never_share_a_conversation(self):
    # users 1 and 3 are both "Ann" with different messages; Bob (2) is adopted
    self.assertEqual(person.conversations["Ann"].messages[0].content, "ann-hello")
    self.assertEqual(person.conversations[self.store.people()[3]].messages[0].content, "other-ann-hello")
    self.assertNotEqual(self.store.people()[3], "Ann")

def test_old_rows_are_untouched(self):
    before = (self.user_db.load_person_state(2), len(self.user_db.get_events(2)))
    adopt_existing(...); self.assertEqual((self.user_db.load_person_state(2), len(self.user_db.get_events(2))), before)

def test_nobody_to_adopt_gives_a_new_person(self):
    person, situation, report = adopt_existing(self.store, self.user_db, None, None, None, NOW)
    self.assertIsNone(report.adopted_user_id); self.assertEqual(person.name, "Jenbina")

def test_build_person_refuses_unreadable_state(self):
    with self.assertRaises(BeingStateError): build_person("{broken", None, None, None)
```

The fixture builds each saved state from a real `Person` with a `LearningSystem(MagicMock())` holding the stated number of `record_experience` calls, serialized with `Person.serialize()`. LLMs passed to `adopt_existing` are `MagicMock()`s, because `Person.deserialize` only restores the learning system when it is given an LLM.

- [ ] **Step 2: Run** `$PY -m pytest tests/test_heartbeat_adoption.py tests/test_user_db.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** `list_person_states`, `being.py` and `adoption.py`.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: build the single being and adopt the existing per-user Jenbina`.

---

### Task 6: The host

**Files:**
- Create: `core/heartbeat/host.py`
- Test: `tests/test_heartbeat_host.py`

**Interfaces:**
- Consumes: everything from Tasks 1 to 5; `run_single_iteration_headless(person, llm_json_mode, meta_cognitive_system, iteration, context) -> dict`.
- Produces:

```python
@dataclass
class ChatTurn:
    person_key: str
    user_id: int
    woken: bool                 # this message woke her
    last_responses: dict        # needs_response, world_description, action_decision, state_response (all may be missing)
    history: list               # iteration records, newest last
    event_log: LifeEventLog

@dataclass
class HeartStatus:
    hosting: bool
    holder: str | None          # the other owner when not hosting
    phase: str
    phase_since: datetime
    last_beat_at: datetime | None
    next_beat_at: datetime | None
    note: str                   # "", "daily_cap" or "backoff"
    busy: bool                  # a beat is running
    stage: str                  # what she is doing right now; "idle" between beats

class JenbinaHost:
    def __init__(self, store: BeingStore, user_db, llm, llm_json_mode, insight_llm, *,
                 clock: Callable[[], datetime] = datetime.now,
                 iteration_fn: Callable = run_single_iteration_headless,
                 meta_cognitive_system=None,          # built from llm_json_mode when None
                 config: RhythmConfig | None = None,  # RhythmConfig.from_env() when None
                 owner: str | None = None,            # make_owner_id() when None
                 adopt_user_id: int | None = None)
    person: Person
    situation: Situation
    event_log: LifeEventLog
    meta_cognitive_system: Any
    lock: threading.RLock
    hosting: bool
    debug_iterations: list
    def start(self, threads: bool = True) -> bool      # False when another process holds the lease; raises BeingStateError on unreadable state
    def stop(self) -> None                             # stops threads, saves, releases the lease; safe to call twice
    def run_forever(self) -> None                      # pulse thread + heart loop in the calling thread until stop()
    def pulse(self) -> bool                            # renew the lease; on failure hosting becomes False
    def tick(self) -> Step                             # one pass of the heart
    def step_once(self) -> str                         # "done", "failed", "asleep", "daily_cap" or "not_hosting"
    def chat_turn(self, user: dict) -> ContextManager[ChatTurn]
    def greeting_turn(self, user: dict) -> ContextManager[ChatTurn | None]
    def person_key(self, user: dict) -> str
    def save(self) -> None
    def status(self) -> HeartStatus
```

Behaviour:

- **`stop`**: stop both threads, `save()` if hosting, renew the lease one last time (so its `renewed_at` is the moment she stopped), then `release_lease(owner)` and `hosting = False`.
- **`start`**: `acquire_lease(owner, now, cfg.lease_stale_after)`. Not acquired → `hosting = False`, remember the holder, return `False`, load nothing. Acquired → `load_state()`; a row gives `build_person(json, ...)` and `Situation.from_dict(situation, now)`; no row gives `adopt_existing(..., prefer_user_id=adopt_user_id)`. The lease's `previous_renewed_at` becomes the "last alive" time, so the first tick absorbs any lost time. With `threads=True` start two daemon threads (`heart`: `tick()` every `loop_period_seconds`; `pulse`: `pulse()` every `loop_period_seconds`) and register `stop` with `atexit`. Calling `start` again while hosting is a no-op returning `True`; calling it while not hosting retries the lease.
- **`tick`**: not hosting → `Step(WAIT, "not_hosting")`. Otherwise, holding the lock for the whole pass: if `lost_time(last_alive, now, cfg)` gives a gap, absorb it; `decide`; perform `BEAT`, `SLEEP_TICK`, `FALL_ASLEEP` (reason from the step) or `WAKE` (reason from the step); set `last_alive = clock()`; return the step. `tick` never raises: any exception is logged and `Step(WAIT, "error")` returned.
- **Beat**: set `situation.last_beat_at = now`; roll the day counter (`beats_day != today` → `beats_day = today, beats_count = 0`) and add one **before** running, so failed attempts count toward the cap. Call `iteration_fn(person=..., llm_json_mode=..., meta_cognitive_system=..., iteration=situation.beat_index, context=ctx)` where `ctx` has `simulation_history` (the situation's list), `jenbina_location`, `debug_iterations`, `user_db`, `event_log`, `status` (a sink that sets `self._stage`), `sleep_config` (the config), and `proactive_target` (`choose_outreach_target(person, store.people(), now)`). On success: `consecutive_failures = 0`, `beat_index += 1`, append an iteration record (`iteration`, `timestamp`, `duration_seconds`, `action_decision`, `needs_state`, `emotions_state`, `world_summary`, `satisfaction_delta`, as `run_simulation_loop` builds it today) and trim to `history_limit`, set `last_responses` (`needs_response` is the record's `needs_state`, as today), take `location` from `ctx["jenbina_location"]`, trim `debug_iterations` to `debug_limit`, and fall asleep with reason `"chose"` when `result.get("fell_asleep")`. On an exception: log it, `consecutive_failures += 1`. Always: stage back to `"idle"`, `save()`.
- **Falling asleep** (`reason`): if `woken_by_message_at` is set, within `resleep_window` of now, and `interrupted_sleep_started_at` is set, this is the same sleep: `phase_since = interrupted_sleep_started_at` and no event. Otherwise `phase_since = now` and `make_sleep(reason)` is recorded. Then `phase = ASLEEP`, `last_sleep_tick_at = now`, both interruption markers cleared.
- **Sleep tick**: `hours` since `last_sleep_tick_at`; `person.maslow_needs.satisfy_need("sleep", cfg.sleep_recovery_per_hour * hours, source="sleeping")`; `person.update_all_needs(now=now, skip_needs=("sleep",))`; `last_sleep_tick_at = now`; `save()`. No LLM is touched.
- **Waking** (`reason`): run a sleep tick for the part interval; record `make_wake(now - phase_since, reason)`; when `reason == "message"` set `interrupted_sleep_started_at = phase_since`, `woken_by_message_at = now` and add the working-memory note `"I was asleep and a message just woke me."` (`cycles=2`); then `phase = AWAKE`, `phase_since = awake_since = now`.
- **Absorbing lost time** (`gap`): `person.suspend_until(now)`; if asleep and `gap > cfg.max_sleep`, she is awake (`phase_since = awake_since = now`, no wake event), else the phase is kept and `last_sleep_tick_at = now` when asleep; record `make_gap(gap)`; add the note `f"I was away for {format_duration(gap)}. That time passed without me."` (`cycles=3`); `save()`.
- **`chat_turn`**: takes the lock (blocking). If asleep, wake with reason `"message"` and `woken=True`. `last_chat_at = now`. Yields the `ChatTurn`. On exit: `last_chat_at = clock()`, `save()`, release.
- **`greeting_turn`**: tries the lock without blocking. Lock busy, or she is asleep → yields `None` and changes nothing. Otherwise yields a `ChatTurn` and saves on exit.
- **`step_once`**: under the lock (blocking): not hosting → `"not_hosting"`; asleep → `"asleep"`; `beats_today >= cap` → `"daily_cap"`; otherwise a beat right now, ignoring interval, attention and back-off, returning `"done"` or `"failed"`.
- **`person_key`**: `store.person_key(user["id"], user.get("display_name"))`, cached per user id in the host so page refreshes do not query the database.
- **`save`**: under the lock, `store.save_state(person.serialize(), situation.to_dict(), owner=self.owner)`. A `False` result means another process has taken the lease: set `hosting = False`, log it, and write nothing more.
- **`status`**: reads without the lock. `note` is `"daily_cap"` at the cap, `"backoff"` when `consecutive_failures >= failures_before_backoff`, else `""`.

- [ ] **Step 1: Write the failing tests.** Fixture: temp db, `BeingStore`, `UserDatabase` with users Ann (id 1) and Bob (id 2), a mutable clock (`self.now`, starting `datetime(2026, 11, 15, 12, 0)`, `clock=lambda: self.now`), a fake `iteration_fn` returning a canned result dict (`action_decision={"chosen_action": "Read a book"}`, `fell_asleep=False`, and the other keys of the runner's result) and recording its calls in `self.calls`, `MagicMock()` LLMs, `meta_cognitive_system=MagicMock()`, `self.owner = "test:1:aa"`, `host.start(threads=False)`, then `host.person.suspend_until(self.now)` so her clocks start on the fake clock. Helpers:
  - `advance(**delta)`: move the clock only. More than 45 minutes without a tick is lost time, so use it for gaps and for short hops.
  - `live(hours=0, minutes=0, until=None) -> list[Step]`: move the clock in 5-minute steps, calling `host.tick()` after each, the way the running heart would. Returns the steps.
  - `put_to_sleep(at, sleep_need=None, hunger=None)`: set `self.now = at`, `person.suspend_until(at)`, the given need levels, and call the host's fall-asleep routine with reason `"chose"`.
  - `next_result(**overrides)` and `fail_next(n)`: shape the fake iteration's next result, or make its next `n` calls raise.

```python
class TestOwnership(unittest.TestCase):
    def test_second_host_does_not_host(self):
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            other = make_host(owner="other:1:zz"); self.assertFalse(other.start(threads=False))
        self.assertFalse(other.hosting); self.assertEqual(other.status().holder, self.owner)
        self.assertEqual(other.tick(), Step(WAIT, "not_hosting"))
    def test_losing_the_lease_stops_the_heart(self):
        self.store.release_lease(self.owner); self.store.acquire_lease("other:1:zz", self.now, STALE)
        self.assertFalse(self.host.pulse()); self.assertFalse(self.host.hosting)
    def test_stop_releases_the_lease(self): ...

class TestBeats(unittest.TestCase):
    def test_first_tick_beats_and_saves_her_situation(self):
        self.assertEqual(self.host.tick(), Step(BEAT)); self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0]["iteration"], 0); self.assertIn("event_log", self.calls[0]["context"])
        again = make_host(owner=self.owner); again.start(threads=False)                 # same owner: restart
        self.assertEqual(again.situation.history[-1]["action_decision"]["chosen_action"], "Read a book")
        self.assertEqual(again.situation.beat_index, 1); self.assertEqual(again.situation.beats_count, 1)
    def test_no_second_beat_before_the_interval(self):
        self.host.tick(); self.advance(minutes=14); self.assertEqual(self.host.tick().kind, WAIT)
        self.advance(minutes=1); self.assertEqual(self.host.tick(), Step(BEAT))
    def test_a_failing_beat_does_not_stop_the_loop_and_backs_off(self):
        self.fail_next(3)
        for _ in range(3): self.host.tick(); self.advance(minutes=15)
        self.assertEqual(self.host.situation.consecutive_failures, 3); self.assertEqual(self.host.status().note, "backoff")
        self.assertEqual(self.host.tick(), Step(WAIT, "backoff"))                        # 15 min after the third failure
        self.advance(minutes=15); self.assertEqual(self.host.tick(), Step(BEAT)); self.assertEqual(self.host.situation.consecutive_failures, 0)
    def test_history_and_debug_are_bounded(self): ...                                   # 15 beats -> len(history) == 12
    def test_location_survives_a_restart(self): ...                                     # fake sets context["jenbina_location"] = "Coupa Cafe"

class TestSleep(unittest.TestCase):
    def test_choosing_sleep_at_night_puts_her_to_sleep_and_stops_llm_work(self):
        self.now = datetime(2026, 11, 15, 23, 40); self.next_result(fell_asleep=True)
        self.host.tick(); self.assertEqual(self.host.situation.phase, ASLEEP)
        self.assertEqual(self.store.get_events()[-1]["kind"], "sleep")
        steps = self.live(hours=6)                                                       # 23:40 to 05:40, still night
        self.assertEqual(len(self.calls), 1)                                             # no beat ran while asleep
        self.assertEqual({s.kind for s in steps}, {WAIT, SLEEP_TICK})
        self.llm_json_mode.invoke.assert_not_called(); self.llm.invoke.assert_not_called()
    def test_sleep_recovers_twelve_points_an_hour_and_she_wakes_hungry(self):
        self.put_to_sleep(at=datetime(2026, 11, 15, 23, 0), sleep_need=20.0, hunger=80.0)
        self.live(hours=2)
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("sleep"), 44.0, delta=0.5)
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), 64.0, delta=3.5)
    def test_morning_wake_is_recorded_with_its_length(self):
        self.put_to_sleep(at=datetime(2026, 11, 15, 22, 20))
        steps = self.live(until=datetime(2026, 11, 16, 6, 0))
        self.assertEqual(steps[-1], Step(WAKE, "morning")); self.assertNotIn(WAKE, [s.kind for s in steps[:-1]])
        self.assertEqual(self.store.get_events()[-1]["title"], "Woke after 7h 40m"); self.assertEqual(self.host.situation.phase, AWAKE)
    def test_a_message_wakes_her_and_resleep_within_the_hour_is_the_same_sleep(self):
        start = datetime(2026, 11, 15, 23, 0); self.put_to_sleep(at=start); self.live(until=datetime(2026, 11, 16, 2, 10))
        with self.host.chat_turn(ANN) as turn: self.assertTrue(turn.woken)
        self.assertEqual(self.store.get_events()[-1]["title"], "Woken by a message after 3h 10m")
        self.assertIn("a message just woke me", self.host.person.working_memory.format_for_prompt())
        events_before = len(self.store.get_events())
        self.advance(minutes=20); self.next_result(fell_asleep=True); self.host.tick()
        self.assertEqual(self.host.situation.phase, ASLEEP); self.assertEqual(self.host.situation.phase_since, start)
        self.assertEqual(len([e for e in self.store.get_events()[events_before:] if e["kind"] == "sleep"]), 0)
    def test_a_greeting_never_wakes_her(self):
        self.put_to_sleep(at=datetime(2026, 11, 15, 23, 0))
        with self.host.greeting_turn(ANN) as turn: self.assertIsNone(turn)
        self.assertEqual(self.host.situation.phase, ASLEEP)

class TestLostTime(unittest.TestCase):
    def test_a_long_gap_is_noticed_and_costs_her_nothing(self):
        self.host.tick(); hunger = self.host.person.maslow_needs.get_need_satisfaction("hunger")
        self.advance(hours=5); self.host.tick()
        kinds = [e["kind"] for e in self.store.get_events()]; self.assertIn("gap", kinds)
        self.assertEqual([e for e in self.store.get_events() if e["kind"] == "gap"][0]["title"], "Was away for 5h 0m")
        self.assertAlmostEqual(self.host.person.maslow_needs.get_need_satisfaction("hunger"), hunger, delta=3.0)
        self.assertIn("I was away for 5h 0m", self.host.person.working_memory.format_for_prompt())
    def test_backoff_and_the_daily_cap_are_not_lost_time(self):
        self.host.situation.beats_day = self.now.date().isoformat(); self.host.situation.beats_count = 80
        self.live(hours=5)                                                               # the heart runs, no beat is allowed
        self.assertEqual(len(self.calls), 0)
        self.assertNotIn("gap", [e["kind"] for e in self.store.get_events()])
    def test_gap_on_restart_is_measured_from_the_last_pulse(self):
        self.host.pulse(); self.host.stop(); self.advance(hours=2)
        again = make_host(); again.start(threads=False); again.tick()
        self.assertIn("gap", [e["kind"] for e in self.store.get_events()])
    def test_asleep_through_a_gap_longer_than_nine_hours_wakes_her(self): ...

class TestTurnsAndStepOnce(unittest.TestCase):
    def test_chat_holds_her_attention(self):
        self.host.tick(); self.advance(minutes=20)
        with self.host.chat_turn(ANN) as turn: self.assertEqual((turn.person_key, turn.user_id, turn.woken), ("Ann", 1, False))
        self.assertEqual(self.host.tick(), Step(WAIT, "attention"))
        self.advance(minutes=3); self.assertEqual(self.host.tick(), Step(BEAT))
    def test_chat_turn_carries_the_last_beat(self): ...                                 # last_responses["action_decision"], history
    def test_greeting_turn_yields_none_while_the_mind_is_busy(self):                     # hold host.lock in another thread via threading.Event, no sleep
    def test_step_once_ignores_the_interval_but_not_the_cap_or_sleep(self):
        self.host.tick(); self.assertEqual(self.host.step_once(), "done"); self.assertEqual(len(self.calls), 2)
        self.host.situation.beats_count = 80; self.assertEqual(self.host.step_once(), "daily_cap")
        self.put_to_sleep(at=self.now); self.assertEqual(self.host.step_once(), "asleep")
    def test_proactive_target_is_offered_to_the_beat(self): ...                          # ctx["proactive_target"] == (1, "Ann") after a recent chat

class TestUnreadableState(unittest.TestCase):                                            # Review Focus 4
    def test_corrupt_person_state_stops_the_host_and_is_not_overwritten(self):
        self.store.save_state("{broken", {}); host = make_host()
        with self.assertRaises(BeingStateError): host.start(threads=False)
        self.assertEqual(self.store.load_state()[0], "{broken")
    def test_old_situation_without_new_fields_loads_with_defaults(self):
        self.store.save_state(Person().serialize(), {"location": "Coupa Cafe"})
        host = make_host(); self.assertTrue(host.start(threads=False))
        self.assertEqual((host.situation.location, host.situation.phase), ("Coupa Cafe", "awake"))
```

- [ ] **Step 2: Run** `$PY -m pytest tests/test_heartbeat_host.py -q`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement** `core/heartbeat/host.py`. Keep the thread loops to a few lines each (`while not self._stop.wait(period): self.tick()`), so everything else is reachable from `tick()` and `pulse()` without threads.
- [ ] **Step 4: Run** the same command, then the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: add the host that owns Jenbina and keeps her heart beating`.

---

### Task 7: Standalone runner

**Files:**
- Create: `run_heartbeat.py`
- Delete: `run_scheduler.py`
- Modify: `requirements.txt` (remove `apscheduler>=3.10.0`)
- Test: `tests/test_run_heartbeat.py`

**Interfaces:**
- Consumes: `JenbinaHost` (Task 6).
- Produces: `run_heartbeat.main(argv: list[str] | None = None, host_factory: Callable[..., JenbinaHost] | None = None) -> int`. `main` obtains the host with `host_factory(adopt_user_id=args.adopt_user_id)`; the default factory, `build_host(adopt_user_id: int | None = None) -> JenbinaHost`, is the only place that builds the store, the database and the LLMs, so a test that injects a factory needs no API key. Options: `--adopt-user-id N` (passed to the host as `adopt_user_id`), `--list-users` (print the users table as `run_scheduler.py` did, return 0), `--once` (`start(threads=False)`, `step_once()`, `stop()`, return 0). Without `--once`: `start(threads=False)` then `run_forever()`, with `SIGINT` and `SIGTERM` calling `stop()`. When `start` returns `False`, print `Jenbina is already living in another process (<holder>).` to stderr and return 1. The module keeps `run_scheduler.py`'s preamble (`sys.path`, `load_dotenv`, the `LANGSMITH_*` variables) and builds the LLMs the way `core/ui/shared_init.py:init_llm` does, plus `insight_llm = get_llm(provider="openai-advanced", temperature=0.8, max_tokens=500)`.

- [ ] **Step 1: Write the failing tests**

```python
def test_exits_1_when_she_lives_elsewhere(self):
    host = MagicMock(); host.start.return_value = False; host.status.return_value.holder = "other:1:zz"
    self.assertEqual(main(["--once"], host_factory=lambda **kw: host), 1); host.step_once.assert_not_called()
def test_once_beats_once_and_stops(self):
    host = MagicMock(); host.start.return_value = True
    self.assertEqual(main(["--once"], host_factory=lambda **kw: host), 0)
    host.step_once.assert_called_once(); host.stop.assert_called_once(); host.run_forever.assert_not_called()
def test_adopt_user_id_reaches_the_host(self):
    seen = {}; main(["--once", "--adopt-user-id", "3"], host_factory=lambda **kw: seen.update(kw) or MagicMock())
    self.assertEqual(seen["adopt_user_id"], 3)
def test_scheduler_is_gone(self):
    self.assertFalse(os.path.exists(os.path.join(ROOT, "run_scheduler.py")))
    self.assertNotIn("apscheduler", open(os.path.join(ROOT, "requirements.txt")).read())
```

- [ ] **Step 2: Run** `$PY -m pytest tests/test_run_heartbeat.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** `run_heartbeat.py`, delete `run_scheduler.py`, remove the requirement.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: replace the 5-hour scheduler with run_heartbeat.py`.

---

### Task 8: Chat on the shared being, and the privacy rule

**Files:**
- Modify: `core/ui/chat.py`, `core/interaction/chat_handler.py` (no prompt change expected; fix anything the privacy test finds)
- Test: `tests/test_privacy.py` (new), `tests/test_chat_ui.py`, `tests/test_greeting_generation.py`

**Interfaces:**
- Consumes: `ChatTurn`, `JenbinaHost.greeting_turn` (Task 6); `Person.get_current_state(partner=...)`, `PersonModel.last_visit_time` (Task 3).
- Produces, in `core/ui/chat.py`:
  - `handle_user_input(person, llm, memory_manager, debug_mode, user_input, turn: ChatTurn)`. It uses `turn.person_key` wherever it used `_get_user_display_name()`, `turn.user_id` for SQLite and Chroma scoping, `turn.last_responses` for `needs_response`, `world_description`, `action_decision`, `state_response`, `turn.history` for `history_context`, `person.get_current_state(partner=turn.person_key)` for `person_state`, and `record_mood(turn.event_log, ...)`. The SQLite `sender` for the user's message stays the account's display name. It no longer saves; the host does when the turn ends.
  - `check_return_greeting(person, llm, person_key: str, now: datetime | None = None) -> str | None`: the same rules as today, reading and writing `person.social_cognition.get_or_create_model(person_key).last_visit_time` instead of `person.last_visit_time`.
  - `ensure_greeting(host, user: dict, llm) -> None`, replacing `ensure_outreach`: returns at once when the session already showed a greeting; opens `host.greeting_turn(user)`; a `None` turn means "try again on a later rerun" (the session flag is left unset); otherwise calls `check_return_greeting` and stores a greeting with `person.send_message(turn.person_key, greeting, "greeting")`.
  - Removed in this task: `ensure_outreach`. `check_proactive_message`, `send_proactive_message` and `get_event_log` stay until Task 9, because the UI iteration copy that Task 9 deletes still imports them.
  - `core/app.py` still calls the old `ensure_outreach` and the old `handle_user_input` after this task and is rewired in Task 9. No unit test imports `core/app.py`, so the suite passes, but the app does not run between these two commits: do Task 9 straight after this one.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_privacy.py
SECRETS = ["ANN-MESSAGE-TEXT", "ANN-BELIEF", "ANN-DOSSIER-FACT"]

def two_people():
    p = Person(); p.init_social_cognition(); p.init_self_narrative(); p.init_curiosity_system(); p.init_social_interaction_tracker()
    p.receive_message("Ann", "ANN-MESSAGE-TEXT"); p.send_message("Ann", "reply to ANN-MESSAGE-TEXT")
    ann = p.social_cognition.get_or_create_model("Ann"); ann.beliefs.append("ANN-BELIEF"); ann.user_dossier = {"job": "ANN-DOSSIER-FACT"}
    p.social_interaction_tracker.record_chat("Ann", "warm")
    p.receive_message("Bob", "hello from Bob"); p.social_cognition.get_or_create_model("Bob").user_dossier = {"job": "baker"}
    return p

class CapturingLLM:                      # .invoke(messages) records every message's content, returns an object with .content = "ok"
    ...

class TestNothingCrossesBetweenPeople(unittest.TestCase):
    def assert_clean(self, llm):
        sent = "\n".join(llm.prompts); self.assertTrue(sent)
        for secret in SECRETS: self.assertNotIn(secret, sent)

    def test_chat_reply_and_insight_prompts(self):
        p = two_people(); llm = CapturingLLM(); p.init_insight_system(llm)
        handle_chat_interaction(st=MagicMock(), llm=llm, needs_response={}, world_description="{}", action_decision={},
                                user_input="what did you do today?", person_state=p.get_current_state(partner="Bob"),
                                conversation_context="Bob: hello from Bob", memory_manager=None, user_id=2, person=p,
                                conversation_partner_name="Bob")
        self.assert_clean(llm)
        self.assertIn("Ann", "\n".join(llm.prompts))          # she may know that she knows Ann, and the tone of the day

    def test_second_message_subtle_insight_prompt(self): ...   # first impression already delivered for Bob; same assertion
    def test_greeting_prompts(self):                           # generate_return_greeting(p, llm, 30.0, "Bob") and generate_first_greeting(p, llm, "Bob")
    def test_proactive_prompt(self):                           # generate_proactive_message(p, llm, {"low_social": {"need": "friendship", "satisfaction": 20}}, display_name="Bob")
    def test_unfiltered_state_would_leak(self):                # guards the test itself
        self.assertIn("ANN-BELIEF", json.dumps(two_people().social_cognition.get_stats(), default=str))

# tests/test_chat_ui.py
def test_chat_passes_only_the_partners_state_and_the_last_beat(self, st, chat, _emotion):
    turn = ChatTurn("Bob", 2, False, {"action_decision": {"chosen_action": "Read"}}, [], MagicMock())
    handle_user_input(person, None, None, False, "hi", turn)
    kwargs = chat.call_args.kwargs
    self.assertEqual((kwargs["conversation_partner_name"], kwargs["user_id"]), ("Bob", 2))
    self.assertEqual(kwargs["action_decision"], {"chosen_action": "Read"})
    self.assertNotIn("ANN-BELIEF", json.dumps(kwargs["person_state"], default=str))
def test_chat_mood_event_goes_to_the_shared_log_without_names(self): ...   # event title has no "Bob" and no message text
def test_greeting_waits_when_the_mind_is_busy(self):          # host.greeting_turn yields None -> nothing sent, session flag still unset
def test_greeting_is_stored_with_greeting_type_under_the_persons_key(self): ...

# tests/test_greeting_generation.py: TestCheckReturnGreetingIntegration updated to the new signature
def test_last_visit_is_per_person(self):
    check_return_greeting(person, None, "Ann", now=T); self.assertEqual(person.social_cognition.get_or_create_model("Ann").last_visit_time, T)
    self.assertIsNone(person.social_cognition.get_or_create_model("Bob").last_visit_time)
```

- [ ] **Step 2: Run** `$PY -m pytest tests/test_privacy.py tests/test_chat_ui.py tests/test_greeting_generation.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** the `core/ui/chat.py` changes. If any privacy test still finds a secret in a prompt, fix the source of that value in `core/interaction/chat_handler.py` so only the current partner's content reaches it, and say so in the commit message. In `core/ui/__init__.py` replace the `ensure_outreach` export with `ensure_greeting` (and update the name in `tests/test_ui_exports.py`) so the package still imports.
- [ ] **Step 4: Run** the full suite. Expected: PASS.
- [ ] **Step 5: Commit** `feat: chat on the shared Jenbina with per-person privacy`.

---

### Task 9: The home screen

**Files:**
- Create: `core/ui/admin.py`, `core/ui/live.py`
- Modify: `core/ui/shared_init.py`, `core/app.py`, `core/ui/rail.py`, `core/ui/simulation.py`, `core/ui/chat.py`, `core/ui/__init__.py`, `core/pages/3_🌍_Environment.py`, `core/pages/5_🔧_Debug_Info.py`, `core/pages/6_🔑_Admin.py`
- Test: `tests/test_rail.py`, `tests/test_ui_exports.py`, `tests/test_simulation_runner.py`, `tests/test_live.py` (new)

**Interfaces:**
- Consumes: `JenbinaHost`, `HeartStatus` (Task 6); `handle_user_input(..., turn)`, `ensure_greeting` (Task 8).
- Produces:
  - `core/ui/admin.py`: `ADMIN_EMAIL`, `is_local_request() -> bool`, `is_admin() -> bool`, moved unchanged from the Admin page, which now imports them.
  - `core/ui/live.py`: `REFRESH_SECONDS = 5`; `draw_guarded(draw: Callable[[], None]) -> bool`: calls `draw()`, returns `True`; on any exception prints it, shows `st.caption("…")` and returns `False`.
  - `core/ui/shared_init.py`: `get_host() -> JenbinaHost` (a `@st.cache_resource` singleton built with `BeingStore()`, `UserDatabase()`, `init_llm()` and the insight LLM; `get_host` calls `host.start()` whenever `host.hosting` is false). `require_auth()` after authentication: get the host; when it is not hosting show `st.info("Jenbina is already living in another process. This window cannot reach her until that one stops.")` and return `False`; otherwise set `st.session_state.person = host.person` and `st.session_state.meta_cognitive_system = host.meta_cognitive_system` on every run (references, never copies). `save_person_state()` becomes `get_host().save()`. `_load_or_create_person` and the person-building half of `init_session_state` are deleted, along with its initialisation of `simulation_completed`, `needs_response`, `world_description`, `action_decision`, `state_response`, `simulation_history` and `is_running`; `action_history`, `memory_manager`, `environment_simulator` and `showed_return_greeting` stay. The user-research thread keeps its behaviour but writes the dossier to `host.person.social_cognition.get_or_create_model(host.person_key(user))` and saves inside `with host.lock:`.
  - `core/ui/rail.py`: `heartbeat_lines(status: HeartStatus, now: datetime) -> list[str]` and `render_heartbeat_card(status: HeartStatus, admin: bool, now: datetime | None = None) -> bool` (returns whether "Step once" was clicked). `render_run_controls` is deleted.
  - `core/ui/simulation.py`: `run_single_iteration`, `run_simulation_loop`, `_now_hhmm`, `get_person_dict`, `_print_json`, `_detect_location_from_action` and every import only they used are deleted. The renderers stay.
  - `core/ui/chat.py`: `check_proactive_message`, `send_proactive_message`, `get_event_log` and the `save_person_state` import are deleted, with their tests in `tests/test_chat_ui.py` (`test_proactive_is_stored_with_proactive_type`, `TestEventLogPerUser`, `test_proactive_message_reads_runner_history_records`).
  - `core/ui/__init__.py`: exports become `render_full_sidebar, inject_pixel_css, render_status_rail, render_heartbeat_card, render_mind_card, build_timeline, render_timeline, handle_user_input, ensure_greeting, require_auth, init_llm, init_session_state, save_person_state, get_host`.

`heartbeat_lines` (wording fixed by the spec's sketch for the first two lines):
- line 1: `"● awake · since 07:12"` or `"● asleep · since 23:40"` (`phase_since` as `%H:%M`).
- line 2 while awake: `"last moment 4 min ago · next in 11 min"`; `"no moment yet · next in 0 min"` before the first beat; the `· next in …` part is dropped when `next_beat_at` is `None`. While asleep there is no line 2.
- a further line `"daily limit reached · resting until tomorrow"` when `note == "daily_cap"`, or `"heart is retrying after errors"` when `note == "backoff"`.
- when `status.busy`, line 2 is replaced by the stage text (`status.stage`).

`render_heartbeat_card`: a bordered card titled `Heartbeat` with those lines; for admins only, a primary button labelled exactly `Step once`, `disabled=status.phase == "asleep" or status.note == "daily_cap"`.

`core/app.py` layout (what each part does; the builder writes the code):
- After `require_auth()`: `host = get_host()`, `user = st.session_state.current_user`, `person = host.person`, `person_key = host.person_key(user)`. Call `ensure_greeting(host, user, llm)`.
- Left column: a fragment `@st.fragment(run_every=REFRESH_SECONDS)` that draws the filter radio and the timeline container through `draw_guarded`: `build_timeline(person.get_conversation_history(person_key, count=MESSAGE_WINDOW), host.event_log.recent(TIMELINE_LIMIT), person.name, filter_name)`. Below the fragment and outside it: a `live` container, then `st.chat_input("Talk to Jenbina...")`. The chat input must stay outside the fragment so a refresh never clears what someone is typing.
- Right column: a second fragment with the same `run_every`, drawing through `draw_guarded`: `render_status_rail(person, world_summary, doing, goal)` where `world_summary` and `doing` come from `host.situation.history[-1]` (as `_latest_world` reads a record today); the stage pill shows `host.status().stage`; the portrait is `jenbina_sleep.png` while `host.situation.phase == "asleep"`; then `render_heartbeat_card(host.status(), is_admin())`; then `render_mind_card(person, person_key)`. When the card returns `True`: `host.step_once()` inside `st.spinner("Jenbina is living a moment…")`, then `st.rerun()`.
- A submitted message: if `host.status().busy`, show the stage pill text `"finishing what she was doing…"` first. Then `with host.chat_turn(user) as turn:` and, inside `with live:`, `handle_user_input(person, llm, memory_manager, False, user_input, turn)`. Then `st.rerun()`.
- Gone: `simulation_auto_started`, `render_run_controls`, `run_simulation_loop`, every `save_person_state()` call, `_latest_world`'s use of session state, `get_event_log`.

Pages: `3_🌍_Environment.py` keeps reading `st.session_state.person` (now the host's). `5_🔧_Debug_Info.py` reads `get_host().debug_iterations`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_rail.py  (TestControlsAndMind.test_run_controls_keys_and_labels is replaced)
NOW = datetime(2026, 11, 15, 7, 23)
def status(**kw):
    base = dict(hosting=True, holder=None, phase="awake", phase_since=datetime(2026, 11, 15, 7, 12),
                last_beat_at=NOW - timedelta(minutes=4), next_beat_at=NOW + timedelta(minutes=11), note="", busy=False, stage="idle")
    base.update(kw); return HeartStatus(**base)

def test_heartbeat_lines_awake(self):
    self.assertEqual(heartbeat_lines(status(), NOW), ["● awake · since 07:12", "last moment 4 min ago · next in 11 min"])
def test_heartbeat_lines_asleep(self):
    self.assertEqual(heartbeat_lines(status(phase="asleep", phase_since=datetime(2026, 11, 14, 23, 40), next_beat_at=None), NOW),
                     ["● asleep · since 23:40"])
def test_heartbeat_lines_notes(self):
    self.assertIn("daily limit reached · resting until tomorrow", heartbeat_lines(status(note="daily_cap", next_beat_at=None), NOW))
    self.assertIn("heart is retrying after errors", heartbeat_lines(status(note="backoff"), NOW))
    self.assertEqual(heartbeat_lines(status(busy=True, stage="deciding…"), NOW)[1], "deciding…")
    self.assertEqual(heartbeat_lines(status(last_beat_at=None, next_beat_at=NOW), NOW)[1], "no moment yet · next in 0 min")
def test_step_once_is_for_admins_and_disabled_while_asleep(self):
    with patch("core.ui.rail.st") as st:
        st.button.return_value = False
        render_heartbeat_card(status(), admin=False, now=NOW); st.button.assert_not_called()
        render_heartbeat_card(status(), admin=True, now=NOW)
        self.assertEqual(st.button.call_args.args[0], "Step once"); self.assertFalse(st.button.call_args.kwargs["disabled"])
        render_heartbeat_card(status(phase="asleep"), admin=True, now=NOW); self.assertTrue(st.button.call_args.kwargs["disabled"])
        render_heartbeat_card(status(note="daily_cap"), admin=True, now=NOW); self.assertTrue(st.button.call_args.kwargs["disabled"])

# tests/test_live.py                                                        # Review Focus 5
def test_a_failing_draw_shows_no_traceback(self):
    with patch("core.ui.live.st") as st:
        self.assertFalse(draw_guarded(lambda: {}["missing"])); st.caption.assert_called_once(); st.exception.assert_not_called()
        self.assertTrue(draw_guarded(lambda: None))

# tests/test_ui_exports.py
def test_home_screen_building_blocks_are_exported(self):                   # the list above; and these are NOT exported:
    for gone in ("run_single_iteration", "run_simulation_loop", "render_run_controls", "ensure_outreach", "get_event_log"):
        self.assertFalse(hasattr(core.ui, gone))
def test_nothing_makes_her_act_on_page_open(self):
    app = open(os.path.join(ROOT, "core", "app.py")).read()
    for gone in ("simulation_auto_started", "run_simulation_loop", "render_run_controls", "Run N"): self.assertNotIn(gone, app)
    self.assertIn("st.fragment", app); self.assertIn("chat_turn", app)
def test_heartbeat_package_has_no_streamlit(self):
    for name in os.listdir(os.path.join(ROOT, "core", "heartbeat")):
        if name.endswith(".py"): self.assertNotIn("streamlit", open(os.path.join(ROOT, "core", "heartbeat", name)).read())
```

In `tests/test_simulation_runner.py`, delete `TestUiRunnerEvents`, `test_ui_runner_records_plan_finished_once_and_goal_advanced`, `test_ui_runner_applies_the_shared_matcher` and the parts of `build_env` only they used; the headless tests stay.

- [ ] **Step 2: Run** `$PY -m pytest tests/test_rail.py tests/test_live.py tests/test_ui_exports.py tests/test_simulation_runner.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** the files as specified.
- [ ] **Step 4: Run** the full suite, then check the app imports: `cd core && JENBINA_SKIP_AUTH=1 $PY -c "import ast,sys; ast.parse(open('app.py').read())"` and `$PY -c "import core.ui, core.heartbeat.host"` from the repository root. Expected: PASS, no output.
- [ ] **Step 5: Commit** `feat: home screen shows her living; remove the run controls and the UI iteration copy`.

---

### Task 10: End-to-end tests, docs, final check

**Files:**
- Modify: `tests/e2e/conftest.py`, `tests/e2e/test_simulation.py`, `tests/e2e/test_feedback_loop.py`, `CLAUDE.md`, `.env.example`, `tests/README.md` if it mentions the run controls

**Interfaces:**
- Consumes: the home screen from Task 9.

- [ ] **Step 1: Update the end-to-end tests.** In `conftest.py`, the server's environment gains `JENBINA_DISABLE_SLEEP=1` (a run at night must not put her to sleep between two "Step once" clicks) and a temporary `JENBINA_DATA_DIR` if it does not set one already. In both test files, replace every wait on `text=completed in` with a wait for one more action row than before the click: count `page.locator(".px-event-action")` before clicking "Step once", then `expect(page.locator(".px-event-action")).to_have_count(n + 1, timeout=...)` with the timeout those tests already use. Leave the "Step once" button lookups as they are (the tests run locally, so the button is shown).
- [ ] **Step 2: Check they still collect:** `$PY -m pytest tests/e2e --collect-only -q`. Expected: the same tests listed, no errors. (They need a browser and an API key to run; do not run them.)
- [ ] **Step 3: Update `CLAUDE.md`:** the repository tree (add `core/heartbeat/` with its six modules, `core/ui/admin.py`, `core/ui/live.py`, `run_heartbeat.py`; remove `run_scheduler.py` if listed); the `core/ui/rail.py` line ("Now card, heartbeat card, mind card"); Common Commands (add `python run_heartbeat.py`, `--once`, `--adopt-user-id`); Environment Variables (`JENBINA_BEAT_MINUTES`, `JENBINA_MAX_BEATS_PER_DAY`, `JENBINA_LLM_TIMEOUT_SECONDS`, `JENBINA_DISABLE_SLEEP`); the "Streamlit State" consideration (the live `Person` belongs to the host in `core/heartbeat/host.py`; `st.session_state.person` is a reference to it; change her only inside `host.chat_turn` or a beat); and two rows in the plans table for `2026-11-15-heartbeat-design.md` and `2026-11-15-heartbeat-implementation.md`. Add the four variables to `.env.example` as commented lines with their defaults.
- [ ] **Step 4: Final verification.** Run `$PY -m pytest tests/test_*.py -q` (expected: all pass, no test skipped that passed before), then `grep -rn "run_scheduler\|apscheduler\|simulation_auto_started\|render_run_controls\|run_simulation_loop" core tests run_heartbeat.py requirements.txt` (expected: only the assertions in `tests/test_ui_exports.py` and `tests/test_run_heartbeat.py` that these are gone), then `graphify update .`.
- [ ] **Step 5: Commit** `docs: describe the heartbeat; update end-to-end tests for the self-running home screen`.

---

## Decisions this plan makes inside the spec's "left to the builder"

- Per-person keys live in a `being_people` table and are fixed at first sight; on a name collision the key is `Name (2)`, `Name (3)` and so on. No part of an email address is used.
- The lease is renewed by its own pulse thread so a long beat cannot let it go stale, and a dead holder on the same machine is replaced at once.
- A beat attempt counts toward the daily cap whether or not it succeeds.
- After a message wakes her, going back to sleep within the hour records no event, and the eventual wake reports the length from the original start. The timeline therefore reads: fell asleep, woken by a message, woke after N hours.
- `JENBINA_DISABLE_SLEEP=1` exists for the end-to-end tests and for anyone who wants her awake around the clock.
- Her first beat happens within seconds of the heart starting, rather than one interval later.

## Changes made after the tasks, from review

A second review, of Tasks 4 to 10, changed these points. Where they differ from the task text above, this section is what the code does.

- **One host per process, whatever Streamlit does.** `get_host()` uses `process_host()` in `core/heartbeat/host.py`, which keeps the host on `sys`, not `st.cache_resource`. Clearing Streamlit's cache or hot-reloading `shared_init` no longer builds a second host that can never take the lease.
- **`start()` is serialized** by its own lock, so two tabs reconnecting at once cannot stop the threads one of them just started.
- **Adoption never picks the end-to-end test login by itself.** Accounts with provider `test` are adopted only when named (`--adopt-user-id`, or `JENBINA_ADOPT_USER_ID` for the app) or when no other account has a readable state. An account whose history cannot be read is skipped and reported in `AdoptionReport.failed_user_ids` instead of stopping her first start.
- **Admin by "local request" only in development.** `is_admin()` trusts a local-looking Host header only when `JENBINA_SKIP_AUTH=1`; with login on, only the admin account. The header match is exact, not a substring.
- **Thoughts name nobody.** The social-day line fed to the inner monologue leaves out names (`format_for_prompt(names=False)`), because thoughts are recorded on the timeline every account sees. Chat prompts still get the names.
- **Home screen.** A message sent during a beat shows a notice in the conversation while it waits; the place line shows where she is now, not where the last beat started; `chat_turn` raises `NotHostingError`, which the page turns into a plain notice.
- **Host.** Lost time is not counted as time awake; an adopted Jenbina's clocks start at adoption; a storage error while renewing the lease does not stop the heart; `stop(patience=...)` lets process exit abandon a beat in flight.
- **`run_heartbeat.py --once`** prints what happened and exits 2 when the beat failed.
- **Greeting** is considered once per session (the 5-second refresh must not re-check it), and a message counts as a visit.

