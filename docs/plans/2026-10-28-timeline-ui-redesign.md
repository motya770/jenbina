# Timeline UI Redesign

**Date:** 2026-10-28
**Status:** Approved (layout approved in conversation on 2026-10-28; spec reviewed by a builder check)
**Approach:** Merge the Simulation and Chat pages into one home screen: a chat timeline on the left that interleaves the conversation with Jenbina's life events, and a live status rail on the right. Streamlit 1.38 only, no framework change, the pixel skin from `2026-10-27-pixel-art-ui-redesign.md` stays.

## Problem

Talking to Jenbina is hard because the conversation has no home.

- On the Simulation page the transcript sits between the status block and the
  iteration output. The input is pinned to the bottom of the window, so after one
  run the conversation is several screens away from where you type.
- The Chat page never renders the transcript (`render_chat_interface` in
  `core/ui/chat.py`). An exchange appears once, between the "Current State" bullets
  and four stat expanders, and vanishes on the next rerun. History survives only as
  text lines inside a collapsed expander. The page also carries leftovers of the old
  sequential layout ("6. Interaction with User:", a second "Chat with Jenbina").
- One iteration renders an expander containing the environment ribbon, a second
  portrait, a second set of needs bars, a second set of emotion chips, the action
  card, five bordered stat cards with duplicated captions, two success banners and a
  "Simulation History Summary" expander that repeats most of it as text. Everything
  inside is squeezed into the middle third of a 46rem device.
