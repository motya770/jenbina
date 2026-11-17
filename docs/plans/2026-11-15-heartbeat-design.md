# Heartbeat: one Jenbina, living continuously

Status: design, awaiting approval. Date: 2026-11-15.

## Intent

Jenbina should be a being rather than a simulation someone steps through. Today
she only acts when a person presses a button or opens the page, and every user
account holds a separate copy of her. This project gives her a continuous
existence as one individual: she lives on her own clock, sleeps and wakes,
and is the same Jenbina for everyone who meets her.

This is the first of several projects toward that aim. A persistent world,
autobiographical memory, real stakes and other inhabitants come later and are
out of scope here.

## Goals

1. Exactly one Jenbina exists. Every account talks to the same being and sees
   the same life.
2. She lives without anyone watching: she takes a moment of life ("a beat")
   on a regular interval for as long as her process is running.
3. She has a sleep and wake rhythm. While asleep she takes no decisions and
   makes no LLM calls.
4. Time she was not running is handled honestly: she notices the gap and is
   not punished for it.
5. Conversations stay private to each person, and chatting stays responsive.
6. The home screen shows her life as it happens, with no button to make her
   live.

## Non-goals

- A world that persists between beats, objects, money, other inhabitants.
- Long-term memory of her own life, dreams, or memory consolidation during
  sleep. (Waking is the hook where consolidation will later attach.)
- Death, illness, or any consequence of unmet needs.
- A separate always-on server process, an API, or non-Streamlit clients.
- Time zones. She keeps using the host machine's clock, as today.
- Persisting `MetaCognitiveSystem`. The host owns one instance per process
  lifetime, as a session does today.

## Anti-goals

These would make the project a failure even if it runs:

- Two hearts beating at once, or two copies of her state overwriting each
  other.
- What one person said to her appearing in a conversation with another person.
- A runaway LLM bill: beats firing far more often than configured, or
  retrying forever against a failing API.
- Chat that regularly hangs for a minute because she is "busy".
- Losing the existing Jenbina's accumulated state during the move.

## How it works today

- `core/app.py` loads a `Person` into `st.session_state` once per browser
  session, runs one iteration automatically when the page opens
  (`simulation_auto_started`), runs more when "Step once" / "Run N" is pressed,
  and saves the whole serialized `Person` on every rerun.
- `run_scheduler.py` is a separate process that loads the same row, runs one
  iteration every 5 hours for one user id, and saves it back. An open browser
  tab never reloads, so it overwrites whatever the scheduler did.
- State is stored per account: `user_state(user_id PRIMARY KEY)` holds the
  serialized `Person`, `events(user_id)` holds her timeline, and
  `conversations(user_id)` holds chat messages.
- The iteration exists twice: `core/ui/simulation.py:run_single_iteration`
  (draws to the rail) and `core/simulation_runner.py:run_single_iteration_headless`
  (no Streamlit). One iteration is roughly ten LLM calls and takes tens of
  seconds. The two copies have drifted: only the UI copy records simulated
  social actions in the social interaction tracker
  (`core/ui/simulation.py:565-577`) and feeds the social day into the inner
  monologue (`:446-448`); `run_scheduler.py` never initialises the tracker; and
  the headless copy stores proactive messages with type `"text"` where the UI
  uses `"proactive"`, which the timeline needs for its label.
- Her location, the recent-actions history and the last world description live
  only in session memory, so a restart puts her back at home with no recent
  past.
- There is no sleep state. An action containing the word "sleep" adds 70 to the
  sleep need instantly.
- `Person` already supports knowing several people: `person.conversations` and
  the social-cognition models are keyed by the person's display name, and
  ChromaDB chat memory is already scoped per account (`user_<id>`).
- Some things in the single `Person` assume one user: `last_visit_time` (drives
  the return greeting), `insight_system.first_impression_delivered`, the
  insight system's "max 3 per session" counter (never serialized), and the
  proactive message, which goes to "the" user.
- Every chat prompt includes `person.get_current_state()`
  (`core/ui/chat.py:227`), which includes `social_cognition.get_stats()`: the
  full model of every person she knows, with beliefs taken verbatim from their
  messages and their research dossier. Harmless while each account has its own
  `Person`; a leak the moment there is one.
- `Person.update_all_needs()` decays lessons and goal confidence by a fixed
  0.5 hours per call, regardless of how much time really passed. Needs and
  emotions already decay by real elapsed time.

