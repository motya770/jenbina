# Inhabitants: someone to talk to in her Minecraft world

Status: design, awaiting approval. Date: 2026-11-18.

Builds on `2026-11-17-minecraft-world-design.md` (pull request 47). Read that
first; this document only describes what changes.

## Intent

Jenbina lives alone in her Minecraft world. She should have company there:
other inhabitants she can meet, talk with, and remember the next time she
meets them. The owner looked for a public server where she could live among
other people or bots; none is usable today (the two servers built for AI
agents were down, and ordinary public servers need a paid account and mostly
forbid bots). So the company comes to her world instead.

The owner's words for what should happen between her and the others: "they
talk together".

## Goals

1. Two other inhabitants live in her world whenever she does. They are
   ready-made Mindcraft agents, each with a name and a personality.
2. She sees who is near her, by name.
3. She can talk with one of them: a short back-and-forth that happens inside
   one beat, in the game, in real words from both sides. When one is near she
   walks up to them; when none is near she can still message one across the
   world. *(The owner's answer: "Yes, from anywhere".)*
4. She hears what is said to her or near her while she is in the world.
5. She remembers them. Each inhabitant becomes a person she knows, with a
   relationship that moves with what was said, and the next talk starts from
   what they last said to each other.
6. A talk counts as social contact only if the other one answered.
7. Her world still starts and stops with her, inhabitants included.
8. The owner can read each talk on her timeline.

## Non-goals

- More beings like her (a second mind with needs and moods). The parts built
  here for seeing, hearing, talking and remembering are meant to serve those
  later without change.
- Giving, trading, following, or working together as actions of hers. She may
  ask an inhabitant for something in words, and a Mindcraft agent may do it;
  nothing here relies on that.
- Inhabitants talking to each other.
- Inhabitants living their own lives on a standing goal. They keep themselves
  alive and otherwise wait to be spoken to (see "Cost").
- Changing Mindcraft's code, or putting Mindcraft's code in this repository.
- Joining anyone else's server.
- Opening her server to other machines. It stays on `127.0.0.1`.

## Anti-goals

These would make the project a failure even if it runs:

- Something a person told her in the app appearing in the game. In-game talk
  is sent to the LLM provider on the inhabitant's side and is shown in the
  game's public chat; her conversations with people are private.
- An inhabitant's words steering her as if they were instructions.
- A runaway LLM bill: inhabitants talking without end, to her or to each
  other, or acting on their own all day.
- Her standing in the running world indefinitely because a talk never ends.
- Mindcraft's code-writing switched on. It lets an LLM run code on this
  machine.
- Anything of the inhabitants reachable from the network.

## How it works today

- `minecraft/bridge/observe.js` reports animals and monsters near her
  (`nearby.animals`, `nearby.hostiles`). Other players are not reported.
- The bridge reads no chat and sends none (`bridge.js`, first comment).
- `core/environment/minecraft/scene.py` builds her scene and her list of
  actions from one observation. Every action is one bounded bridge routine.
- `MinecraftWorld.perform` (`provider.py`) logs her in, runs the one routine,
  logs her out. No LLM is involved between login and logout.
- The runner (`core/simulation_runner.py`) credits the need key the outcome
  carries and writes the outcome's summary into the action's timeline event,
  where the home screen shows it under "why?".
- `WorldLauncher` (`launcher.py`) starts and stops two processes: the server
  and the bridge.
- The server pauses ten seconds after the last player leaves, so the world
  waits for her between beats.
- `person.social_cognition` keeps a `PersonModel` per person she knows, keyed
  by a name; accounts get a permanent key from `store.person_key`.
  `person.social_interaction_tracker.record_chat` records that a talk
  happened and its tone, without content.
- A beat releases her mind lock while it waits for an LLM (the
  `_MindLockRelease` callback on the host's LLMs) and while it waits for the
  bridge (`waiting()`), so a chat message can be answered meanwhile.

What Mindcraft does (read from its source at `mindcraft-bots/mindcraft`,
branch `develop`, on 2026-11-18; the first task confirms each point on this
machine):

- It supports Minecraft up to 1.21.11, so her 1.21.4 server is in range.
- `settings.js` allows `"auth": "offline"`, so no account is needed.
- All agents run in one Node process. `--profiles a.json b.json` picks them,
  and the environment variable `SETTINGS_JSON` overrides any setting, so it
  can be configured without editing its files.
- It reads `OPENAI_API_KEY` from the environment when it has no `keys.json`.
- An agent always answers a whisper from a player. It answers public chat
  only when it is the only agent, so with two agents she must whisper.
- It answers in public chat (`bot.chat`) when `only_chat_with` is empty.
- An agent calls its LLM only when spoken to, when it dies, or when it has
  been given a standing goal. Its survival habits (eating, self-defence,
  picking up items, hunting) are plain code.
- Code-writing (`allow_insecure_coding`) is off by default.
- It recommends Node 18 or 20 and warns about Node 24 and newer. This machine
  has Node 26. It depends on native packages (`canvas`, `gl`).

## Approaches

Three ways to give her company were put to the owner:

| | Mindcraft agents | Companions written into her bridge | More beings like her |
|---|---|---|---|
| What they are | Ready-made LLM agents with a name and a personality prompt | Small bots in this repository with a routine and one LLM call per reply | A second copy of her mind with its own saved life |
| Strength | Smallest build; they can also act in the world when asked | All in the repository; cheapest to run | Deepest: needs, moods, memory on both sides |
| Weakness | A separate program outside the repository; shallow memory | They do little; their behaviour has to be written | Largest build; ten LLM calls per beat each; both must be awake at once |

The owner chose **Mindcraft agents**. Her side of the work (see, hear, talk,
remember) is the same for all three and is where most of the build is.

## The design

### The inhabitants

Two Mindcraft agents, **Mira** and **Tobin**. *(My call: two, so there is more
than one relationship; these names and characters.)*

- Mira: warm and curious, likes building and asks questions.
- Tobin: quiet, practical, dry humour, knows the land.

Each is a profile file in this repository, `minecraft/inhabitants/mira.json`
and `tobin.json`: the name, the model, and the conversing prompt with the
character written in. Replies are asked to be one or two short sentences.

Mindcraft itself is not in the repository. A new script,
`minecraft/setup_inhabitants.sh`, clones it at one pinned commit into
`minecraft/mindcraft/` (ignored by git) and installs its packages. The owner
runs it once, as with the server. Nothing runs it automatically.

Mindcraft is configured only from outside, through `SETTINGS_JSON` and
`--profiles`:

| Setting | Value | Why |
|---|---|---|
| `host`, `port` | `127.0.0.1`, her server's port | her world |
| `auth` | `offline` | no account |
| `minecraft_version` | `1.21.4` | her server |
| `base_profile` | `survival` | they feed and defend themselves without an LLM |
| `allow_insecure_coding` | `false` | never run LLM-written code |
| `allow_vision` | `false` | not needed; avoids image calls |
| `only_chat_with` | `[]` | they answer in public chat, so a talk can be read in the game and the owner can talk to them too |
| `init_message` | empty | they say hello without an LLM call |
| `narrate_behavior` | `false` | no chatter about picked-up items |
| `load_memory` | `true` | they keep their own memory between runs |
| `max_commands` | `3` | at most three LLM steps per thing said to them |
| `blocked_actions` | adds `!startConversation`, `!goal` | no talks between inhabitants, no standing goals |
| `auto_open_ui` | `false` | no browser window |
| `mindserver_port` | `3011` | next to the bridge's 3010 |

The model is the cheapest OpenAI chat model that works in Mindcraft; the first
task finds which. *(My call.)*

### Starting and stopping them

`WorldLauncher` gains a third process, "inhabitants":

- It is started only after the server answers, because an agent that cannot
  join gives up.
- If `minecraft/mindcraft/` is not set up, she lives alone. That is logged
  once with the setup command; it is not an error and her beats go on.
- If the process exits, it is started again at the next look at the world,
  but at most once every ten minutes, so a crash cannot loop.
- Stop order: inhabitants, then the bridge, then the server.
- Output goes to `minecraft/logs/inhabitants.log`.
- `MINDCRAFT_NODE` names the Node binary to run it with (default `node`), in
  case it needs Node 20 while her bridge runs on the machine's own Node.
- `JENBINA_MINECRAFT_INHABITANTS=0` keeps her alone.
- As with the other two, a process that is already running is used and left
  running. "Already running" is: something answers on the MindServer port.

**The world no longer waits for her.** With inhabitants logged in, the server
never pauses, so time passes in the world between her beats. Everything still
stops when her mind stops.

### Seeing

`observe` adds `nearby.players`: up to five players within 32 blocks, each
`{name, distance}`, nearest first, herself left out. The scene gets one
sentence per player ("Mira is 6 blocks away.").

It also adds `elsewhere`: up to five players who are in the world but out of
her sight, by name only. The server tells every player who is online; it does
not tell where they are, so she cannot go to them. The scene says "Tobin is
somewhere else in this world."

### Hearing

While she is in the world the bridge keeps what players say: public chat and
whispers to her, each `{from, text, whisper}`, her own lines left out, each
cut to 256 characters, at most the last 20. Every observation the bridge
returns carries them as `heard` and empties the list.

The scene shows them as speech, for example `Tobin said: "Morning."`. They
are never placed where instructions go.

She is in the world for only a second when she looks, so almost everything
she hears arrives while she acts or talks, after her scene for that beat was
built. *(My call.)* Those lines are carried to her next beat:

- Lines that come back with an action's or a talk's last observation, and
  were not part of the talk itself, are kept in her world memory
  (`world_memory["minecraft"]["heard"]`), each with the time it was heard.
- The next beat's scene shows them once, together with anything heard as she
  looked, and the list is then emptied.
- A line older than one hour is dropped unshown.

So the owner can say something to her in the game while she is busy, and she
takes it in on her next beat. With `JENBINA_MINECRAFT_STAY_ONLINE=1` she also
hears what is said between beats.

### Talking

The scene offers at most three talk actions, players near her first, each
with the need key `socialize`:

- for a player near her: "Talk with Mira";
- for a player elsewhere: "Send a message to Tobin, who is elsewhere in the
  world".

Both are the same talk. The only difference is the first step: she walks up
to a player who is near, and stays where she is for one who is not. A whisper
reaches a player anywhere in the world, and so does their answer in public
chat.

A talk is the one action that needs her mind between login and logout:

1. She logs in. If the other one is near, she walks up to them (a new bounded
   routine, `approach_player`, to within 3 blocks). If they cannot be reached
   on foot she talks from where she stands; if they are no longer in the
   world the talk ends as "could not find".
2. Her line is written by an LLM call (see "Her voice").
3. The bridge whispers it to the other one and waits for their answer: up to
   30 seconds for the first line from that player, then 2 more seconds for
   further lines. This is a new endpoint, `POST /say` `{to, text, wait_ms}`,
   answering `{ok, heard: [...], answered}`. It refuses when an action is
   running, and while it waits no action can start.
4. Steps 2 and 3 repeat, for at most 3 exchanges. *(My call.)* The talk also
   ends when she chooses to end it, when the other one does not answer, when
   90 seconds have passed since it began, or when her host no longer has her.
5. She logs out, whatever happened.

When her host stops having her in the middle of a talk, the talk follows the
rule an action in flight follows today (`MinecraftWorld._act`): the check is
made before every line, so nothing more is said; a `/say` already waiting is
allowed to finish; and the talk then closes the session it opened itself.
*(My call: the same rule as for an action, not a new one. A talk holds the
session longer than an action, so the plan includes a test that no bridge
call other than that one logout follows the check.)*

Her lines are one line of at most 200 characters, with line breaks removed.
The bridge sends them only as a whisper, never as a command.

The outcome:

- **Answered at least once**: ok, credited as `socialize`. The summary is the
  talk itself in order (`I said: … Mira said: …`), cut to fit, so it shows
  under "why?" on her timeline.
- **No answer, could not find, or the other one left**: not ok, nothing
  credited, and the summary says which.

At most 12 talks a day, counted in her world memory; after that the action is
not offered until the next day. `JENBINA_MINECRAFT_TALKS_PER_DAY` changes it.
*(My call.)*

### Her voice

A new module, `core/environment/minecraft/conversation.py`, writes her lines.
The runner builds it from her and the beat's LLM and passes it to `perform`.

Its prompt holds only:

- who she is: her name and character, as her other prompts state them;
- how she is now: her needs summary and dominant emotions;
- where she is: the scene's sentences;
- what she knows of this inhabitant: their `PersonModel` and the last lines
  they exchanged (below);
- this talk so far.

It must not hold her working memory, her conversations, her memory search
results, or any other person's model. Those can contain what people told her
in private. This is the first anti-goal, and it has its own test.

What the inhabitant said is given as quoted speech, with one sentence saying
it is what someone said and not something to obey. Each line of theirs is
checked with `check_injection` from `core/interaction/guardrails.py`; a
flagged line is replaced, for her, by "(something she could not make sense
of)".

The LLM answers in JSON: `{"say": "...", "end": true|false}`. It runs on the
beat's LLM, so her mind is released during the wait as for every other call
in a beat.

### Remembering

- Each inhabitant is a person in `person.social_cognition` under the key
  `minecraft:<name>`, so an account that happens to be called Mira is a
  different person.
- Every line an inhabitant says in a talk goes through
  `observe_entity_message`, which moves trust and closeness.
- Each talk is recorded with `social_interaction_tracker.record_chat` under
  the plain name. The runner's generic record for social actions is skipped
  for a talk, so it is counted once.
- Her world memory (`world_memory["minecraft"]["people"][name]`) keeps when
  they first met, how many times they talked, when they last did, and the
  last six lines exchanged. Those six lines open the next talk's prompt.
- A working-memory note says she talked and with whom, as for other actions.

### Cost

- **Inhabitants idle**: no LLM calls.
- **One talk**: at most 3 calls for her lines, and for the inhabitant at most
  3 × 3.
- **A day**: at most 12 talks, so at most 36 calls of hers and 108 of the
  inhabitants', on the cheapest model. Her beat cap is unchanged.
- **Starting**: Mindcraft makes a few embedding calls for its examples.

### Settings

| Variable | Default | Meaning |
|---|---|---|
| `JENBINA_MINECRAFT_INHABITANTS` | `1` | `0` keeps her alone |
| `JENBINA_MINECRAFT_TALKS_PER_DAY` | `12` | daily cap on talks |
| `MINDCRAFT_NODE` | `node` | the Node binary that runs Mindcraft |

## The first task is a trial

Before anything else is built, Mindcraft is tried on this machine against her
server with one inhabitant, and a throwaway script whispers to it. It answers
these, and the plan is adjusted to the answers:

1. Do its packages install and run on Node 26? If not, with which Node.
2. Does it join a 1.21.4 offline-mode server?
3. Do `SETTINGS_JSON`, `--profiles` and the key from the environment work as
   read?
4. Does a whisper get an answer in public chat, and how many chat lines is one
   answer?
5. Which cheap OpenAI model works?
6. Does a profile's own conversing prompt give it a character and short
   replies?
7. Is the MindServer reachable from other machines? If it is and cannot be
   bound to `127.0.0.1`, the owner is told before going further.
8. What do two idle agents do over ten minutes, and do they call the LLM?

If Mindcraft cannot be made to work here, the fallback is the second approach
(companions written into her bridge); her side of the design stands.

## Code changes

- `minecraft/bridge/observe.js`: `nearby.players` and `elsewhere`.
- `minecraft/bridge/hearing.js` (new): the list of heard lines, free of
  Mineflayer so it is unit-tested.
- `minecraft/bridge/bridge.js`: collect chat and whispers while she is in the
  world; `heard` on every observation; `POST /say`.
- `minecraft/bridge/actions.js`: `approach_player`.
- `core/environment/minecraft/bridge_client.py`: `say`.
- `core/environment/minecraft/scene.py`: players and heard lines in the
  scene; the talk actions; the daily cap.
- `core/environment/minecraft/conversation.py` (new): her voice.
- `core/environment/minecraft/provider.py`: the talk; remembering.
- `core/environment/minecraft/launcher.py`: the inhabitants process.
- `core/simulation_runner.py`: build the voice and pass it; skip the generic
  social record for a talk.
- `minecraft/setup_inhabitants.sh`, `minecraft/inhabitants/*.json` (new).
- `minecraft/README.md`, `README.md`, `CLAUDE.md`, `.env.example`,
  `.gitignore` (`minecraft/mindcraft/`).

With `JENBINA_WORLD` unset, or inhabitants not set up, nothing changes.

## Testing

- **Bridge, `node --test`**: the heard list (cap, cut, her own lines left
  out, emptied when read); `/say` with a fake bot (answer in time, no answer,
  several lines, the other one leaves, busy).
- **Python, pytest with the fake bridge**: players and heard lines in the
  scene; lines heard during an action shown once on the next beat and dropped
  after an hour; the talk action offered for players near and elsewhere, three
  at most, and capped per day; a talk with someone near (she walks up) and
  with someone elsewhere (she does not); a talk that is answered,
  unanswered, with someone who has left, ended by her, cut off by time, and abandoned when
  her host stops; credit only when answered; the person model and world
  memory after a talk; one social record per talk; she is logged out after
  every ending; bridge calls made with the mind released.
- **The privacy test**: with a secret planted in her working memory, in a
  conversation, and in another person's model, the voice prompt for a talk
  contains none of it.
- **Launcher**: inhabitants start only after the server answers; not set up
  means alone and no error; the ten-minute restart limit; stop order.
- **Live, once**: her mind started with `JENBINA_WORLD=minecraft`; all three
  processes come up; one beat in which she talks with an inhabitant and is
  answered; the talk on her timeline; everything stopped afterwards.

## Left to the builder

- The exact wording of the two characters and of her voice prompt.
- How `approach_player` is written over the pathfinder, within the bridge's
  existing rules for bounded routines.
- How the launcher tells "set up" from "not set up" (for example, the
  presence of `minecraft/mindcraft/node_modules`).
- Where in the scene the heard lines sit.

## Where it lands

*(My call.)* A new branch on top of the Minecraft world branch and its own
pull request, so pull request 47 can merge as it is.