- The same state is shown three or four ways (mood badge, emotion chips, "Current
  State" list, needs bars).
- What she did, thought and felt is only visible inside the iteration expander and
  on Debug Info; simulation history lives in session state and is gone on reload,
  while chat history is persisted.

Bugs found while looking:

- `handle_chat_interaction` returns the prompt injection text ("You have just
  noticed something striking about this person. Lead with this observation…") as
  `insight`, and the UI prints it under a lightbulb.
- The action card prints "Lessons applied" as a raw Python list.
- The history summary always reports a 0.0% delta because the iteration record never
  stores `satisfaction_delta`.

## Goal

One screen that answers two questions at a glance: what is Jenbina doing right now,
and what happened between us and in her day. The conversation and her life are one
scrollable story; her current state is always in view beside it; the controls to let
her live are on the same screen. Debug material leaves the home screen entirely.

## Non-goals

- Running the simulation in a background thread or making the chains faster. The
  page still blocks while an iteration runs (today 1–5 minutes). The design makes
  the wait legible (live stage pill, live thought and action rows); it does not
  remove it.
- Changing prompts, chains, needs, memory, goals or learning logic. The computation
  flow and LLM call order of `run_single_iteration()` stay as they are.
- Redesigning the Environment, Console, Debug Info or Admin pages beyond what is
  named below.
- A dedicated mobile layout. Streamlit stacks the two columns on narrow windows;
  that is enough.
- Renaming `core/app.py` (the sidebar entry still reads "app"; launchers and tests
  reference the file).

## Anti-goals (what would make this a failure even if it works)

- The input and the latest exchange end up on different screens again.
- Nested expanders, duplicated captions or repeated status blocks reappear on the
  home screen.
- Raw JSON, chain traces or memory statistics on the home screen.
- Emoji in new markup. Icons come from the 8x8 sprite set (`icon_html`).
- Her day only exists while the browser tab is open.

## Design

### 1. Pages

- `core/app.py` becomes the home screen described below. Title stays "👧 Jenbina".
- `core/pages/2_💬_Chat.py` is deleted. Its only distinct content (communication
  stats, memory stats, social model, memory debug) is either dropped, moved to the
  rail's "About you" tab, or moved to Debug Info (see §6).
- Environment, Console, Debug Info and Admin keep their content. Debug Info gains the
  curiosity and social-interaction stats that the iteration expander used to show.
- Sidebar: page navigation and the "🔧 Debug Mode" checkbox only. The checkbox
  stays because the Environment page reads `st.session_state.debug_mode` for its
  debug controls; the home screen itself never renders debug material (§3). The
  simulation controls move into the rail.

### 2. Shell

- `inject_pixel_css(wide=False)` gains a `wide` flag. With `wide=True` it appends an
  override that sets the device (`.block-container`) to `max-width: 64rem`. The home
  screen passes `wide=True`; every other page keeps 46rem.
- The home screen lays out `left, rail = st.columns([1.55, 1], gap="medium")`.
- The existing bottom-bar CSS for `stBottomBlockContainer` stays for other pages but
  is unused on the home screen, because the chat input is rendered inline (§3).

### 3. Left column: the timeline

```
┌ Today with Jenbina            (·) All  ( ) Chat  ( ) Her day  ( ) Thoughts ┐
│ ── 23:38 · Jenbina's House · night · clear skies, 15°C ──                  │
│ [avatar] Hey, you've got "E2E Test User" energy…                          │
│          23:38 · she reached out first                                     │
│ (thought) It's so quiet tonight… maybe I should text someone   ▸ more      │
│ [icon] Jenbina decided to attend live music at Coupa Cafe   83 → 85%  ▸why?│
│                               Hi Jenbina, how was your evening? [player]   │
│                                                                    23:41   │
│ [avatar] Pretty calm and grounding. I kept it simple…                      │
│          23:41                                                             │
│ [icon] Mood lifted: trust 40 → 44, joy 35 → 38                             │
│ [icon] New goal: feel more connected this week                             │
├────────────────────────────────────────────────────────────────────────────┤
│ [ Talk to Jenbina...                                                    ▶ ] │
└────────────────────────────────────────────────────────────────────────────┘
```

**Header.** The label "Today with Jenbina" and a horizontal `st.radio` (label
collapsed) with the filters All / Chat / Her day / Thoughts, stored in
`st.session_state["timeline_filter"]`, default All.

**Body.** `timeline = st.container(height=TIMELINE_HEIGHT)` with
`TIMELINE_HEIGHT = 560`. Items render oldest first, newest at the bottom. The
container holds, in order: the persisted items (§4), then the live exchange of the
current turn when the user just sent a message (§3, "Live turn"), then an empty
placeholder (`st.empty()`) that the runner uses for live rows during an iteration
(§5).

**Input.** `st.chat_input("Talk to Jenbina...")` is called directly under the
container, inside the left column. Streamlit 1.38 renders a chat input inline when it
is nested in a column or container, so it sits at the bottom of the timeline, not at
the bottom of the window.

**Live turn.** `handle_user_input` in `core/ui/chat.py` no longer calls
`st.chat_input` itself; it takes the submitted text as a parameter. The home screen
reads the input below the container and, when there is text, calls
`handle_user_input(...)` inside `with timeline:` so the new user bubble and reply
(rendered by `handle_chat_interaction`) appear at the bottom of the timeline. On the
next rerun the same exchange comes from history. The separate "💡 insight" bubble is
removed; the insight is already woven into the reply by the prompt. The "Context: N
recent messages + M semantically relevant" toast stays. The home screen always calls
`handle_user_input(..., debug_mode=False)`, so the chat handler's "🔍 Context Being
Used" expander (memory documents, relevance scores, needs snapshots) never renders
in the timeline, whatever the sidebar checkbox says.

**Scroll.** After the timeline renders, the newest item must be in view. Builder's
call on mechanism; the intended one is a `streamlit.components.v1.html` snippet of
height 0 that scrolls the first height-limited block wrapper in the parent document
(`[data-testid="stVerticalBlockBorderWrapper"]` with an `overflow` style) to its
bottom. If that proves unreliable, the fallback is to render newest first with the
input above the list, and the design accepts that.

**Items.** Each item is one of:

| Kind | Rendered as | Text |
|------|-------------|------|
| user message | `st.chat_message("user", avatar=icon_path("player"))` | content, then a caption `HH:MM` |
| Jenbina message | `st.chat_message("assistant", avatar=avatar_path())` | content, then a caption `HH:MM`, plus ` · she reached out first` when the message type is `greeting` or `proactive` |
| thought | `event_html("thought", …)` | first sentence of the thought in italics; the full text inside `<details><summary>more</summary>` when it is longer |
| action | `event_html("action", …)` | icon, "Jenbina decided to …" (title, §4) in a `.px-event-title` element, a `.satisfaction-delta` badge reading `83% → 85% (+1.7%)` (one decimal on the signed delta, `delta-positive` / `delta-negative` / `delta-neutral` as today, plus `data-before`, `data-after` and `data-delta` attributes for tests), and `<details><summary>why?</summary>` holding the reasoning and "Lessons applied: a; b; c" |
| mood, goal, plan, move | `event_html(kind, …)` | icon and title |
| marker | `marker_html(text)` | centered muted divider |

A marker is inserted before the first item and whenever the gap to the previous item
is more than 60 minutes or the calendar day changes. Marker text is `HH:MM` plus the
world context (`location · time of day · weather, temp°C`) of the most recent action
event at or before that point when one exists, and the date (`Mon 27 Oct`) when the
day changed.

`event_html`, `marker_html` and the CSS for `.px-event`, `.px-event-<kind>`,
`.px-event-title`, `.px-event-meta`, `.px-event details/summary` and `.px-marker`
live in `core/ui/pixel_theme.py`, in the existing vocabulary: 3px `#1E1B3A` borders,
hard 4px shadows, VT323 20px for text, Press Start 2P 9–10px for meta, no radius, no
gradients. Thought rows use the `--px-muted` ink and italics; action rows carry the
left-tail of the current `.px-dialog-action`. Icons come from `icon_html`; each
event kind maps to one icon name. Existing icons may be reused (`love` for social
actions, `hunger` for eating, `sleep`, `self_actualization` for reading and
learning, `esteem` for goals). Builder's call which new 8x8 icons to add (for
example `thought`, `walk`, `drink`, `plan`, `mood`, `act`), drawn in
`core/ui/sprites/art.py` in the shared palette and rebuilt with
`python -m core.ui.sprites.build`.

**Filter.** All shows everything. Chat shows messages only. Her day shows action,
move, goal, plan and mood. Thoughts shows thought only. Markers always show when at
least one item follows them in the filtered list.

**Limit.** The timeline shows at most the last 200 items after merging (the last 100
messages with the last 200 events, merged, then truncated from the front). No
"show earlier" control in this revision.

### 4. The event log

Her day is persisted as events in `users.db`, next to the conversations table, so it
survives reloads and is per user.

**Table** (created in `UserDatabase._create_tables`):

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

`created_at` is written by Python as `datetime.now().isoformat()` (local, naive,
microseconds), not by SQLite's `datetime('now')`. Chat messages in the timeline come
from `Person.conversations` whose `Message.timestamp` is also `datetime.now()`, so
the two sort consistently. (The `conversations` table's second-resolution UTC
`created_at` is not used for ordering the timeline.)

**API** on `UserDatabase`:

- `store_event(user_id, kind, title, detail=None, created_at=None) -> int`
- `get_events(user_id, limit=200) -> list[dict]`, oldest first, each dict with
  `id, kind, title, detail (parsed), created_at (datetime)`.

**Module** `core/timeline/` (new, Streamlit-free so the headless runner can use it):

- `events.py`: `TimelineEvent` dataclass (`kind, title, detail, created_at`), the
  kind constants `THOUGHT, ACTION, MOOD, GOAL, PLAN, MOVE`, the title builders, and
  `EventLog`.
- `EventLog(user_db, user_id)` wraps `store_event`/`get_events`; with no `user_db`
  or `user_id` it keeps events in an in-memory list (for tests and sessions without
  a user). `record(event)` persists; `recent(limit)` returns events oldest first.

**Kinds, details and titles** (titles are computed when the event is recorded, so
rendering needs no logic and the table is self-describing):

| Kind | detail | title |
|------|--------|-------|
| `thought` | `{"mode": "deliberation", "text": "…full text…"}` | the full thought text (the renderer shortens it) |
| `action` | `{"action", "reasoning", "lessons": [..], "satisfaction_before", "satisfaction_after", "location", "time_of_day", "weather", "temperature"}` | `Jenbina decided to <action>` with the action lower-cased and cut to 90 characters at a word boundary with `…` |
| `mood` | `{"source": "action"\|"chat", "changes": {"trust": [40, 44], "joy": [35, 38]}}` (top three by absolute delta, only deltas ≥ 1) | `Mood lifted: trust 40 → 44, joy 35 → 38` when the sum of deltas is positive, `Mood dipped: …` otherwise; no event when nothing changed |
| `goal` | `{"event": "created"\|"advanced"\|"completed", "description", "progress"}` | `New goal: …` / `Goal advanced: … → 40%` / `Goal reached: …` |
| `plan` | `{"event": "step_completed"\|"replanned"\|"completed"\|"overridden", "goal", "step"}` | `Plan step done: <step>` / `Replanned: <goal>, first step <step>` / `Plan finished: <goal>` / `Plan step skipped for an urgent need` |
| `move` | `{"from", "to"}` | `Walked from <from> to <to>` |

**Recording points** in the iteration (both `core/ui/simulation.py` and
`core/simulation_runner.py` record the same events through `EventLog`, so a day
simulated by `run_scheduler.py` while the user is away shows up in the timeline):

1. after the inner monologue completes: `thought`
2. after the action is chosen and its location detected: `move` (only when the
   location changed), then `action` once the satisfaction delta is known (after
   `update_all_needs`)
3. after emotion adjustments are applied: `mood` with source `action`
4. in the learning stage: `goal` for each advanced or newly created or completed
   goal, `plan` for step completed / replanned / completed / overridden

In the chat flow (`handle_user_input`), after `analyze_emotion_impact` applies
adjustments: `mood` with source `chat`.

**Message types.** `check_return_greeting` and `send_proactive_message` store their
messages with `message_type` `greeting` and `proactive` instead of `text`, so the
timeline can label them. `Person.send_message` already accepts the type.

### 5. Right column: the status rail

```
┌ Now                                   [ thinking… ] ┐
│ ┌────────┐  Jenbina · Trust 44                      │
│ │portrait│  Jenbina's House · night · 15°C          │
│ │        │  Doing: attending live music at Coupa…   │
│ └────────┘  Goal: feel more connected               │
│ [sprite strip + caption]                            │
│ HUNGER  ██████████ 100%                             │
│ SLEEP   ██████████ 100%                             │
│ SAFETY  ██████████ 100%                             │
│ SOCIAL  ██████░░░░  60%                             │
│ ESTEEM  ░░░░░░░░░░   0%                             │
│ GROWTH  ░░░░░░░░░░   0%                             │
│ [Trust 44] [Joy 38] [Anticipation 35]               │
├─────────────────────────────────────────────────────┤
│ Let her live                                        │
│ Iterations [5]   Delay (s) [3]                      │
│ [ Step once ]  [ Run 5 ]                            │
├─────────────────────────────────────────────────────┤
│ Goals | Plans | Lessons | About you                 │
│ Feel more connected ……………………… 10%                  │
│ Learn one new thing a day ………… 40%                  │
└─────────────────────────────────────────────────────┘
```

Three bordered containers (`st.container(border=True)`), pixel-styled by the
existing expander/alert rules or a new `.px-card` rule, builder's call.

**Now card.**

- Header: "Now" and a stage pill. The pill replaces the "⚙️ stage" one-liner: it
  shows the live system stage (`idle`, `thinking…`, `deciding…`, `checking…`,
  `learning…`, `replying…`, `iteration 2 of 5`, `completed in 269s`). It is an
  `st.empty()` placeholder written by `update_system_stage`, which keeps its name
  and signature.
- Portrait and sprite strip: `display_jenbina_image` into an `st.empty()`
  placeholder, portrait width 192, so the runner can switch to the thinking,
  action and final-emotion states as today.
- Mood badge (`render_mood_indicator`), one line
  `location · time of day · weather temp°C` from the latest world summary of the
  session (or, before any run, from the most recent action event, or
  "Jenbina's House" alone), `Doing: <last action, cut to 60 characters>` and
  `Goal: <top active goal>` when there is one.
- Needs bars (`render_needs_bars`) and emotion chips (`render_emotion_chips`),
  both in a placeholder the runner refreshes after `update_all_needs`.

The placeholders are bundled in a `StatusRail` object (`core/ui/rail.py`) with
`stage(text)`, `portrait(state_or_path, caption)`, `refresh(person)` and
`live_row(html)` (writes into the timeline's live placeholder, §3) so
`run_single_iteration` takes one handle instead of touching page layout.

**Let her live card.** "Iterations" (1–20, default 5) and "Delay (seconds)" (1–60,
default 3) number inputs, then two buttons: "Step once" (primary) and "Run N" where N
is the current iterations value. These replace "▶️ Run Single Iteration" and
"🔄 Run Simulation Loop"; the e2e tests are updated to the new labels.

**Mind card.** `st.tabs(["Goals", "Plans", "Lessons", "About you"])`:

- Goals: up to five active goals as `description · progress%`, else "No goals yet."
- Plans: the active plan's goal, "step n of m", the current step; else "No plan."
- Lessons: up to five active lessons as `description · confidence%`, else
  "Nothing learned yet."
- About you: the social model for the current user: inferred emotion, trust /
  closeness / conflict, and the top three interests. The research dossier is not
  shown.

Nothing else from the old Tier-2 cards (learning counters, curiosity, social
interaction counters, working memory, identity, meta-cognition) appears on the home
screen; see §6.

### 6. The runner

`run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration,
rail, event_log)`:

- The computation flow, chains and their order are unchanged.
- All page rendering is removed: no environment ribbon, no centered avatar column,
  no thought bubble, no needs bars, no emotion chips, no action placeholder, no
  Tier-2 cards, no `st.success`. In their place: `rail.stage(...)` at each stage,
  `rail.portrait(...)` for the thinking/action/final states, `rail.refresh(person)`
  after `update_all_needs`, `rail.live_row(...)` for the thought row as soon as the
  monologue is ready and for the action row once the delta is known, and
  `event_log.record(...)` at the points in §4.
- The debug entry for Debug Info is kept and gains `curiosity_stats` and
  `social_interaction_stats`; Debug Info renders them in the same style as its
  other sections.
- Returns the same dict as today plus `satisfaction_delta` already present.

`run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations,
delay_seconds, rail, event_log)`:

- No progress bar, no status text, no per-iteration expander. The stage pill
  carries "iteration i of n" and the delay countdown text.
- Still appends the iteration record to `st.session_state.simulation_history`
  (the chat and proactive-message code read recent actions from it).
- After the loop the page calls `save_person_state()` and `st.rerun()` so the
  timeline re-renders from the persisted events and the live rows are replaced.

Auto-start on first load stays as it is (one iteration, then the rerun).

`display_simulation_summary`, `render_action_narrative`, `render_environment_ribbon`
and the `display_*_stats` helpers that only served the iteration expander are
deleted from `core/ui/simulation.py` unless Debug Info still uses them (then they
move or are imported from there). `core/ui/__init__.py` exports are updated.

### 7. Bug fixes in scope

- `handle_chat_interaction` returns the generated insight text as `insight`, never
  the injection wrapper.
- Lessons are joined with "; " wherever a list is shown as text.
- The iteration record stores `satisfaction_delta` (used by the headless runner's
  callers and kept for parity even though the summary expander is gone).

### 8. Error handling

- `EventLog.record` never raises into the runner: storage errors are printed and the
  event is dropped; the iteration continues.
- `get_events` on a database created before this change works because
  `_create_tables` runs `CREATE TABLE IF NOT EXISTS` on every open.
- A `detail_json` that fails to parse yields `detail = {}`.
- An unknown event kind renders with the generic `act` icon and its title.
- Missing portrait or sprite files fall back as they do today (`sprite_html`
  placeholder text).
- If the scroll snippet cannot find the container, nothing happens and the page is
  still usable.

### 9. Testing

Unit tests (no LLM, no live database; `UserDatabase(db_path=<tempfile>)`):

- `tests/test_user_db.py`: the `events` table exists; `store_event`/`get_events`
  round trip, ordering oldest-first, `limit`, `detail` parsing, empty detail.
- `tests/test_timeline.py` (new): title builders for every kind, including the
  90-character cut and the lifted/dipped wording; `EventLog` in-memory fallback;
  `build_timeline` merges messages and events by time, inserts markers on gaps and
  day changes, applies each filter, and truncates to the limit; `event_html` and
  `marker_html` escape content and carry the kind classes; the renderer calls
  `st.chat_message` with the player icon for user rows and the Jenbina avatar for
  her rows and adds "she reached out first" for greeting/proactive types.
- `tests/test_pixel_ui.py`: `TestChatAvatars` moves to the timeline renderer; the
  needs/emotion/mood/sprite tests stay; a `StatusRail` test checks `stage()` writes
  the pill text and `refresh()` renders needs rows into the placeholder.
- `tests/test_chat_handler.py`: the insight test asserts the returned insight is the
  generated text and does not contain "Lead with this observation".
- `tests/test_simulation_runner.py` (new or extended): with chains mocked, one
  headless iteration records a thought, an action and a mood event in an in-memory
  `EventLog`.

E2E (`tests/e2e/test_simulation.py`, manual/scheduled workflow):

- page loads: "Today with Jenbina" and the "Step once" button are visible;
- after clicking "Step once": "Hunger" is visible in the rail, a row containing
  "Jenbina decided to" appears in the timeline, and the stage pill shows
  "completed in".

The e2e test for the summary section is removed with the section.

`tests/e2e/test_feedback_loop.py` (manual workflow `feedback-loop-test.yml`) is
ported, not rewritten: it clicks "Step once", reads the action title from
`.px-event-action .px-event-title`, parses the signed delta from the
`.satisfaction-delta` badge text with the same `\(([+-]?\d+\.?\d*)%\)` pattern,
waits for "completed in" in the stage pill, and counts `.need-row` elements in the
rail. Its assertions do not change.

### 10. Code changes

**New**

- `core/timeline/__init__.py`, `core/timeline/events.py`
- `core/ui/timeline.py`: `build_timeline(messages, events, limit=200, filter_name="All")`
  and `render_timeline(items)`
- `core/ui/rail.py`: `StatusRail`, `render_status_rail(person, ...) -> StatusRail`,
  `render_run_controls()`, `render_mind_card(person, display_name)`
- `tests/test_timeline.py`, `tests/test_simulation_runner.py`
- new 8x8 icons in `core/ui/sprites/art.py` and `assets/sprites/icons/`

**Modified**

- `core/app.py`: the home screen layout above
- `core/ui/chat.py`: `handle_user_input` takes the text; greeting and proactive
  message types; `mood` event after chat; `render_chat_simple`,
  `render_chat_interface`, `display_person_state_compact`,
  `display_communication_stats`, `display_conversation_history`,
  `display_memory_stats`, `display_social_model`, `display_memory_debug` deleted
- `core/ui/simulation.py`: runner changes in §6; dead renderers removed
- `core/simulation_runner.py`: records the same events
- `core/ui/pixel_theme.py`: `wide` flag, `event_html`, `marker_html`, new CSS
- `core/auth/user_db.py`: events table and API
- `core/interaction/chat_handler.py`: insight fix
- `core/pages/5_🔧_Debug_Info.py`: curiosity and social sections
- `core/ui/__init__.py`: exports
- `tests/test_user_db.py`, `tests/test_pixel_ui.py`, `tests/test_chat_handler.py`,
  `tests/e2e/test_simulation.py`, `tests/e2e/test_feedback_loop.py`
- `CLAUDE.md`: repository structure and plan table

**Removed**

- `core/pages/2_💬_Chat.py`

## Decisions made while writing this (my calls, open to change)

- The event log lives in `users.db` as a table rather than inside the serialized
  Person state, so the scheduler and the UI write to one place and the log does not
  grow the person blob.
- Titles are computed at record time, not render time.
- The timeline keeps chat messages in `Person.conversations` as the source (it is
  what the UI renders today and it includes greetings), and only the message types
  change.
- The separate insight bubble goes away.
- Auto-start of one iteration on first load stays.
- The mind card shows the social model but not the research dossier.
- Button labels change to "Step once" / "Run N"; the e2e tests follow.
- Thought and action rows render live during an iteration; everything else waits
  for the rerun.
- The home screen never shows the chat handler's context expander, even with Debug
  Mode on (raised by the builder check).
- The action badge keeps the signed delta so the feedback-loop e2e test can be
  ported instead of rewritten (raised by the builder check).
- Goal `created` and `completed` events come from diffing the goal list before and
  after the learning stage, since `generate_goals` and milestone completion expose
  no hook (noted by the builder check).

## Left to the builder

- Exact CSS values and the new icon art.
- The scroll-to-newest mechanism (intended approach in §3).
- Whether `StatusRail` is passed explicitly or kept in session state (explicit is
  preferred).
- The order of tasks, provided each lands green.