## Approaches

**A. The heart lives inside the app's server process (chosen).** One object,
the host, owns the single live `Person`. A background thread in the Streamlit
server process beats on it; every browser session reads and talks to that same
object. Storage is only for surviving restarts.
Trade-offs: the smallest change to the chat path, which keeps working on a
live in-memory object and stays fast. She lives exactly as long as the app
server runs, and the heart starts on the first page load after the server
starts, because Streamlit runs no code before that.

**B. A separate daemon process owns her; the UI talks to it through the
database.** The UI writes messages to an inbox table and polls for replies.
Trade-offs: she survives UI restarts and other clients could reach her later,
but the whole chat path, greetings, insights and the live rail must be rebuilt
around polling, and two processes must be deployed and kept alive. It is the
right shape eventually and too large a first step.

**C. Keep loading and saving her state around every iteration, and add
database locking.** Trade-offs: least new structure, but an iteration spends
tens of seconds in LLM calls, so either chat is locked out for that long or
updates are lost. Rejected.

A was chosen because it removes the copies, which is the actual defect, with
the least rewriting. To keep B open, the host and its rhythm logic must not
import Streamlit, so a daemon can host the same code later.

## Design

### 1. One owner

A new package, `core/heartbeat/`, with no Streamlit imports, provides the
**host**: the only holder of the live `Person`, the `MetaCognitiveSystem`, the
event log, and her situational state (location, phase, recent iteration
records, last world/needs/action/state responses).

- The Streamlit app obtains the host once per server process
  (`st.cache_resource` or equivalent) and every session uses `host.person`.
  `st.session_state.person` stops being a private copy. Pages that read it
  (`core/pages/3_*`, the rail, the mind card) read the host's.
- The host has one **mind lock** (re-entrant). A beat holds it for the whole
  beat. A chat turn holds it for the whole turn. Saving happens while holding
  it. One mind does one thing at a time.
- A standalone `run_heartbeat.py` replaces `run_scheduler.py` and hosts her
  with no UI (same host class, same loop). `apscheduler` is dropped from
  `requirements.txt`.
- **Only one process may host her.** The host takes a lease in the database
  (owner id plus a timestamp it renews each loop pass). A second process that
  finds a fresh lease does not host: the standalone runner exits with a clear
  message, and the app shows a plain notice that Jenbina is already living in
  another process. A lease not renewed for a few minutes is stale and may be
  taken over.

### 2. One record

Her state stops being tied to an account.

- New storage for the being: one state record (serialized `Person`, location,
  phase and when it began, time of last beat, beat counters, the last few
  iteration records, the last world/needs/action/state responses, the lease)
  and one stream of life events.
- Chat messages stay per account in `conversations`, unchanged.
- Each account's timeline is its own messages merged with her single life
  event stream. Everyone sees the same life.
- The existing `user_state` and per-user `events` rows are left untouched as a
  backup.

**Moving the existing Jenbina.** On first start with no being record, adopt
one existing per-user state as hers: by default the one with the most recorded
experiences (ties go to the lowest user id), overridable by a command-line
option on `run_heartbeat.py`. Her life events come from that same user. From
every other user's saved state, import that user's conversation and social
model so nobody loses their history with her. The adoption runs once and is
logged.

### 3. The rhythm

The host loop wakes every few seconds and asks a pure function, given the
current time and her state, what to do: beat, sleep-beat, or wait. The clock
is injectable so this is testable without threads or real waiting.

- **Awake beat.** One call to `run_single_iteration_headless` on the live
  `Person`, then save. Default interval 15 minutes, set by
  `JENBINA_BEAT_MINUTES`.
- **Conversation has her attention.** No awake beat starts within 3 minutes of
  the last chat message from anyone; the beat is postponed, not skipped.
- **Daily cap.** At most `JENBINA_MAX_BEATS_PER_DAY` awake beats per calendar
  day (default 80). Beyond that she idles until the next day and the heartbeat
  card says so.
- **Failure.** A beat that raises is logged and never kills the loop. After 3
  consecutive failures the interval doubles each time up to 1 hour, and resets
  on the first success. LLM calls made by a beat must have a timeout so a hung
  call cannot hold the mind lock indefinitely.
- **Real time for decay.** Lessons and goal confidence must decay by the real
  hours elapsed since the previous beat, replacing the fixed 0.5 hours per
  call, so a faster heartbeat does not make her forget faster.
