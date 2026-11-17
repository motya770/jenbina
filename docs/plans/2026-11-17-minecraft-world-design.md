# Minecraft world: Jenbina lives in a real place

Status: design. The owner asked for the design and the implementation in one
request, so building proceeds from this document; the build is then reviewed
with Codex. Date: 2026-11-17. Revised the same day after a design review and a
live test of the bridge (sleep offer, drinking, plans, the variety rule, when
she is logged in, and monsters off by default).

## Intent

Jenbina's world today is a description. Every beat rebuilds a fixed list of
Palo Alto places, asks an LLM to invent a scene and a list of possible actions,
and credits her needs by matching keywords in the action she picked. Nothing
she does changes anything, and nothing is there the next time she looks.

This project gives her a world that exists without her: a private Minecraft
server. What she sees is read from the world, what she can do is what the world
allows, and what happened is what the world reports. Her inventory, the trees
she cut and the place she calls home are still there on the next beat.

The owner chose Minecraft on 2026-11-17 after trying Agent Craft and reviewing
Concordia, Evennia, AI Town and NexWorld. A throwaway test the same day showed
the approach works: she joined a private server, chopped logs and crafted a
pickaxe in under 30 seconds.

## Goals

1. With `JENBINA_WORLD=minecraft`, each beat perceives the Minecraft world,
   chooses one action the world offers, performs it there, and learns the real
   outcome.
2. The world persists between beats: position, inventory, health, food and
   every block she changed.
3. Need satisfaction follows outcomes. A failed action satisfies nothing. Her
   hunger is her body's hunger in the world.
4. Her existing mind is untouched: needs, emotions, inner monologue, goals,
   plans, learning, sleep rhythm and chat all keep working, and the timeline
   shows her Minecraft life.
5. Nothing changes for anyone who does not turn it on. The default world stays
   Palo Alto and the existing tests pass unmodified.
6. A beat costs no more LLM calls than today. (It costs one fewer.)

## Non-goals

- Building a house, farming, smelting, beds and sleeping in the game.
- Other players, other bots, and reading or writing in-game chat.
- Public servers and Microsoft accounts.
- Starting or stopping the Minecraft server or the bridge from Python.
- A 3D view inside the Streamlit app. (The bridge can serve the browser viewer
  on its own port.)
- A map or long-term memory of places beyond one remembered home position.
- Supporting Minecraft versions other than 1.21.4.

## Anti-goals

These would make the project a failure even if it runs:

- The Palo Alto world or any existing test breaking for people who do not use
  Minecraft.
- LLM calls spent on a beat that cannot reach the world.
- She is credited for something that did not happen in the world.
- A beat that hangs: every routine in the world has a time budget.
- Anything from her private conversations reaching the game.
- The Minecraft server or the bridge listening beyond this machine by default.

## How it works today

`run_single_iteration_headless` in `core/simulation_runner.py` runs a beat:

1. `create_comprehensive_world_state(person_location=...)` rebuilds a
   `WorldState` from static Palo Alto data, and `get_world_state_summary`
   flattens it for the timeline and the rail.
2. Three LLM calls run in parallel: needs, the world description (which
   invents `list_of_actions` and `list_of_descriptions`), and the inner
   monologue.
3. `create_meta_cognitive_action_chain` picks one action as free text from
   `list_of_actions` in three more LLM calls.
4. `match_action_key(chosen)` maps that text to a need-satisfaction key by
   keyword, and `_detect_location_from_action` moves her if the text names a
   known place.
5. Safety check, emotion analysis, state analysis, learning, goals and plans
   follow, then the host saves her.

`JenbinaHost._beat` in `core/heartbeat/host.py` builds the `context` dict for
the runner and keeps `Situation` (location, history, last responses) between
beats.

## Approaches

**A. A Node bridge beside the Python app (chosen).** Minecraft bots are written
with Mineflayer, a Node library. A small Node process logs in as Jenbina and
exposes a local HTTP API with two verbs, observe and act. Python stays Python
and talks to it over localhost. The bridge holds all Minecraft knowledge
(path-finding, digging, crafting); Python holds all of her mind.

