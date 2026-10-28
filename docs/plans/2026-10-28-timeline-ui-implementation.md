# Timeline UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task (superpowers:subagent-driven-development is the alternative when a fresh subagent per task is wanted). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Simulation and Chat pages with one home screen: a chat timeline that interleaves the conversation with Jenbina's persisted life events, beside a live status rail with her state, the run controls and her mind.

**Architecture:** A new Streamlit-free package `core/timeline/` defines the event vocabulary, the title builders, an `EventLog` over a new `events` table in `users.db`, and recording helpers that both the Streamlit runner and the headless runner call. The UI layer gets two new modules, `core/ui/timeline.py` (merge messages and events, render rows) and `core/ui/rail.py` (the status rail, run controls and mind card). The runner in `core/ui/simulation.py` stops rendering the page and instead updates rail placeholders and records events; `core/app.py` lays out the two columns. The Chat page and every renderer that only served the old layout are deleted.

**Tech Stack:** Python 3.10+, Streamlit 1.38.0 (pinned), SQLite via `sqlite3`, Pillow for the sprite builder, `unittest` + `pytest`, Playwright for e2e.

**Spec:** `docs/plans/2026-10-28-timeline-ui-redesign.md`

## Global Constraints

- Streamlit is pinned to `1.38.0`; run the app and every test with the project venv (`.venv/bin/python` at the repository root; from the worktree `../../../.venv/bin/python`). The system `python3` has a different Streamlit and must not be used.
- Unit tests need no LLM and no live database: `UserDatabase(db_path=<tempfile>)`, `EventLog()` in-memory, chain factories patched.
- No emoji in new markup; icons come from `icon_html` (8x8 sprites). Pixel vocabulary for new CSS: 3px `#1E1B3A` borders, hard 4px shadows, VT323 20px text, Press Start 2P 9–10px meta, no border radius, no gradients.
- The computation flow and LLM call order inside `run_single_iteration()` and `run_single_iteration_headless()` do not change.
- Every event's `created_at` is `datetime.now()` (local, naive) so it sorts with `Message.timestamp`.
- Event titles are computed when recorded; the renderer never derives wording from `detail`.
- After changing `core/ui/sprites/art.py`, run `python -m core.ui.sprites.build` and commit the regenerated PNGs; `python -m core.ui.sprites.build --check` must pass.
- The home screen always calls the chat flow with `debug_mode=False`.
- Conventional commit messages (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`), one commit per task.

## Review Focus

- A thought with no sentence punctuation ("maybe text someone") must render whole with no "more" details: Task 6 `test_first_sentence_without_punctuation_is_whole_text`.
- An event and a message recorded in the same microsecond must keep a deterministic order (event first): Task 6 `test_equal_timestamps_put_event_before_message`.
- A corrupted `detail_json` row must still render its title: Task 1 `test_bad_detail_json_becomes_empty_dict`, Task 6 `test_unknown_kind_renders_title`.
- A 300-character action with no spaces must still get a 90-character title: Task 2 `test_shorten_without_spaces_cuts_hard`.
- A database write failure mid-iteration must not abort the iteration: Task 2 `test_record_swallows_storage_errors`, Task 9 `test_iteration_survives_event_log_failure`.

---

### Task 1: Events table in UserDatabase

**Files:**
- Modify: `core/auth/user_db.py:30-70` (`_create_tables`), add methods after `get_messages` (line 179)
- Test: `tests/test_user_db.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `UserDatabase.store_event(user_id: int, kind: str, title: str, detail: dict | None = None, created_at: datetime | None = None) -> int` (row id) and `UserDatabase.get_events(user_id: int, limit: int = 200) -> list[dict]` oldest first, each dict `{"id": int, "kind": str, "title": str, "detail": dict, "created_at": datetime}`.

- [ ] **Step 1: Write the failing tests**

Add `class TestEvents(unittest.TestCase)` to `tests/test_user_db.py` with the same `setUp`/`tearDown` as `TestUserDatabase` plus `self.uid = self.db.create_or_update_user(firebase_uid="u1", email="a@b.c", display_name="A", photo_url="", provider="test")["id"]`.

```python
def test_events_table_created(self):
    names = [r["name"] for r in self.db._get_conn().execute("SELECT name FROM sqlite_master WHERE type='table'")]
    self.assertIn("events", names)

def test_store_and_get_round_trip(self):
    when = datetime(2026, 10, 27, 23, 41, 5, 123456)
    row_id = self.db.store_event(self.uid, "action", "Jenbina decided to nap", {"a": 1}, created_at=when)
    [ev] = self.db.get_events(self.uid)
    self.assertEqual((ev["id"], ev["kind"], ev["title"], ev["detail"], ev["created_at"]), (row_id, "action", "Jenbina decided to nap", {"a": 1}, when))

def test_oldest_first_and_limit(self):
    for i in range(5):
        self.db.store_event(self.uid, "mood", f"m{i}", created_at=datetime(2026, 1, 1, 0, 0, i))
    self.assertEqual([e["title"] for e in self.db.get_events(self.uid, limit=3)], ["m2", "m3", "m4"])

def test_empty_detail_is_empty_dict(self):
    self.db.store_event(self.uid, "move", "Walked home")
    self.assertEqual(self.db.get_events(self.uid)[0]["detail"], {})

def test_bad_detail_json_becomes_empty_dict(self):
    conn = self.db._get_conn()
    conn.execute("INSERT INTO events (user_id, kind, title, detail_json, created_at) VALUES (?, 'goal', 'x', '{not json', ?)", (self.uid, datetime.now().isoformat()))
    conn.commit()
    self.assertEqual(self.db.get_events(self.uid)[0]["detail"], {})

def test_events_isolated_per_user(self):
    other = self.db.create_or_update_user(firebase_uid="u2", email="c@d.e", display_name="B", photo_url="", provider="test")["id"]
    self.db.store_event(self.uid, "mood", "mine")
    self.assertEqual(self.db.get_events(other), [])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_user_db.py::TestEvents -v`
Expected: FAIL with `AttributeError: 'UserDatabase' object has no attribute 'store_event'` (the table test fails on the missing table).

- [ ] **Step 3: Implement the table and the two methods in `core/auth/user_db.py`**

Add to the `executescript` in `_create_tables`:

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    detail_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id, created_at);
```

`store_event` writes `created_at=(created_at or datetime.now()).isoformat()` and `detail_json=json.dumps(detail) if detail else None`. `get_events` selects `ORDER BY created_at DESC, id DESC LIMIT ?`, reverses, parses `detail_json` with a `try/except (TypeError, ValueError)` that yields `{}`, and parses `created_at` with `datetime.fromisoformat`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_user_db.py -v`
Expected: all PASS (the existing classes included).

- [ ] **Step 5: Commit**

```bash
git add core/auth/user_db.py tests/test_user_db.py
git commit -m "feat(db): add a per-user events table for Jenbina's life events"
```

---

### Task 2: Event vocabulary, title builders and EventLog

**Files:**
- Create: `core/timeline/__init__.py`, `core/timeline/events.py`
- Test: `tests/test_timeline.py` (new)