- **Situation survives restarts.** Location, recent iteration records and the
  last responses are saved with her state and restored on start.

The headless runner becomes the only iteration. Before the UI copy is deleted
(section 8), the behaviour only it has is ported into the headless runner:
recording simulated social actions in the social interaction tracker, feeding
the social day into the inner monologue, and the `"proactive"` message type.
The host initialises the social interaction tracker like every other
subsystem. The runner also gains an optional status sink (an object with a
`stage(text)` method, like `NullRail`) so the host can publish what she is
doing right now for the UI to show.

### 4. Sleep

She has a phase: `awake` or `asleep`.

Sleep is governed by time, not by the level of the sleep need. The existing
action effects (`rest` +30, a walk +10, decay of only 4 per hour) keep that
need near full most evenings, so a rule keyed to its level would wake her
minutes after she fell asleep.

- **Falling asleep.** When an awake beat's chosen action maps to the `sleep`
  action key and either it is night (`time_of_day == "night"`, which the
  environment simulator produces from 21:00 to 06:00) or her sleep need is
  below 30, she falls asleep and the instant +70 is not applied. A
  sleep-mapped action at any other time is a nap and behaves as today. If she
  has been awake for 20 hours she falls asleep regardless.
- **While asleep.** No decision beats and no LLM calls. On each interval the
  host does bookkeeping only: the sleep need recovers at 12 points per hour up
  to its maximum; all other needs keep decaying by the clock, so she wakes
  hungry.
- **Waking.** She wakes when she has slept 9 hours, or it is no longer night
  and she has slept at least 6 hours, or someone sends her a message. The
  level of the sleep need never wakes her.
- **Woken by a message.** She wakes, the wake is recorded with that reason,
  and the reply is generated with the fact that she was just woken added to
  her context. If she falls asleep again within an hour, it counts as the same
  sleep: the original start time is kept and no second pair of events is
  recorded.
- **Timeline.** Two new event kinds, `sleep` and `wake` ("woke after 7h 40m").
  The sleep portrait is shown while she is asleep.

### 5. Lost time

Lost time means the heart itself was not running (laptop asleep, process
down). It is measured from the last loop pass, which is the lease renewal
time, never from the last beat: back-off, the daily cap and long
conversations all delay beats while the loop keeps running, and none of them
is lost time. On start, and whenever the loop finds that more than 3 beat
intervals passed since its previous pass, that span is lost time:

- Her body was suspended: need clocks are moved to now so no decay is applied
  for the gap.
- If she was asleep and the gap exceeds 9 hours she is awake on return;
  otherwise her phase is kept.
- A `gap` event is recorded on the timeline stating how long she was gone, and
  the gap is put into working memory so her next thoughts can refer to it.

### 6. Chat

`handle_user_input` keeps its shape but works on the host's `Person` under the
mind lock.

- If a beat is in progress when a message arrives, the turn waits for the beat
  to finish and the stage pill says she is finishing what she was doing. With
  the attention rule above this only affects the first message of a
  conversation.
- The session values the chat prompt reads today (`needs_response`,
  `world_description`, `action_decision`, `state_response`,
  `simulation_history`) come from the host's last beat.
- Mood events caused by a chat go to the shared life event stream with no
  names and no message content.
- **Greetings.** The first and return greetings are still generated when a
  person opens the page, but they must never make the page wait and never
  wake her. The greeting takes the mind lock without blocking: if a beat is in
  progress it is retried on a later refresh. If she is asleep no greeting is
  generated and that person's `last_visit_time` is not updated, so the
  greeting comes on their first visit while she is awake. Only a message
  wakes her.

### 7. Many people, one Jenbina