**B. Mineflayer inside Python through a JavaScript bridge package.** One
process, but it puts a Node runtime inside the Streamlit process, makes the
heartbeat depend on a cross-language callback layer, and cannot be tested or
restarted separately. Rejected.

**C. Let Mindcraft drive her.** Mindcraft is a complete Minecraft agent with its
own LLM loop. It would replace her mind instead of connecting it. Rejected.

A is also what the test on 2026-11-17 already proved, with the same libraries.

## Design

### Pieces

```
Minecraft server 1.21.4  <--game protocol-->  Node bridge  <--HTTP, localhost-->  Python beat
(minecraft/server, ignored)                   (minecraft/bridge)                  (core/environment/minecraft)
```

- **Server.** The official Mojang server for 1.21.4, in offline mode, bound to
  `127.0.0.1`, with `pause-when-empty-seconds=10`, `difficulty=easy` and
  `spawn-monsters=false`. Easy difficulty gives her a body that gets hungry.
  Monsters are off because the live test on 2026-11-17 showed what they do: at
  night she was attacked while digging a shelter, died, and lost everything
  she carried. An owner who wants that danger can switch them on. Version 1.21.4 is the newest
  one both Mineflayer and its browser viewer support; 26.1 was tried and
  crafting misbehaved. `minecraft/setup_server.sh` downloads it from Mojang,
  checks the checksum from Mojang's manifest, and writes `server.properties`.
  It accepts the Minecraft EULA only when run with `--accept-eula`.
- **Bridge.** `minecraft/bridge/`: Mineflayer with the pathfinder and
  collect-block plugins. It listens on `127.0.0.1:3010`.
- **World adapter.** `core/environment/minecraft/`: a client for the bridge,
  the code that turns an observation into a scene and a list of actions, and
  the provider the runner calls.

The owner starts the server and the bridge. Python never launches them.

### One beat in Minecraft

1. **Look.** The provider asks the bridge to start a session (log in), takes
   the observation that comes back, and ends the session again. If this fails,
   the beat fails here, before any LLM call, with `WorldUnavailable`. The
   host's existing failure back-off applies. She does not fall back to Palo
   Alto. She is logged out while she thinks, so she never stands idle in a
   running world for the minute her decision takes.
2. **Body.** Her `hunger` need is set from the body's food bar
   (`food / 20 * 100`), and hunger is skipped in the real-time decay for this
   beat. The first observation ever stores her home position.
3. **Scene.** Code builds a `WorldState` from the observation using the
   existing dataclasses, so `get_world_state_summary`, the rail and the
   timeline work unchanged. Code also builds the scene description and the list
   of available actions. The world-description LLM call is skipped.
4. **Decide.** The existing three-step decision chain picks one action from
   that list, as today. Its "choose something different from your recent
   actions" rule is given only her single most recent action in this mode:
   with about a dozen fixed labels, the usual six would forbid most of them.
5. **Act.** The chosen text is resolved to an offered action. The provider
   starts a session, sends the action to the bridge, which runs a bounded
   routine and reports the outcome, and ends the session in a `finally`. With
   nobody online the server pauses, so the world waits for her next beat.
6. **Consequences.** Needs are credited from the action's need key only if the
   outcome is ok. The outcome is added to the action record, the timeline, the
   emotion analysis and her working memory, so the next beat knows what
   happened. Her location becomes the place label of where she now stands.
7. **Plans.** The planner is told which actions this world offers, so the
   steps of new plans are things she can do here. Plans she brought from Palo
   Alto are replaced by the planner's normal replan cycle.

The safety (Asimov) check keeps its place after the action, as today. Every
action here comes from a closed list written in code, and there are no people
or other agents in the world to harm. When either of those changes, the check
must move in front of the action.

### Two clocks

Her day is the real clock. The heartbeat decides when she sleeps, and while she
sleeps she is not in the world. `WorldState.time_data` therefore keeps the real
time of day, so the existing sleep rule and prompts stay consistent.