**Interfaces:**
- Consumes: Task 1's `store_event` / `get_events`.
- Produces, in `core/timeline/events.py` (re-exported by `core/timeline/__init__.py`):
  - constants `THOUGHT = "thought"`, `ACTION = "action"`, `MOOD = "mood"`, `GOAL = "goal"`, `PLAN = "plan"`, `MOVE = "move"`, `KINDS = (THOUGHT, ACTION, MOOD, GOAL, PLAN, MOVE)`
  - `@dataclass class TimelineEvent: kind: str; title: str; detail: dict = field(default_factory=dict); created_at: datetime = field(default_factory=datetime.now); id: int | None = None`
  - `shorten(text: str, limit: int = 90) -> str`
  - `lessons_text(lessons) -> str`
  - `mood_changes(before: dict, after: dict, limit: int = 3) -> dict[str, tuple[float, float]]`
  - `make_thought(mode: str, text: str) -> TimelineEvent`
  - `make_action(action: str, reasoning: str, lessons, satisfaction_before: float, satisfaction_after: float, location: str, time_of_day: str, weather: str, temperature: float) -> TimelineEvent`
  - `make_mood(changes: dict, source: str) -> TimelineEvent | None`
  - `make_goal(event: str, description: str, progress: float) -> TimelineEvent`
  - `make_plan(event: str, goal: str, step: str) -> TimelineEvent`
  - `make_move(src: str, dst: str) -> TimelineEvent`
  - `class EventLog: __init__(self, user_db=None, user_id=None)`, `record(self, event: TimelineEvent) -> TimelineEvent`, `recent(self, limit: int = 200) -> list[TimelineEvent]`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_timeline.py` (unittest, `sys.path.append` like the other tests) with:

```python
class TestTitles(unittest.TestCase):
    def test_shorten_cuts_at_word_boundary_with_ellipsis(self):
        self.assertEqual(shorten("attend live music at coupa cafe tonight", 20), "attend live music…")
    def test_shorten_leaves_short_text_alone(self):
        self.assertEqual(shorten("nap", 90), "nap")
    def test_shorten_without_spaces_cuts_hard(self):
        self.assertEqual(len(shorten("x" * 300, 90)), 90)   # 89 chars + "…"
    def test_lessons_text_joins_lists(self):
        self.assertEqual(lessons_text(["a", "b"]), "a; b")
        self.assertEqual(lessons_text("solo"), "solo")
        self.assertEqual(lessons_text(None), "")
    def test_action_title(self):
        ev = make_action("Attend Live Music at Coupa Cafe", "r", [], 83.4, 85.1, "Jenbina's House", "night", "Clear skies", 15.1)
        self.assertEqual(ev.title, "Jenbina decided to attend live music at coupa cafe")
        self.assertEqual(ev.detail["satisfaction_after"], 85.1)
        self.assertEqual(ev.kind, "action")
    def test_mood_changes_keeps_top_three_above_one_point(self):
        changes = mood_changes({"trust": 40, "joy": 35, "fear": 10, "anger": 5, "surprise": 20}, {"trust": 44, "joy": 38, "fear": 10.5, "anger": 1, "surprise": 22})
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
        self.assertEqual((ev.title, ev.detail), ("Quiet tonight. Maybe text someone.", {"mode": "deliberation", "text": "Quiet tonight. Maybe text someone."}))

class TestEventLog(unittest.TestCase):
    # setUp: a UserDatabase on a NamedTemporaryFile (deleted in tearDown) and
    # self.uid from create_or_update_user, as in tests/test_user_db.py.
    def test_memory_log_round_trip_oldest_first(self):
        log = EventLog()
        log.record(make_move("a", "b")); log.record(make_move("b", "c"))
        self.assertEqual([e.title for e in log.recent()], ["Walked from a to b", "Walked from b to c"])
    def test_memory_log_limit_keeps_newest(self):
        log = EventLog()
        for i in range(5): log.record(make_goal("created", str(i), 0))
        self.assertEqual([e.detail["description"] for e in log.recent(2)], ["3", "4"])
    def test_db_log_persists_and_sets_id(self):   # UserDatabase on a tempfile, one user
        log = EventLog(self.db, self.uid)
        ev = log.record(make_move("a", "b"))
        self.assertIsNotNone(ev.id)
        again = EventLog(self.db, self.uid).recent()
        self.assertEqual((again[0].kind, again[0].title, again[0].detail), ("move", "Walked from a to b", {"from": "a", "to": "b"}))
    def test_record_swallows_storage_errors(self):
        db = MagicMock(); db.store_event.side_effect = RuntimeError("disk")
        ev = EventLog(db, 1).record(make_move("a", "b"))
        self.assertEqual(ev.title, "Walked from a to b")   # no exception
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.timeline'`.

- [ ] **Step 3: Implement `core/timeline/events.py` and the package `__init__.py`**

Rules the tests pin: `shorten` cuts at the last space at or before `limit - 1` characters and appends `…`, falling back to a hard cut when there is no space; `mood_changes` keeps keys present in both dicts with `abs(after - before) >= 1`, sorted by absolute delta descending, first `limit`; `make_mood` returns `None` for empty changes, uses "lifted" when the sum of deltas is positive and "dipped" otherwise, formats values with `:.0f`; `make_action` lower-cases the action before `shorten(…, 90)` and stores `lessons` as a list (a string becomes a one-element list); `EventLog.record` calls `user_db.store_event(user_id, kind, title, detail, created_at)` when both `user_db` and `user_id` are set, prints and continues on any exception, otherwise appends to an in-memory list; `recent` maps `get_events` rows to `TimelineEvent`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/timeline tests/test_timeline.py
git commit -m "feat(timeline): add the event vocabulary, title builders and EventLog"
```

---

### Task 3: Recording helpers shared by both runners

**Files:**
- Create: `core/timeline/recording.py`
- Modify: `core/timeline/__init__.py` (re-export)
- Test: `tests/test_timeline.py`

**Interfaces:**
- Consumes: Task 2.
- Produces, in `core/timeline/recording.py`:
  - `record_thought(log, inner_monologue) -> TimelineEvent | None` (uses `inner_monologue.get_current_thought()`, which has `.content` and `.mode`; `None` when the system or the thought is missing)
  - `record_move(log, old_location: str, new_location: str | None) -> TimelineEvent | None` (`None` when equal or empty)
  - `record_action(log, action_response: dict, satisfaction_before: float, satisfaction_after: float, world_summary: dict) -> TimelineEvent` (reads `chosen_action`, `reasoning`, `lessons_applied`; `world_summary["location"]["name"]`, `["time"]["time_of_day"]`, `["weather"]["description"]`, `["weather"]["temperature"]`, each defaulting to `""`/`0`)
  - `record_mood(log, emotions_before: dict, emotions_after: dict, source: str) -> TimelineEvent | None`
  - `snapshot_goals(goal_system) -> dict[str, tuple[str, float]]` mapping `goal.description -> (goal.status, goal.progress)`; `{}` when `goal_system` is `None`
  - `record_goal_changes(log, before: dict, after: dict) -> list[TimelineEvent]`: `created` for keys new in `after`; `completed` when status became `"completed"`; `advanced` when status is still `"active"` and progress grew by at least `0.01`
  - `record_plan_step(log, step_result: str | None, goal_description: str, step_description: str) -> TimelineEvent | None` (`"step_completed"` → `step_completed`, `"step_overridden"` → `overridden`, else `None`)
  - `record_replan(log, plan) -> TimelineEvent | None` (plan has `.goal_description` and `.steps[0].description`)
  - `record_plan_finished(log, plan) -> TimelineEvent`

- [ ] **Step 1: Write the failing tests**

Add `class TestRecording(unittest.TestCase)` to `tests/test_timeline.py`, using `SimpleNamespace` fakes:

```python
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
    ws = {"location": {"name": "Jenbina's House"}, "time": {"time_of_day": "night"}, "weather": {"description": "Clear skies", "temperature": 15.1}}
    ev = record_action(self.log, {"chosen_action": "Nap", "reasoning": "tired", "lessons_applied": "rest early"}, 80.0, 82.5, ws)
    self.assertEqual(ev.detail["location"], "Jenbina's House")
    self.assertEqual(ev.detail["lessons"], ["rest early"])
    self.assertEqual(record_action(self.log, {"chosen_action": "Nap"}, 1, 2, {}).detail["location"], "")