- **Per-person state.** `last_visit_time` and the first-impression flag become
  per person (for example on that person's social model). Each person gets
  their own first greeting, return greeting and first impression. The subtle
  insight limit becomes 3 per person per calendar day and is saved with her
  state.
- **Distinct identities.** Two accounts must never share a conversation or a
  social model. If a new account's display name is already used by another
  account, its key is made distinct.
- **Privacy rule.** She may know that she knows other people, their names, and
  the tone of the day's interactions; this already flows into prompts through
  the social interaction tracker and communication stats. What a person said,
  what she believes about them, and their research dossier must never enter a
  prompt for a different person. The SQLite message history and ChromaDB
  retrieval are already scoped to the account. The state passed into the chat
  prompt is not: it must be changed so the social-cognition part contains only
  the current partner's model. The builder must check every other value that
  reaches a chat, greeting, insight or proactive prompt for the same problem,
  and add a test that fails if another person's message text, beliefs or
  dossier appears in a prompt.
- **Reaching out.** Proactive messages are sent from beats only; opening the
  page no longer triggers one. On a beat whose triggers fire, she messages at
  most one person: among people she has exchanged messages with in the last 7
  days, the one she is closest to, and not anyone she messaged proactively in
  the last 6 hours. The message is stored in that account's conversation.

### 8. The home screen

- Opening the page no longer makes her act. `simulation_auto_started`, "Run N",
  the delay and iteration inputs are removed.
- The UI copy of the iteration (`run_single_iteration`, `run_simulation_loop`
  in `core/ui/simulation.py`) is deleted; its renderers stay.
- The timeline and the status rail refresh themselves every few seconds so
  beats appear without any action from the viewer (Streamlit 1.38 provides
  `st.fragment(run_every=...)`).
- A heartbeat card replaces the run controls on the rail:

  ```
  HEARTBEAT
  ● awake · since 07:12
  last moment 4 min ago · next in 11 min
  [ Step once ]        (admins only)
  ```

  While asleep it reads `● asleep · since 23:40`. It also states when the daily
  cap is reached or the heart is in failure back-off.
- "Step once" asks the host to beat now. It is shown only to admins, using the
  same test as the Admin page (a local request, or the admin account); the
  debug checkbox is on for everyone by default and gates nothing. It ignores
  the interval, the attention rule and failure back-off; it counts toward the
  daily cap and is refused once the cap is reached; it is disabled while she
  is asleep; it waits for the mind lock like anything else. It keeps its label
  so the end-to-end tests, which run locally, still find it. Those tests
  assert a "completed in" pill that only the deleted UI loop drew; they are
  changed to assert the beat's action event appearing on the timeline.
- The Debug page reads the last iterations' debug data from the host, which
  keeps a bounded number in memory.

### 9. Testing

- The rhythm function is tested with a fake clock: intervals, attention
  postponement, daily cap, back-off, falling asleep, each wake condition, and
  lost time.
- The host is tested with a fake iteration function and an in-memory or
  temporary database: single ownership via the lease, save and restore of
  situation, adoption of an existing per-user state, and that a failing beat
  does not stop the loop.
- A test that one person's message content cannot reach another person's
  prompt.
- No test may call an LLM or sleep in real time. Existing tests for the removed
  UI loop and run controls are updated or removed. The unit suite
  (`python -m pytest tests/test_*.py`) must pass.

## Calls made without asking

These are the designer's decisions, not the owner's. Each is cheap to change
before the build.

1. Approach A, the heart inside the app process, over a separate daemon.
2. Beat every 15 minutes while awake, capped at 80 a day; both configurable.
3. A message wakes her, instead of waiting until morning for a reply.
4. Lost time suspends her body; she does not come back starving.
5. The existing Jenbina with the most experiences becomes the one Jenbina.
6. She knows the names of the people she talks to and the tone of those
   interactions across conversations; never the content.
7. Proactive messages go to one person at a time, the closest recent one.
8. She keeps the host machine's clock; no Palo Alto time zone.
9. One mind lock: a message arriving mid-beat waits for the beat to end.
   (Changed after first use: the wait was up to two minutes. A message is now
   answered between the steps of a beat; see the implementation plan.)
10. `run_scheduler.py` is replaced, not kept alongside.
11. Sleep length is set by the clock (6 to 9 hours), not by the sleep need.
12. Opening the page never wakes her and gives no greeting while she sleeps.
13. "Step once" is for admins only and counts toward the daily cap.
14. Subtle insights are limited to 3 per person per day.

## Left to the builder

- Table and column layout for the being's state, events and lease, and whether
  the event log class is reused or extended.
- Module and class names inside `core/heartbeat/`.
- Exact loop wake-up period, lease staleness window, and LLM timeout value.
- How the display-name collision is resolved, as long as identities stay
  distinct and prompts still read naturally.
- Wording and icons of the new timeline events and the heartbeat card, within
  the existing theme.
- How pages obtain the host and how the periodic refresh is wired.