The Minecraft sky is described separately in the scene ("The sun is up here" /
"It is dark here, and monsters are about"). It affects which actions are
offered (shelter at night), not when she sleeps.

"Go to sleep" is offered exactly when the existing rule (`should_fall_asleep`)
would let her fall asleep: sleep is enabled and either her own clock says
night or her sleep need is low. It maps to the existing `sleep` key, so
choosing it always runs the existing fall-asleep path. It is never offered when
choosing it would only credit sleep while she stays awake.

### Observation

`GET /observe` returns:

```json
{
  "position": {"x": -144, "y": 65, "z": 157},
  "biome": "forest", "temperature": 0.7,
  "sky": {"is_day": true, "time_of_day": 2517, "raining": false},
  "health": 20, "food": 17,
  "inventory": {"oak_planks": 44, "wooden_pickaxe": 1},
  "nearby": {
    "logs": 6, "stone": true, "water": false,
    "animals": [{"name": "cow", "distance": 12}],
    "hostiles": [{"name": "zombie", "distance": 20}],
    "crafting_table": true
  },
  "craftable": ["stick", "wooden_axe", "stone_pickaxe"],
  "sheltered": false
}
```

`craftable` is limited to the bridge's whitelist of items and to what her
inventory can make right now.

### Actions

Each is one bounded routine in the bridge with a default budget of 45 seconds.
The label is what her mind reads and chooses. An action is offered only when
the observation says it is possible.

| Action | Label | Offered when | Need key if ok |
|---|---|---|---|
| `look_around` | Look around and take in the surroundings | always | `explore_meaning` |
| `explore` | Explore to the north / east / south / west | always (four labels) | `learn_new_things` |
| `gather_wood` | Chop wood from the trees nearby | logs within reach of sight | `work_on_goals` |
| `craft` | Craft a wooden pickaxe (one label per craftable item, at most four) | item is craftable | `develop_skills` |
| `mine_stone` | Mine stone with the pickaxe | she holds a pickaxe and stone is near | `work_on_goals` |
| `hunt` | Hunt the cow nearby for food | an animal is near | `work_on_goals` |
| `eat` | Eat the beef you are carrying | she carries food and food is below 20 | `eat` |
| `drink` | Drink from the water nearby | water is near | `drink` |
| `take_shelter` | Dig a burrow and shelter in it | a monster is near and she is not sheltered | `find_shelter` |
| `go_home` | Walk back home | she is more than 24 blocks from home | `find_shelter` |
| `rest` | Rest for a while | always | `rest` |
| (no bridge call) | Go to sleep for the night | her clock says evening or night, or sleep is low | `sleep` |

Craft whitelist: planks, stick, crafting table, wooden and stone pickaxe, axe
and sword, furnace. The craft routine places her crafting table when a recipe
needs one and none is within reach.

Some needs have no action in this world: order, respect, creativity and love.
They keep decaying and are met, as today, only through her conversations with
people. This is accepted for the first version.

`POST /act` returns:

```json
{"ok": true, "name": "gather_wood", "summary": "Chopped 4 oak logs.",
 "gained": {"oak_log": 4}, "lost": {}, "died": false,
 "duration_ms": 21400, "observation": { }}
```

`summary` is one plain sentence written by the bridge from what actually
changed. `observation` is a fresh observation after the action.

### Resolving her choice

The decision chain returns free text. The provider matches it to the offered
labels: exact match ignoring case and punctuation, then containment, then the
closest label by `difflib` with a ratio of at least 0.6. If nothing matches,
nothing is sent to the world, the outcome is "not ok" with the summary "I could
not work out how to do that here", and no need is credited.

### Places

Her location is a short, stable label: `Home` within 12 blocks of her home
position, otherwise the biome in plain words (`Birch forest`). A move is
recorded only when the label changes.

### Death

If the bridge reports that she died during an action, the outcome says so, her
`security` need drops by 30 points, and a note goes into working memory for the
next three beats. Minecraft respawns her; her dropped items may be lost.

### What is stored