def test_record_mood_none_when_unchanged(self):
    self.assertIsNone(record_mood(self.log, {"joy": 30}, {"joy": 30.4}, "chat"))
    self.assertEqual(record_mood(self.log, {"joy": 30}, {"joy": 35}, "chat").detail["source"], "chat")

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
```

(`self.log = EventLog()` in `setUp`; the order in `test_goal_changes` is: advanced/completed for keys in `before` in their original order, then created keys in `after` order.)

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py::TestRecording -v`
Expected: FAIL with `ImportError` on `record_thought`.

- [ ] **Step 3: Implement `core/timeline/recording.py`**

Every helper builds the event with a Task 2 `make_*` function and returns `log.record(event)`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/timeline tests/test_timeline.py
git commit -m "feat(timeline): add recording helpers for thoughts, actions, moods, goals and plans"
```

---

### Task 4: Return the insight text, not the prompt injection

**Files:**
- Modify: `core/interaction/chat_handler.py:390-445` (insight block) and `:497`
- Test: `tests/test_chat_handler.py:486-500` (`test_subtle_insight_injected`) and the first-impression test in the same class

**Interfaces:**
- Produces: `handle_chat_interaction(...)["insight"]` is the generated insight string or `None`.

- [ ] **Step 1: Extend the failing test**

In `test_subtle_insight_injected` add:

```python
self.assertEqual(result["insight"], "You seek control.")
self.assertNotIn("Lead with this observation", result["insight"])
```

Add the same two assertions (with that test's own insight string) to the first-impression test in `TestHandleChatInteraction` if one exists.

- [ ] **Step 2: Run the test to verify it fails**

Run: `../../../.venv/bin/python -m pytest tests/test_chat_handler.py::TestHandleChatInteraction::test_subtle_insight_injected -v`
Expected: FAIL on the `assertEqual` (the value starts with the injection wrapper).

- [ ] **Step 3: Fix `chat_handler.py`**

Introduce `insight_text = None` before the insight block, set it to `insight` in both modes where `insight_injection` is built, and return `"insight": insight_text`.

- [ ] **Step 4: Run the chat handler tests**

Run: `../../../.venv/bin/python -m pytest tests/test_chat_handler.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/interaction/chat_handler.py tests/test_chat_handler.py
git commit -m "fix(chat): return the generated insight instead of the prompt injection"
```

---

### Task 5: Pixel theme additions — wide shell, event rows, markers, badges, icons

**Files:**
- Modify: `core/ui/pixel_theme.py:80-87` (`inject_pixel_css`), add helpers after `dialog_html` (line 72), add CSS before the `/* ---- icons` block (line 708)
- Modify: `core/ui/sprites/art.py` (six new 8x8 icons), regenerate `assets/sprites/icons/*.png`
- Test: `tests/test_pixel_ui.py`, `tests/test_sprites.py` (existing checks cover the new icons)

**Interfaces:**
- Produces, in `core/ui/pixel_theme.py`:
  - `inject_pixel_css(wide: bool = False) -> None` — with `wide=True` the injected CSS also contains `.stApp .block-container { max-width: 64rem; }`
  - `EVENT_ICONS = {"thought": "thought", "action": "act", "mood": "mood", "goal": "esteem", "plan": "plan", "move": "walk"}`
  - `action_icon(action: str) -> str` — keyword map: eat/food/meal/snack/cook → `hunger`; drink/coffee/tea/water → `drink`; sleep/nap/rest → `sleep`; walk/stroll/visit/go to/wander/explore → `walk`; talk/chat/call/friend/social/music → `love`; read/study/learn/book → `self_actualization`; else `act`
  - `event_html(kind: str, title: str, meta: str = "", details: tuple[str, str] | None = None, badge: str | None = None, icon: str | None = None) -> str`
  - `delta_badge_html(before: float, after: float) -> str`
  - `marker_html(text: str) -> str`
  - `stage_pill_html(text: str) -> str`
- Produces six icon names in `ICONS`: `thought`, `act`, `mood`, `plan`, `walk`, `drink`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_pixel_ui.py`:

```python
class TestWideShell(unittest.TestCase):
    def test_wide_flag_widens_device(self):
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css(wide=True)
            self.assertIn("max-width: 64rem", "".join(c.args[0] for c in st.markdown.call_args_list))
        with patch("core.ui.pixel_theme.st") as st:
            inject_pixel_css()
            self.assertNotIn("64rem", "".join(c.args[0] for c in st.markdown.call_args_list))

class TestEventHtml(unittest.TestCase):
    def test_classes_icon_and_escaping(self):
        html_ = event_html("mood", "Mood <lifted>", meta="23:41")
        self.assertIn('class="px-event px-event-mood"', html_)
        self.assertIn("Mood &lt;lifted&gt;", html_)
        self.assertIn('alt="mood"', html_)
        self.assertIn('<span class="px-event-meta">23:41</span>', html_)
        self.assertNotIn("<details", html_)
    def test_details_badge_and_icon_override(self):
        html_ = event_html("action", "t", details=("why?", "a & b\nc"), badge="<b>B</b>", icon="hunger")
        self.assertIn("<summary>why?</summary>", html_)
        self.assertIn("a &amp; b<br>c", html_)
        self.assertIn("<b>B</b>", html_)
        self.assertIn('alt="hunger"', html_)
    def test_unknown_kind_uses_generic_icon_and_safe_class(self):
        html_ = event_html("we!rd", "t")
        self.assertIn('px-event-werd"', html_)
        self.assertIn('alt="act"', html_)
    def test_action_icon_keywords(self):
        self.assertEqual(action_icon("Eat breakfast"), "hunger")
        self.assertEqual(action_icon("Attend live music at Coupa"), "love")
        self.assertEqual(action_icon("Stroll University Avenue"), "walk")
        self.assertEqual(action_icon("Contemplate"), "act")

class TestDeltaBadge(unittest.TestCase):
    def test_text_attributes_and_sign_class(self):
        html_ = delta_badge_html(83.4, 85.1)
        self.assertIn("83% → 85% (+1.7%)", html_)
        self.assertIn('data-before="83.4"', html_); self.assertIn('data-after="85.1"', html_); self.assertIn('data-delta="1.7"', html_)
        self.assertIn("delta-positive", html_)
        self.assertIn("delta-negative", delta_badge_html(50, 48.2))
        self.assertIn("delta-neutral", delta_badge_html(50, 50))
        self.assertIn("(+0.0%)", delta_badge_html(50, 50))

class TestMarkerAndPill(unittest.TestCase):
    def test_marker_and_pill(self):
        self.assertEqual(marker_html("23:38 · <home>"), '<div class="px-marker">23:38 · &lt;home&gt;</div>')
        self.assertIn('class="px-stage"', stage_pill_html("thinking…"))
```

Add to `tests/test_sprites.py` an assertion that `set(["thought", "act", "mood", "plan", "walk", "drink"]) <= set(ICONS)`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_pixel_ui.py tests/test_sprites.py -v`
Expected: FAIL on the new imports and the icon-set assertion.

- [ ] **Step 3: Implement the helpers, the CSS and the icons**

`event_html` output shape (one line, escaped where noted):

```html
<div class="px-event px-event-{kind}">{icon_html}<span class="px-event-title">{title}</span>{badge}{meta span if meta}{details if given}</div>
```

`details` renders `<details><summary>{summary}</summary><div class="px-event-body">{body}</div></details>` with the body escaped and newlines turned into `<br>`. `kind` is reduced to `[a-z0-9_]` for the class. `delta_badge_html` rounds `after - before` to one decimal for the text and the `data-delta` value and picks the class from the sign of that rounded delta. CSS rules to add: `.px-event` (block, margin `10px 0`, padding `8px 12px`, background `#FFF6D5`, 3px border, `4px 4px 0 0 #1E1B3A` shadow, VT323 20px, flex-wrap row with 8px gap), `.px-event-title` (flex 1 1 auto), `.px-event-thought .px-event-title` (italic, color `#4A4670`), `.px-event-action::before` (the `.px-dialog-action` tail), `.px-event-meta` (chrome font 9px, color `#C2185B`, full width), `.px-event details` (full width), `.px-event summary` (chrome font 9px, cursor pointer), `.px-event-body` (margin-top 6px, color `#4A4670`), `.px-marker` (centered, chrome font 9px, color `#FFF6D5`, letter-spacing 1px, margin `14px 0 6px`), `.px-stage` (chrome font 9px, padding `6px 8px`, 3px border, background `#FFD93D`, hard 3px shadow). Draw `thought`, `act`, `mood`, `plan`, `walk`, `drink` as 8x8 strings in `art.py` in the shared palette, then run `../../../.venv/bin/python -m core.ui.sprites.build`.

- [ ] **Step 4: Run the tests and the asset check**

Run: `../../../.venv/bin/python -m pytest tests/test_pixel_ui.py tests/test_sprites.py -v && ../../../.venv/bin/python -m core.ui.sprites.build --check`
Expected: PASS, and the check exits 0.

- [ ] **Step 5: Commit**

```bash
git add core/ui/pixel_theme.py core/ui/sprites/art.py assets/sprites/icons tests/test_pixel_ui.py tests/test_sprites.py
git commit -m "feat(ui): pixel markup for timeline rows, markers, delta badges and the wide shell"
```

---

### Task 6: Timeline builder and renderer

**Files:**
- Create: `core/ui/timeline.py`
- Modify: `tests/test_pixel_ui.py:203-218` (`TestChatAvatars` moves here)
- Test: `tests/test_timeline.py`

**Interfaces:**
- Consumes: Task 2 `TimelineEvent`, Task 5 `event_html`, `marker_html`, `delta_badge_html`, `action_icon`, `EVENT_ICONS`; `core.ui.sprites.avatar_path()` and `icon_path("player")`; `Message` objects with `timestamp`, `sender`, `content`, `message_type`.
- Produces, in `core/ui/timeline.py`:
  - `FILTERS = ("All", "Chat", "Her day", "Thoughts")`, `TIMELINE_LIMIT = 200`, `TIMELINE_HEIGHT = 560`, `MARKER_GAP = timedelta(minutes=60)`, `EMPTY_TEXT = "Nothing yet. Say hi, or let her live."`
  - `@dataclass class TimelineItem: kind: str; timestamp: datetime; text: str; meta: str = ""; event: TimelineEvent | None = None` where `kind` is `"user"`, `"jenbina"`, `"marker"` or an event kind
  - `first_sentence(text: str) -> tuple[str, str]` (sentence, remainder)
  - `build_timeline(messages, events, person_name: str = "Jenbina", filter_name: str = "All", limit: int = TIMELINE_LIMIT) -> list[TimelineItem]`
  - `render_timeline(items: list[TimelineItem]) -> None`
  - `scroll_timeline_to_bottom() -> None`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_timeline.py` (a `Msg = namedtuple("Msg", "timestamp sender content message_type")` helper, `T = datetime(2026, 10, 27, 23, 38)`):

```python
class TestBuildTimeline(unittest.TestCase):
    def test_merges_by_time_and_detects_speakers(self):
        msgs = [Msg(T, "person", "hi", "greeting"), Msg(T + timedelta(minutes=3), "Matt", "hello", "text")]
        evs = [make_thought("x", "Quiet.")]; evs[0].created_at = T + timedelta(minutes=1)
        kinds = [i.kind for i in build_timeline(msgs, evs)]
        self.assertEqual(kinds, ["marker", "jenbina", "thought", "user"])
    def test_meta_marks_outreach(self):
        items = build_timeline([Msg(T, "person", "hi", "proactive"), Msg(T, "person", "hi", "text")], [])
        self.assertEqual(items[1].meta, "23:38 · she reached out first")
        self.assertEqual(items[2].meta, "23:38")
    def test_markers_on_gap_and_day_change(self):
        msgs = [Msg(T, "Matt", "a", "text"), Msg(T + timedelta(minutes=61), "Matt", "b", "text"), Msg(T + timedelta(days=1, minutes=5), "Matt", "c", "text")]
        markers = [i.text for i in build_timeline(msgs, []) if i.kind == "marker"]
        self.assertEqual(markers[0], "23:38")
        self.assertEqual(markers[1], "00:39 · Wed 28 Oct")
        self.assertEqual(len(markers), 3)
    def test_marker_carries_world_context_of_latest_action(self):
        T0 = datetime(2026, 10, 27, 20, 0)   # same calendar day throughout
        act = make_action("nap", "", [], 1, 2, "Jenbina's House", "night", "Clear skies", 15.1); act.created_at = T0
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
        ev = make_move("a", "b"); ev.created_at = T
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
        self.assertTrue(avatars[0].endswith("icons/player.png")); self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))
        self.assertIn("she reached out first", st.caption.call_args_list[-1].args[0])
    def test_action_row_has_badge_and_details(self):
        act = make_action("Eat soup", "hungry", ["eat early"], 80, 82, "Home", "noon", "Sunny", 20)
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [act]))
        html_ = st.markdown.call_args_list[-1].args[0]
        for needle in ("px-event-action", "Jenbina decided to eat soup", "80% → 82% (+2.0%)", "<summary>why?</summary>", "Lessons applied: eat early", 'alt="hunger"'):
            self.assertIn(needle, html_)
    def test_thought_row_details_only_when_longer(self):
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [make_thought("x", "Quiet night. Maybe text someone.")]))
            long_html = st.markdown.call_args_list[-1].args[0]
            render_timeline(build_timeline([], [make_thought("x", "Quiet night.")]))
            short_html = st.markdown.call_args_list[-1].args[0]
        self.assertIn("<summary>more</summary>", long_html); self.assertNotIn("<details", short_html)
    def test_unknown_kind_renders_title(self):
        ev = TimelineEvent(kind="mystery", title="Something happened")
        with patch("core.ui.timeline.st") as st:
            render_timeline(build_timeline([], [ev]))
        self.assertIn("Something happened", st.markdown.call_args_list[-1].args[0])
    def test_empty_timeline_shows_empty_text(self):
        with patch("core.ui.timeline.st") as st:
            render_timeline([])
        self.assertIn(EMPTY_TEXT, st.markdown.call_args[0][0])
```

Delete `TestChatAvatars` from `tests/test_pixel_ui.py` (its `render_chat_simple` import goes with it; `TestChatHandlerAvatars` stays).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.ui.timeline'`.

- [ ] **Step 3: Implement `core/ui/timeline.py`**

`build_timeline`: wrap messages as items (`kind="jenbina"` when `sender in ("person", person_name)`, else `"user"`; meta `HH:MM` plus ` · she reached out first` for `message_type in ("greeting", "proactive")`), wrap events as items (`kind=event.kind`, `text=event.title`, `meta=HH:MM`; note that `event.detail["action"]` holds the original, un-lowercased action text, which `action_icon` lower-cases itself), apply the filter, sort by `(timestamp, 0 if event else 1)`, keep the last `limit`, then insert markers: before the first item, and when the gap to the previous kept item exceeds `MARKER_GAP` or the date changes; marker text is `HH:MM`, then ` · %a %d %b` when the date differs from the previous item's, then ` · location · time_of_day · weather, {temperature:.0f}°C` from the most recent `action` item at or before this position in the unfiltered, sorted list (searching the events list, not the filtered one). `render_timeline`: messages through `st.chat_message(role, avatar=...)` (the avatar as a keyword argument) with `st.write(text)` and `st.caption(meta)`; events through `st.markdown(event_html(...), unsafe_allow_html=True)` with the per-kind rules in the spec table (thought: `first_sentence`, `details=("more", full)` only when the remainder is non-empty; action: `badge=delta_badge_html(before, after)`, `icon=action_icon(detail["action"])`, `details=("why?", reasoning + "\nLessons applied: " + lessons_text(lessons))` with the lessons line omitted when empty); markers through `marker_html`; an empty list renders `marker_html(EMPTY_TEXT)`. `scroll_timeline_to_bottom` calls `streamlit.components.v1.html(..., height=0)` with a script that, in `window.parent.document`, finds the first `[data-testid="stVerticalBlockBorderWrapper"]` whose inline style contains `overflow` and sets `scrollTop = scrollHeight`; verify the selector in the running app and adjust it if 1.38 names the scrolling element differently.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_timeline.py tests/test_pixel_ui.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/ui/timeline.py tests/test_timeline.py tests/test_pixel_ui.py
git commit -m "feat(ui): build and render the chat timeline with Jenbina's life events"
```

---

### Task 7: Status rail, run controls and mind card

**Files:**
- Create: `core/ui/rail.py`
- Modify: `core/ui/chat.py:418-432` (`_init_stage_placeholder`, `update_system_stage`), `core/ui/simulation.py:98-118` (`display_jenbina_image` gains `width: int = PORTRAIT_WIDTH`; the rail passes `width=192`)
- Test: `tests/test_rail.py` (new)

**Interfaces:**
- Consumes: `display_jenbina_image`, `render_needs_bars`, `render_emotion_chips`, `render_mood_indicator`, `get_jenbina_image_for_emotion`, `_weather_icon` from `core/ui/simulation.py`; `stage_pill_html`, `icon_html` from `pixel_theme`; `update_system_stage` from `core/ui/chat.py`.
- Produces, in `core/ui/rail.py`:
  - `class StatusRail: __init__(self, stage_slot, portrait_slot, vitals_slot, live_slot=None)`; `stage(self, text: str) -> None`; `portrait(self, image_path_or_state: str, caption: str | None = None) -> None`; `refresh(self, person) -> None`; `live_row(self, html: str) -> None`
  - `class NullRail(StatusRail)` with a no-argument constructor and no-op methods
  - `env_line_html(world_summary: dict | None) -> str` — `"<icon> Jenbina's House · Night · Clear skies, 15°C"`, or `"Jenbina's House"` when `world_summary` is `None`
  - `render_status_rail(person, world_summary: dict | None, doing: str | None, goal: str | None, live_slot=None) -> StatusRail`
  - `render_run_controls() -> dict` with keys `num_iterations`, `delay_seconds`, `run_loop`, `single_run`
  - `render_mind_card(person, display_name: str) -> None`
- Changes `update_system_stage(stage)` in `core/ui/chat.py` to write `stage_pill_html(stage)` into `st.session_state["_stage_placeholder"]`; `_init_stage_placeholder` is deleted (the rail registers the slot).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_rail.py` reusing `FakePerson` from `tests.test_pixel_ui`:

```python
class TestStatusRail(unittest.TestCase):
    def test_stage_writes_pill(self):
        slot = MagicMock()
        with patch("core.ui.chat.st") as st:
            st.session_state = {"_stage_placeholder": slot}
            StatusRail(slot, MagicMock(), MagicMock()).stage("thinking…")
        self.assertIn("px-stage", slot.markdown.call_args.args[0]); self.assertIn("thinking…", slot.markdown.call_args.args[0])
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
        rail = NullRail(); rail.stage("x"); rail.portrait("jenbina_base.png"); rail.refresh(FakePerson({}, {})); rail.live_row("y")
    def test_env_line(self):
        ws = {"location": {"name": "Jenbina's House"}, "time": {"time_of_day": "night"}, "weather": {"description": "light rain", "temperature": 15.1}}
        html_ = env_line_html(ws)
        self.assertIn('alt="rain"', html_); self.assertIn("Jenbina&#x27;s House · Night · light rain, 15°C", html_)
        self.assertEqual(env_line_html(None), "Jenbina's House")

class TestControlsAndMind(unittest.TestCase):
    def test_run_controls_keys_and_labels(self):
        with patch("core.ui.rail.st") as st:
            st.number_input.side_effect = [5, 3]; st.button.side_effect = [False, True]
            controls = render_run_controls()
        self.assertEqual(controls, {"num_iterations": 5, "delay_seconds": 3, "run_loop": True, "single_run": False})
        self.assertEqual([c.args[0] for c in st.button.call_args_list], ["Step once", "Run 5"])
    def test_mind_card_lists_goals_or_empty_text(self):
        person = SimpleNamespace(goal_system=SimpleNamespace(get_goal_stats=lambda: {"goals": [{"description": "feel connected", "progress": 0.1}]}), planning_system=None, learning_system=None, social_cognition=None)
        with patch("core.ui.rail.st") as st:
            st.tabs.return_value = [MagicMock() for _ in range(4)]
            render_mind_card(person, "Matt")
        written = " ".join(str(c.args[0]) for c in st.write.call_args_list + st.markdown.call_args_list)
        self.assertIn("feel connected · 10%", written); self.assertIn("No plan.", written); self.assertIn("Nothing learned yet.", written)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_rail.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.ui.rail'`.

- [ ] **Step 3: Implement `core/ui/rail.py` and adjust `update_system_stage`**

`render_status_rail` draws, inside `st.container(border=True)`: a header row (`st.columns([2, 1])`) with the "Now" label and `stage_slot = st.empty()` (registered as `st.session_state["_stage_placeholder"]` and initialised to `idle`); `portrait_slot = st.empty()` filled with `display_jenbina_image(get_jenbina_image_for_emotion(person), caption=person.name, width=192)` (and `portrait()` passes `width=192` too); `vitals_slot = st.empty()` filled by `refresh(person)`. `refresh` renders, in `vitals_slot.container()`: `render_mood_indicator`, `env_line_html(world_summary)`, `Doing: …` (`doing` cut with `shorten(…, 60)`) and `Goal: …` when set, `render_needs_bars`, `render_emotion_chips`. Store `world_summary`, `doing` and `goal` on the rail so `refresh(person)` can redraw them. `render_run_controls` renders the "Let her live" container: `st.number_input("Iterations", 1, 20, 5, 1)`, `st.number_input("Delay (seconds)", 1, 60, 3, 1)`, `st.button("Step once", type="primary", use_container_width=True)`, `st.button(f"Run {n}", use_container_width=True)` in that order (the test's `side_effect` order). `render_mind_card` renders `st.tabs(["Goals", "Plans", "Lessons", "About you"])` with the lists in spec §5 and the empty texts "No goals yet.", "No plan.", "Nothing learned yet.", "Nothing known yet."; the About you tab reads `person.social_cognition.get_or_create_model(display_name)` for `inferred_emotional_state`, `relationship.trust/closeness/conflict` and the top three `interests`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_rail.py tests/test_pixel_ui.py tests/test_greeting_generation.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/ui/rail.py core/ui/chat.py tests/test_rail.py
git commit -m "feat(ui): add the status rail with run controls and the mind card"
```

---

### Task 8: Chat flow — inline input, outreach message types, chat mood events

**Files:**
- Modify: `core/ui/chat.py:76-123` (`send_proactive_message`), `:126-164` (`check_return_greeting` callers), `:187-310` (`handle_user_input`), `:435-465` (`render_chat_simple`, kept working until Task 11)
- Test: `tests/test_chat_ui.py` (new)

**Interfaces:**
- Consumes: Task 3 `record_mood`, Task 2 `EventLog`.
- Produces, in `core/ui/chat.py`:
  - `get_event_log() -> EventLog` — cached in `st.session_state["event_log"]`, built from `_get_user_db_and_id()`
  - `ensure_outreach(person, llm) -> None` — the greeting check and the once-per-session proactive check that `render_chat_simple` does today; greeting stored with `person.send_message(display_name, greeting, "greeting")`, proactive with `"proactive"`
  - `handle_user_input(person, llm, memory_manager, debug_mode, user_input) -> dict | None` — no longer calls `st.chat_input`; returns `None` for empty input; records a `mood` event with source `"chat"` after `analyze_emotion_impact` adjustments are applied; the "💡 insight" bubble is gone
  - `render_chat_simple` now calls `ensure_outreach`, then `user_input = st.chat_input("Talk to Jenbina...")` and `handle_user_input(..., user_input)` so `core/app.py` keeps working until Task 11

- [ ] **Step 1: Write the failing tests**

Create `tests/test_chat_ui.py` using `_FakeSessionState` from `tests.test_greeting_generation`:

```python
class TestOutreachTypes(unittest.TestCase):
    @patch("core.ui.chat.send_proactive_message", return_value=None)
    @patch("core.ui.chat.check_return_greeting", return_value="You're back!")
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_greeting_is_stored_with_greeting_type(self, st, *_):
        st.session_state = _FakeSessionState(proactive_checked=True)
        person = MagicMock()
        ensure_outreach(person, None)
        person.send_message.assert_called_once_with("Matt", "You're back!", "greeting")

    @patch("core.ui.chat.generate_proactive_message", return_value="Still there?")
    @patch("core.ui.chat.check_proactive_message", return_value={"low_social": {}})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_proactive_is_stored_with_proactive_type(self, st, *_):
        st.session_state = _FakeSessionState()
        person = MagicMock()
        send_proactive_message(person, None)
        person.send_message.assert_called_once_with("Matt", "Still there?", "proactive")

class TestHandleUserInput(unittest.TestCase):
    @patch("core.ui.chat.st")
    def test_empty_input_returns_none_without_chat_input(self, st):
        self.assertIsNone(handle_user_input(MagicMock(), None, None, False, ""))
        st.chat_input.assert_not_called()

    @patch("core.ui.chat.analyze_emotion_impact", return_value={"joy": 6})
    @patch("core.ui.chat.handle_chat_interaction", return_value={"assistant_response": "hey", "user_message": "hi", "insight": "x"})
    @patch("core.ui.chat._get_user_db_and_id", return_value=(None, None))
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_chat_records_mood_event_and_no_insight_bubble(self, st, *_):
        log = EventLog()
        st.session_state = _FakeSessionState(event_log=log, action_history=[], needs_response=None, world_description=None, action_decision=None, state_response=None, simulation_history=[])
        snaps = iter([{"joy": 30}, {"joy": 36}])
        person = MagicMock(); person.get_emotions_snapshot.side_effect = lambda: next(snaps); person.social_cognition = None
        result = handle_user_input(person, None, None, False, "hi")
        self.assertEqual(result["assistant_response"], "hey")
        self.assertEqual([e.kind for e in log.recent()], ["mood"]); self.assertEqual(log.recent()[0].detail["source"], "chat")
        st.chat_message.assert_not_called()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_chat_ui.py -v`
Expected: FAIL with `ImportError: cannot import name 'ensure_outreach'`.

- [ ] **Step 3: Implement the changes in `core/ui/chat.py`**

Take `emotions_before = person.get_emotions_snapshot()` right before `analyze_emotion_impact` and `emotions_after` right after `apply_adjustments`, then `record_mood(get_event_log(), emotions_before, emotions_after, "chat")` inside the same `try`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_chat_ui.py tests/test_pixel_ui.py tests/test_greeting_generation.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/ui/chat.py tests/test_chat_ui.py
git commit -m "feat(chat): inline input handling, outreach message types and chat mood events"
```

---

### Task 9: The Streamlit runner updates the rail and records events instead of rendering

**Files:**
- Modify: `core/ui/simulation.py:584-1275` (`run_single_iteration`, `run_simulation_loop`), delete `render_environment_ribbon` (140-158) and `render_action_narrative` (247-276)
- Modify: `tests/test_pixel_ui.py` (drop the ribbon and action-narrative tests; keep `_weather_icon` coverage through `env_line_html` in Task 7)
- Test: `tests/test_simulation_runner.py` (new)

**Interfaces:**
- Consumes: Task 3 recording helpers, Task 7 `StatusRail`/`NullRail`, Task 5 `event_html`, `delta_badge_html`, `action_icon`, Task 8 `get_event_log`.
- Produces: `run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration, rail=None, event_log=None) -> dict` (same keys as today, `rail=None` means `NullRail()`, `event_log=None` means `get_event_log()`), `run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations, delay_seconds, rail=None, event_log=None) -> list[dict]` whose records now include `satisfaction_delta`, and the shared test helper `build_env(module) -> tuple[person, meta_cognitive_system, patches]` in `tests/test_simulation_runner.py`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_simulation_runner.py` with `build_env(module)`: a real `Person()` after `update_all_needs()`, with `init_learning_system(MagicMock())`, `init_goal_system(MagicMock())`, `init_planning_system(MagicMock())`, `init_social_cognition()`, `init_self_narrative()`, `init_curiosity_system()`, `init_social_interaction_tracker()`; `person.inner_monologue = SimpleNamespace(think=lambda **k: None, format_for_prompt=lambda: "[Inner voice — deliberation] Quiet tonight. Maybe text someone.", get_current_thought=lambda: SimpleNamespace(content="Quiet tonight. Maybe text someone.", mode="deliberation"))`; `person.goal_system.should_generate = lambda: False` (so no goal generation hits the mock LLM; if `record_experience` ever calls `extract_lessons` on the first experience, patch `person.learning_system.extract_lessons` the same way); `meta = MagicMock(); meta.get_meta_cognitive_stats.return_value = {"total_processes": 0, "total_insights": 0, "cognitive_biases": {}, "recent_insights": []}`; and `patch.multiple(module, create_basic_needs_chain=lambda llm, needs: {"action": "rest", "reasoning": "r"}, create_world_description_system=lambda llm: (lambda person, world, recent_actions="": '{"list_of_descriptions": [], "list_of_actions": ["Walk to Coupa Cafe"]}'), create_meta_cognitive_action_chain=lambda **k: {"chosen_action": "Walk to Coupa Cafe for coffee", "reasoning": "social", "lessons_applied": ["go out"]}, create_asimov_check_system=lambda llm: (lambda resp: {"compliant": True}), create_state_analysis_system=lambda llm, **k: {"ok": True}, analyze_emotion_impact=lambda **k: {"joy": 8})`.

```python
class TestUiRunnerEvents(unittest.TestCase):
    def test_iteration_records_events_and_drives_rail(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        rail = MagicMock(); log = EventLog()
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"):
            st.session_state = _FakeSessionState(simulation_history=[], jenbina_location="Jenbina's House", _proactive_llm=MagicMock())
            result = sim.run_single_iteration(person, MagicMock(), meta, 0, rail=rail, event_log=log)
        kinds = [e.kind for e in log.recent()]
        self.assertEqual(kinds[:2], ["thought", "move"]); self.assertIn("action", kinds); self.assertIn("mood", kinds)
        action = next(e for e in log.recent() if e.kind == "action")
        self.assertEqual(action.detail["location"], "Jenbina's House"); self.assertEqual(action.detail["lessons"], ["go out"])
        self.assertEqual(st.session_state["jenbina_location"], "Coupa Cafe")
        self.assertIn("satisfaction_delta", result)
        self.assertTrue(any("completed in" in c.args[0] for c in rail.stage.call_args_list))
        self.assertEqual(rail.live_row.call_count, 2)
        st.success.assert_not_called(); st.expander.assert_not_called(); st.columns.assert_not_called()

    def test_iteration_survives_event_log_failure(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        db = MagicMock(); db.store_event.side_effect = RuntimeError("disk")
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"):
            st.session_state = _FakeSessionState(simulation_history=[], jenbina_location="Jenbina's House")
            result = sim.run_single_iteration(person, MagicMock(), meta, 0, rail=NullRail(), event_log=EventLog(db, 1))
        self.assertIn("action_decision", result)

    def test_loop_records_delta_and_history(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"), patch("core.ui.simulation.time.sleep"):
            st.session_state = _FakeSessionState(simulation_history=[], jenbina_location="Jenbina's House")
            results = sim.run_simulation_loop(person, MagicMock(), meta, 2, 0, rail=NullRail(), event_log=EventLog())
        self.assertEqual(len(st.session_state["simulation_history"]), 2)
        self.assertIn("satisfaction_delta", results[0]); st.progress.assert_not_called()
```

Remove `TestChipsMoodRibbon.test_ribbon_icons` (or the ribbon assertions) and `TestActionAndSprite`'s `render_action_narrative` test from `tests/test_pixel_ui.py`, with their imports.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `../../../.venv/bin/python -m pytest tests/test_simulation_runner.py -v`
Expected: FAIL (`TypeError: run_single_iteration() got an unexpected keyword argument 'rail'`).

- [ ] **Step 3: Rewrite the rendering parts of `run_single_iteration` and `run_simulation_loop`**

Keep every computation line. Default the new parameters inside the function body (`from core.ui.rail import NullRail` imported there, not at module level, because `rail.py` imports this module's renderers; `event_log = event_log or get_event_log()`), and replace every direct `update_system_stage(...)` call in the runner with `rail.stage(...)`. Then replace, in order: the `inject_tamagotchi_css()` / `render_environment_ribbon` / centered avatar block (lines 620-635) with `rail.stage("thinking…")` and `rail.portrait(initial_image, caption=person.name)`; after the monologue (line 790) with `thought = record_thought(event_log, person.inner_monologue)` and, when not `None`, `rail.live_row(event_html("thought", first_sentence(thought.title)[0], meta=now_hhmm))`; the center panel block (794-801) with nothing; the thinking portrait with `rail.stage("deciding…")` + `rail.portrait(...)` as today; the location change (916-922) with `record_move(event_log, old_location, new_location)` when it changes; the action placeholder block (924-932) with nothing; the Stage 4 start with `rail.stage("checking…")`; after `apply_adjustments` (963) with `record_mood(event_log, emotions_before, person.get_emotions_snapshot(), "action")`; after `update_all_needs()` (987) with `rail.stage("learning…")`, `rail.refresh(person)`, `action_event = record_action(event_log, action_response, satisfaction_before, satisfaction_after, world_summary)` and `rail.live_row(event_html("action", action_event.title, meta=now_hhmm, badge=delta_badge_html(...), icon=action_icon(chosen_action), details=("why?", ...)))`; around the goal block (1031-1049) with `goals_before = snapshot_goals(person.goal_system)` before `update_progress` and `record_goal_changes(event_log, goals_before, snapshot_goals(person.goal_system))` after `generate_goals`; around `evaluate_step` (1052) with `current = person.planning_system.get_current_step()` captured before the call and `record_plan_step(event_log, step_result, plan.goal_description, step.description)` after it, `record_plan_finished` where the completed-plan loop runs, and `record_replan(event_log, replan_result)` after `check_for_replan`; the action-narrative update and final portrait (1119-1127) with `rail.portrait(final_image, caption=person.name)` only; the Tier-2 block (1130-1172) with nothing; the `st.success` (1210) with `rail.stage(f"completed in {iteration_duration:.0f}s")`. `debug_entry` gains `"curiosity_stats": person.curiosity_system.get_stats() if getattr(person, "curiosity_system", None) else None` and `"social_interaction_stats": person.social_interaction_tracker.get_stats() if getattr(person, "social_interaction_tracker", None) else None`. In `run_simulation_loop` drop the progress bar, status text, container and expander; call `rail.stage(f"iteration {i+1} of {n}")` before each iteration and `rail.stage(f"waiting {delay_seconds}s…")` before the sleep; add `"satisfaction_delta": result["satisfaction_delta"]` to the record. Delete `render_environment_ribbon` and `render_action_narrative`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_simulation_runner.py tests/test_pixel_ui.py tests/test_rail.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/ui/simulation.py tests/test_simulation_runner.py tests/test_pixel_ui.py
git commit -m "refactor(simulation): drive the status rail and record events instead of rendering the page"
```

---

### Task 10: The headless runner records the same events

**Files:**
- Modify: `core/simulation_runner.py:201-700`
- Test: `tests/test_simulation_runner.py`

**Interfaces:**
- Consumes: Task 3 helpers, Task 9's `build_env`.
- Produces: `run_single_iteration_headless(person, llm_json_mode, meta_cognitive_system, iteration, context)` uses `context["event_log"]` when present, else `EventLog(context.get("user_db"), context.get("user_id"))`, and records the same events at the same points as Task 9.

- [ ] **Step 1: Write the failing test**

```python
class TestHeadlessRunnerEvents(unittest.TestCase):
    def test_headless_iteration_records_same_events(self):
        import core.simulation_runner as hr
        person, meta, patches = build_env(hr)
        log = EventLog()
        context = {"simulation_history": [], "jenbina_location": "Jenbina's House", "debug_iterations": [], "event_log": log}
        with patches, patch("core.simulation_runner.generate_proactive_message", return_value=None), patch("core.simulation_runner.get_llm", return_value=MagicMock()):
            result = hr.run_single_iteration_headless(person, MagicMock(), meta, 0, context)
        kinds = [e.kind for e in log.recent()]
        self.assertEqual(kinds[:2], ["thought", "move"]); self.assertIn("action", kinds); self.assertIn("mood", kinds)
        self.assertEqual(context["jenbina_location"], "Coupa Cafe")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `../../../.venv/bin/python -m pytest tests/test_simulation_runner.py::TestHeadlessRunnerEvents -v`
Expected: FAIL (no events recorded: `kinds == []`).

- [ ] **Step 3: Add the recording calls to `core/simulation_runner.py`**

Mirror Task 9's recording points at lines 370 (thought), 444 (move), 478 (mood), 501 (action after `update_all_needs`), 540-551 (goals), 560-579 (plans). No rail calls here.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `../../../.venv/bin/python -m pytest tests/test_simulation_runner.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/simulation_runner.py tests/test_simulation_runner.py
git commit -m "feat(simulation): record Jenbina's life events from the headless runner too"
```

---

### Task 11: The home screen, and removal of the Chat page and dead renderers

**Files:**
- Modify: `core/app.py` (rewrite), `core/ui/chat.py` (delete `render_chat_simple`, `render_chat_interface`, `display_person_state_compact`, `display_communication_stats`, `display_conversation_history`, `display_memory_stats`, `display_memory_debug`, `display_social_model`), `core/ui/simulation.py` (delete `inject_tamagotchi_css`, `display_person_state`, `display_world_state`, `display_meta_cognitive_insights`, `display_learning_stats`, `display_goal_stats`, `display_working_memory_stats`, `display_identity_stats`, `display_curiosity_stats`, `display_social_interaction_stats`, `display_planning_stats`, `display_simulation_summary`, `render_simulation_controls`), `core/ui/__init__.py` (exports), `core/pages/5_🔧_Debug_Info.py` (two new sections)
- Delete: `core/pages/2_💬_Chat.py`
- Test: `tests/test_ui_exports.py` (new, tiny), plus a manual check in the running app

**Interfaces:**
- Consumes: everything above.
- Produces: `core.ui` exports `inject_pixel_css`, `run_single_iteration`, `run_simulation_loop`, `render_status_rail`, `render_run_controls`, `render_mind_card`, `build_timeline`, `render_timeline`, `handle_user_input`, `ensure_outreach`, `get_event_log`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_ui_exports.py`:

```python
def test_home_screen_building_blocks_are_exported(self):
    import core.ui as ui
    for name in ("inject_pixel_css", "run_single_iteration", "run_simulation_loop", "render_status_rail", "render_run_controls", "render_mind_card", "build_timeline", "render_timeline", "handle_user_input", "ensure_outreach", "get_event_log"):
        self.assertTrue(hasattr(ui, name), name)
    self.assertFalse(hasattr(ui, "render_chat_interface"))

def test_chat_page_is_gone(self):
    self.assertFalse(any(p.name.endswith("Chat.py") for p in Path("core/pages").iterdir()))
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `../../../.venv/bin/python -m pytest tests/test_ui_exports.py -v`
Expected: FAIL on the missing exports and the existing Chat page.

- [ ] **Step 3: Rewrite `core/app.py` and delete the dead code**

`main()` in order: `st.set_page_config(...)` as today; `inject_pixel_css(wide=True)`; `require_auth()`; `llm, llm_json_mode = init_llm()`; `person`, `meta_cognitive_system`, `memory_manager` from session state; `st.title("👧 Jenbina")`; sidebar with only the Debug Mode checkbox (value `True`, stored in `st.session_state.debug_mode`); `event_log = get_event_log()`; `display_name = _get_user_display_name()`; `ensure_outreach(person, llm)`; `world_summary = st.session_state.simulation_history[-1]["world_summary"] if st.session_state.get("simulation_history") else None`; `doing` from that record's `action_decision["chosen_action"]` (else `None`); `goal` from `person.goal_system.get_goal_stats()["goals"][0]["description"]` when any; `left, rail_col = st.columns([1.55, 1], gap="medium")`. In `left`: `st.markdown("**Today with Jenbina**")`, `filter_name = st.radio("Show", FILTERS, horizontal=True, label_visibility="collapsed", key="timeline_filter")`, `timeline = st.container(height=TIMELINE_HEIGHT)`, inside it `render_timeline(build_timeline(person.get_conversation_history(display_name, count=100), event_log.recent(200), person.name, filter_name))` then `live_slot = st.container()`; then `user_input = st.chat_input("Talk to Jenbina...")` and `scroll_timeline_to_bottom()`. In `rail_col`: `rail = render_status_rail(person, world_summary, doing, goal, live_slot=live_slot)`, `controls = render_run_controls()`, `render_mind_card(person, display_name)`. Then: if `user_input`: `with timeline: handle_user_input(person, llm, memory_manager, False, user_input)`, `save_person_state()`, `st.rerun()`. Then the auto-start flag exactly as today, and if `controls["run_loop"] or controls["single_run"] or auto_start`: `run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations, controls["delay_seconds"], rail=rail, event_log=event_log)`, copy the last result into `st.session_state.action_decision` / `needs_response` as today, `st.session_state.simulation_completed = True`, `save_person_state()`, `st.rerun()`. Finally `save_person_state()`. Delete the Chat page and the functions listed above; update `core/ui/__init__.py`. In Debug Info, after the Learning section, add "🔎 Curiosity & Exploration" (curiosity, boredom, novelty, open questions, exploration candidates) and "👥 Social Interactions" (people met today, total interactions, met names) reading `data.get("curiosity_stats")` and `data.get("social_interaction_stats")` in the same bordered-container style as the sections above them.

- [ ] **Step 4: Run the whole unit suite**

Run: `../../../.venv/bin/python -m pytest tests/test_*.py -v --tb=short`
Expected: all PASS, no `ImportError` from deleted names.

- [ ] **Step 5: Check the screen in the running app**

Run from the worktree with the venv: `JENBINA_SKIP_AUTH=1 ../../../.venv/bin/python -m streamlit run core/app.py --server.headless true --server.port 8511` (or the `jenbina` entry in `.claude/launch.json`) and open it.
Expected: the device is wider than before with two columns; the timeline is a scrollable box with the chat input directly under it; the rail shows the Now card (stage pill, portrait, needs bars), "Step once" / "Run 5", and the four tabs; no expanders, no success banners, no "Simulation History Summary"; after the auto-started iteration finishes the page reruns and the thought, action and mood rows appear in the timeline; typing a message shows it and the reply at the bottom of the timeline, and after the rerun the exchange is still there; with the "Thoughts" filter only thought rows remain; the sidebar has only navigation and the Debug Mode checkbox, and no "Chat" entry. If the newest row is not in view after a rerun, fix the selector in `scroll_timeline_to_bottom` (Task 6) here.

- [ ] **Step 6: Commit**

```bash
git add core/app.py core/ui core/pages tests/test_ui_exports.py
git rm core/pages/2_💬_Chat.py
git commit -m "feat(ui): one home screen with the chat timeline and the status rail; drop the Chat page"
```

---

### Task 12: E2E tests, docs and the knowledge graph

**Files:**
- Modify: `tests/e2e/test_simulation.py`, `tests/e2e/test_feedback_loop.py`, `CLAUDE.md`
- Run: `graphify update .`

**Interfaces:**
- Consumes: the labels and selectors fixed above: button "Step once", `.px-event-action .px-event-title`, `.satisfaction-delta`, `.need-row`, stage text "completed in".

- [ ] **Step 1: Port `tests/e2e/test_simulation.py`**

`test_page_loads` expects `text=Today with Jenbina` and a button named `Step once`. `test_single_iteration_produces_output` clicks `Step once`, then expects `text=Hunger` (rail), `.px-event-action .px-event-title` containing "Jenbina decided to", and `text=completed in` (stage pill), each with `STAGE_TIMEOUT`. Delete `test_simulation_summary_appears`.

- [ ] **Step 2: Port `tests/e2e/test_feedback_loop.py`**

In `_run_one_iteration`: click `Step once`; `action_el = page.locator(".px-event-action .px-event-title").first`; parse the delta from `page.locator(".satisfaction-delta").all()` texts with the existing `\(([+-]?\d+\.?\d*)%\)` pattern; keep the `completed in` wait and the `.need-row` count; the action-name regex becomes `^Jenbina decided to\s*`. Assertions unchanged.

- [ ] **Step 3: Syntax-check the e2e modules**

Run: `../../../.venv/bin/python -m py_compile tests/e2e/test_simulation.py tests/e2e/test_feedback_loop.py`
Expected: no output. (The e2e suites run only from their manual workflows; running `tests/e2e/test_simulation.py` locally with `JENBINA_SKIP_AUTH=1` and Playwright installed is optional and costs LLM calls.)

- [ ] **Step 4: Update `CLAUDE.md`**

Repository structure: remove `2_Chat.py`, add `core/timeline/` ("event log of Jenbina's life: vocabulary, titles, EventLog, recording helpers"), `core/ui/timeline.py` and `core/ui/rail.py`. Plan table: add rows for `2026-10-28-timeline-ui-redesign.md` and `2026-10-28-timeline-ui-implementation.md`.

- [ ] **Step 5: Refresh the knowledge graph and run the suite once more**

Run: `graphify update . && ../../../.venv/bin/python -m pytest tests/test_*.py -q`
Expected: the graph updates without error; all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/e2e CLAUDE.md graphify-out
git commit -m "test(e2e): port the simulation and feedback-loop tests to the timeline screen; docs: update CLAUDE.md"
```
