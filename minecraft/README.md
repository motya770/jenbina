# Jenbina's Minecraft world

With `JENBINA_WORLD=minecraft`, Jenbina lives in a private Minecraft world
instead of the described Palo Alto one. Each beat she looks at the real world,
picks one of the actions it offers, does it there, and is credited for what
actually happened. Her inventory, her body and everything she changed are
still there on the next beat.

She need not live there alone: Mira and Tobin can live in the same world, and
she can talk with them. See [Company](#company).

The designs are in
[docs/plans/2026-11-17-minecraft-world-design.md](../docs/plans/2026-11-17-minecraft-world-design.md)
and
[docs/plans/2026-11-18-minecraft-inhabitants-design.md](../docs/plans/2026-11-18-minecraft-inhabitants-design.md).

## What runs

| Piece | Where | Started by |
|---|---|---|
| Her mind | the app or `run_heartbeat.py` | you, as before |
| Minecraft server 1.21.4 | `minecraft/server/` (ignored by git) | her mind, when it starts |
| Bridge (Node, Mineflayer) | `minecraft/bridge/` | her mind, when it starts |
| Inhabitants (Mindcraft), optional | `minecraft/mindcraft/` (ignored by git) | her mind, once the server answers |

Her world starts with her. When her mind starts, it starts the server and the
bridge if they are not already running, and when it stops it stops the ones it
started. One that you started yourself is left running. Before each look at
the world she checks that both are up and starts again whichever went down.
The inhabitants are started the same way when they are set up; without them
she lives alone and nothing else changes.

If the world cannot be started or reached, her beats fail before any LLM call
and back off until it returns. Set `JENBINA_MINECRAFT_AUTOSTART=0` to start
the two yourself instead.

## Requirements

- Java 21 or newer
- Node 18 or newer
- No Minecraft account. You only need to buy Minecraft if you want to walk
  around in her world yourself.

## Set up, once

```bash
./minecraft/setup_server.sh
```

This downloads the official server from Mojang, checks it against Mojang's
checksum, and writes `server.properties`. The server will not start until you
accept the [Minecraft EULA](https://www.minecraft.net/en-us/eula):

```bash
./minecraft/setup_server.sh --accept-eula
```

Then install the bridge's packages:

```bash
cd minecraft/bridge && npm install
```

## Run

Start her mind; the world comes up with it. For one beat:

```bash
JENBINA_WORLD=minecraft python run_heartbeat.py --once
```

Or with the app:

```bash
JENBINA_WORLD=minecraft streamlit run core/app.py
```

`run_heartbeat.py` also reads a `.env` file in the project root, so the
variable can live there. The app reads only the environment it is started
with.

The first beat waits for the server, which takes about half a minute, and
longer the first time, when it makes the world. What the server and the bridge
print goes to `minecraft/logs/server.log` and `minecraft/logs/bridge.log`.

`--once` starts the world, takes one beat and stops the world again. To keep
the world up between such beats, start it yourself first; she then uses the
running one and leaves it running:

```bash
./minecraft/run_server.sh
```

```bash
node minecraft/bridge/bridge.js
```

The setup is never done for you: if the server is not set up, the EULA is not
accepted, or the bridge's packages are missing, her mind says which step
above is missing and starts nothing.

If her mind is killed outright, the server, the bridge and the inhabitants it
started keep running. The next start finds them, uses them, and leaves them
running when it stops; stop them yourself with `pkill -f "main.js --profiles"`,
`pkill -f bridge.js` and `pkill -f server.jar`.

## Company

Mira and Tobin are two others who can live in her world. Each is an agent of
[Mindcraft](https://github.com/mindcraft-bots/mindcraft), someone else's
open-source program, with its own small LLM (`gpt-5-nano`). Mira is warm and
curious and likes building; Tobin is quiet and practical, with a dry sense of
humour. Their characters are in `minecraft/inhabitants/`.

Set them up once:

```bash
./minecraft/setup_inhabitants.sh
```

This downloads Mindcraft into `minecraft/mindcraft/` at one fixed commit and
installs its packages. Mindcraft needs Node 20; when your Node is another
version, the script also installs a private Node 20 into
`minecraft/mindcraft-node/`. Nothing of Mindcraft is changed or committed
here. Its packages are whatever npm resolves on the day, except Mineflayer,
which is pinned to the version Mindcraft patches.

After that they start with her world, a little after the server answers, and
stop with it. They take about half a minute to join. A single `--once` beat
that has to start the world is over before they arrive, so to try a talk with
`--once` beats keep the world up yourself (see [Run](#run)), or run her
continuously. They need `OPENAI_API_KEY` in the environment her mind is
started with; it is the only key of hers they are given. What they print goes
to `minecraft/logs/inhabitants.log`.

**What she does with them.** Her scene says who is near and who is elsewhere
in the world, and quotes what they said since she last looked. She can choose
to talk with one: she walks up if they are near, or messages them across the
world, and they exchange up to three lines each inside that one beat. She
remembers who she has met and the last things they said to each other, and a
talk counts as social contact only when she was answered. A talk appears on
her timeline as an action whose outcome is what was said.

**What stays private.** Her lines in the game are written by a prompt that
reads her name, her lowest needs, her strongest feelings, the scene, what she
knows of that inhabitant and their own earlier words. It never reads her
conversations with people, her working memory or her memories, so nothing you
tell her in the app can be repeated in the game. What an inhabitant says
reaches her only as quoted speech; it never chooses her actions.

**What it costs.** An inhabitant asks its LLM only when it is spoken to: one
call for each line of hers. Ten idle minutes cost nothing. She begins at most
twelve talks a day. As a last guard, her mind counts the inhabitants' LLM
calls from their log and stops them when they make more than 60 in an hour;
they then stay stopped until her mind is started again.

**Talking to them yourself.** If you own Minecraft, join `127.0.0.1:25565`
and whisper: `/msg Mira hello`. They answer in the public chat. With both in
the world they answer whispers only.

**Limits worth knowing.**

- They do not hunt and do not fight: left on, hunting took the animals she
  lives on, and fighting got one of them thrown out of the world.
- They never write or run code (`allow_insecure_coding` is off, always), never
  start a talk themselves, and are told to refuse a task without an end.
  Mindcraft cannot switch its endless-goal command off; the hourly limit above
  is what bounds it. If that limit ever stops them, delete
  `minecraft/mindcraft/bots/<Name>/memory.json` before the next start so an
  unfinished goal is not picked up again.
- If one of them drops out of the world for good, all are started again, no
  sooner than ten minutes after the last start.
- Mindcraft keeps each one's own notes in `minecraft/mindcraft/bots/`.
- Its control page listens on `localhost:3011` only.

## Watching her

Give the bridge a viewer port and open `http://localhost:3007`. When her mind
starts the bridge, set it where her mind runs:

```bash
VIEWER_PORT=3007 JENBINA_WORLD=minecraft python run_heartbeat.py
```

When you start the bridge yourself:

```bash
VIEWER_PORT=3007 node minecraft/bridge/bridge.js
```

She is in the world only while she looks and while she acts (a talk is an
act), so the view is live for a short stretch of every beat. To watch continuously, also set
`JENBINA_MINECRAFT_STAY_ONLINE=1` for her mind; she then stays logged in
between beats and the world keeps running around her.

The viewer listens on all network interfaces, so anyone on your network can
watch while it is on. It is off unless you set `VIEWER_PORT`.

## Settings

| Variable | Read by | Default | Meaning |
|---|---|---|---|
| `JENBINA_WORLD` | her mind | `palo_alto` | `minecraft` turns this on |
| `JENBINA_MINECRAFT_BRIDGE_URL` | her mind | `http://127.0.0.1:3010` | where the bridge listens |
| `JENBINA_MINECRAFT_STAY_ONLINE` | her mind | `0` | `1` keeps her logged in between beats |
| `JENBINA_MINECRAFT_AUTOSTART` | her mind | `1` | `0` stops her mind from starting the server, the bridge and the inhabitants |
| `JENBINA_MINECRAFT_INHABITANTS` | her mind | `1` | `0` leaves Mira and Tobin out even when they are set up |
| `JENBINA_MINECRAFT_TALKS_PER_DAY` | her mind | `12` | how many talks she may begin in a day; `0` means she never talks |
| `MINDCRAFT_NODE` | her mind | the private Node 20, else `node` | the Node binary that runs Mindcraft |
| `MC_HOST`, `MC_PORT` | bridge | `127.0.0.1`, `25565` | the server to join |
| `MC_USERNAME` | bridge | `Jenbina` | her name in the world |
| `MC_VERSION` | bridge | `1.21.4` | must match the server |
| `BRIDGE_PORT` | bridge | `3010` | bridge port, bound to `127.0.0.1` |
| `VIEWER_PORT` | bridge | unset | serve the browser viewer on this port |

## The world's rules

`setup_server.sh` writes a world that is reachable from this machine only, on
`easy` difficulty with monsters off:

- **Easy** gives her a body that gets hungry. Her hunger need follows her food
  bar, so she has to find food and eat it.
- **Monsters are off** (`spawn-monsters=false`). With them on, she is attacked
  at night and loses everything she carries when she dies. Switch them on in
  `minecraft/server/server.properties` if you want that danger; she can dig a
  burrow to shelter, but it does not always save her. Switching them off stops
  new ones appearing; any already in the world stay until they burn at sunrise.
- **The world waits for her.** It pauses ten seconds after she leaves. With
  Mira and Tobin in it the world is never empty, so it keeps running between
  her beats: days pass, and things change while she is away.
- **Offline mode** lets her join without a Microsoft account. Keep `server-ip`
  set to `127.0.0.1`: an offline-mode server open to a network lets anyone
  join under any name.

## What she can do

Look around, explore in four directions, chop wood, craft (planks, sticks, a
crafting table, wooden and stone tools, a furnace), mine stone, hunt, eat,
drink, dig a burrow, walk home, rest, and go to sleep. An action is offered
only when the world makes it possible. Home is where she first arrived.

With others in the world she can also talk with one of them. She is shown
what players say, as quoted speech; the only thing she ever says in the game
is her own line in a talk, as a whisper to the one she is talking with.

## Checking it by hand

The bridge's helpers have unit tests:

```bash
cd minecraft/bridge && npm test
```

Its routines need a live server. With the server and the bridge running:

```bash
curl -s -X POST http://127.0.0.1:3010/session/start
curl -s -X POST http://127.0.0.1:3010/act -H 'content-type: application/json' -d '{"name":"gather_wood"}'
curl -s -X POST http://127.0.0.1:3010/session/end
```

With an inhabitant in the world, between the first and the last of those:

```bash
curl -s -X POST http://127.0.0.1:3010/say -H 'content-type: application/json' -d '{"to":"Mira","text":"Hello"}'
```

The answer holds `answered` and the lines that came back in `heard`.

Each answer carries a one-sentence `summary` of what really changed.

An action that runs out of time, or leaves a step still going that cannot be
cancelled (eating, for one), ends with her logged out, so nothing in the world
changes after the answer. Such an answer has `left_world` set.

## Versions

The server is pinned to 1.21.4, the newest version that Mineflayer and its
browser viewer both support. On 26.1 she could join, walk and chop, but
crafting misbehaved and the viewer did not work.