`Situation` gains one field, `world: dict`, saved with the rest of her
situation. It holds `{"minecraft": {"home": [x, y, z], "deaths": 0}}`. Old
saved situations without it load with an empty dict.

### Watching her

The bridge serves the browser viewer when `VIEWER_PORT` is set. The viewer
library listens on all network interfaces, so it is off by default.

She is in the world only during a beat, so the view is live for about a minute
every beat interval. `JENBINA_MINECRAFT_STAY_ONLINE=1` keeps her logged in
between beats so she can be watched continuously. The world then keeps running
while she stands still, which on any difficulty above `peaceful` means monsters
can reach her at night; the setup notes say so.

### Settings

| Variable | Read by | Default | Meaning |
|---|---|---|---|
| `JENBINA_WORLD` | Python | `palo_alto` | `minecraft` turns this on |
| `JENBINA_MINECRAFT_BRIDGE_URL` | Python | `http://127.0.0.1:3010` | where the bridge listens |
| `JENBINA_MINECRAFT_STAY_ONLINE` | Python | `0` | `1` keeps her logged in between beats |
| `MC_HOST`, `MC_PORT`, `MC_USERNAME`, `MC_VERSION` | bridge | `127.0.0.1`, `25565`, `Jenbina`, `1.21.4` | the server to join |
| `BRIDGE_PORT` | bridge | `3010` | bridge HTTP port, bound to `127.0.0.1` |
| `VIEWER_PORT` | bridge | unset | serve the browser viewer on this port |

### Code changes

- `core/environment/minecraft/` (new): `bridge_client.py`, `scene.py`,
  `provider.py`, `__init__.py`.
- `core/simulation_runner.py`: when `context["world_provider"]` is set, use it
  for the world state, the scene, the action outcome, the need key and the
  location. With no provider the code path is exactly today's.
- `core/heartbeat/rhythm.py`: `Situation.world`.
- `core/heartbeat/host.py`: accept `world_provider`, pass it and
  `situation.world` to the runner.
- `core/ui/shared_init.py`, `run_heartbeat.py`: build the provider from the
  environment.
- `core/timeline/events.py`, `core/timeline/recording.py`,
  `core/ui/timeline.py`: an optional `outcome` on action events, shown as
  "What happened" in the row's details.
- `core/ui/rail.py`: a body line (health and food) when the world reports one.
- `minecraft/bridge/` (new): `bridge.js`, `actions.js`, `observe.js`,
  `package.json`, lock file.
- `minecraft/setup_server.sh`, `minecraft/README.md` (new).
- `.gitignore`, `.env.example`, `CLAUDE.md`.

### Testing

- Python unit tests use a fake bridge and never touch the network: scene and
  action building, label resolution, outcome to need key, hunger from the food
  bar, home and place labels, the runner with a provider (no world LLM call,
  the session always ends, nothing credited on failure), the host passing the
  provider and saving `Situation.world`, and the timeline and rail additions.
- The bridge's pure helpers (shaping an observation, writing a summary from an
  inventory difference) have Node tests run with `node --test`. CI does not run
  them; it has no Node step today.
- The bridge's routines need a live server and are checked by hand with the
  procedure in `minecraft/README.md`: one real beat with
  `python run_heartbeat.py --once`.

## Risks

- **Routines are flaky.** Path-finding and digging sometimes fail or time out.
  Every routine is bounded and reports failure honestly, and a failed action
  costs her one beat.
- **Library versions.** Mineflayer and the viewer lag behind Minecraft
  releases. The server is pinned to 1.21.4 and the bridge's dependencies are
  locked.
- **She can die.** On `easy` difficulty monsters come at night. The burrow
  action and the fact that she is offline between beats limit this; the setup
  notes recommend `easy` and explain `peaceful`.
- **Two processes to run.** If the server or bridge is down her beats fail and
  back off until they return. The rail already shows the back-off note.

## Left to the builder

- Exact wording of scene descriptions and outcome summaries.
- How the bridge chooses which tree, animal or stone to go for.
- The nominal temperature shown per biome on the rail.
