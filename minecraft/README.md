# Jenbina's Minecraft world

With `JENBINA_WORLD=minecraft`, Jenbina lives in a private Minecraft world
instead of the described Palo Alto one. Each beat she looks at the real world,
picks one of the actions it offers, does it there, and is credited for what
actually happened. Her inventory, her body and everything she changed are
still there on the next beat.

The design is in
[docs/plans/2026-11-17-minecraft-world-design.md](../docs/plans/2026-11-17-minecraft-world-design.md).

## What runs

| Piece | Where | Started by |
|---|---|---|
| Her mind | the app or `run_heartbeat.py` | you, as before |
| Minecraft server 1.21.4 | `minecraft/server/` (ignored by git) | her mind, when it starts |
| Bridge (Node, Mineflayer) | `minecraft/bridge/` | her mind, when it starts |

Her world starts with her. When her mind starts, it starts the server and the
bridge if they are not already running, and when it stops it stops the ones it
started. One that you started yourself is left running. Before each look at
the world she checks that both are up and starts again whichever went down.

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

Or put `JENBINA_WORLD=minecraft` in `.env` and start the app as usual.

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

If her mind is killed outright, the server and the bridge it started keep
running. The next start finds them, uses them, and leaves them running when it
stops; stop them yourself with `pkill -f server.jar` and `pkill -f bridge.js`.

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

She is in the world only while she looks and while she acts, so the view is
live for a short stretch of every beat. To watch continuously, also set
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
| `JENBINA_MINECRAFT_AUTOSTART` | her mind | `1` | `0` stops her mind from starting the server and the bridge |
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
- **The world waits for her.** It pauses ten seconds after she leaves.
- **Offline mode** lets her join without a Microsoft account. Keep `server-ip`
  set to `127.0.0.1`: an offline-mode server open to a network lets anyone
  join under any name.

## What she can do

Look around, explore in four directions, chop wood, craft (planks, sticks, a
crafting table, wooden and stone tools, a furnace), mine stone, hunt, eat,
drink, dig a burrow, walk home, rest, and go to sleep. An action is offered
only when the world makes it possible. Home is where she first arrived.

She reads no in-game chat and says nothing in the game.

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

Each answer carries a one-sentence `summary` of what really changed.

An action that runs out of time, or leaves a step still going that cannot be
cancelled (eating, for one), ends with her logged out, so nothing in the world
changes after the answer. Such an answer has `left_world` set.

## Versions

The server is pinned to 1.21.4, the newest version that Mineflayer and its
browser viewer both support. On 26.1 she could join, walk and chop, but
crafting misbehaved and the viewer did not work.
