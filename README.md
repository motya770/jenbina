# Jenbina

[![Run Unit Tests](https://github.com/motya770/jenbina/actions/workflows/run-tests.yml/badge.svg)](https://github.com/motya770/jenbina/actions/workflows/run-tests.yml)
[![E2E Tests](https://github.com/motya770/jenbina/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/motya770/jenbina/actions/workflows/e2e-tests.yml)
[![codecov](https://codecov.io/gh/motya770/jenbina/branch/main/graph/badge.svg)](https://codecov.io/gh/motya770/jenbina)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-4581C3?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Auth-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/e6sRPpyc)

**Open-source AGI simulation with personality, motivation, and memory.**

Jenbina is a self-sustaining virtual persona that simulates human-like cognition using LLMs, a hybrid memory system, and Maslow's Hierarchy of Needs. Unlike standard chatbots, Jenbina has her own personality, internal drives, emotions, and long-term memory of people and events.

There is one Jenbina. She lives on her own clock whether or not anyone is watching: she takes a moment of life every few minutes, sleeps at night, and is the same being for everyone who talks to her. She can live in a described town or in a real Minecraft world.

Community Discord: https://discord.gg/e6sRPpyc

## How It Works

Jenbina addresses three fundamental limitations of LLMs:

1. **No persona** — LLMs are text generators without personality. Jenbina has character traits, emotions, and a self-narrative that evolve over time.
2. **No motivation** — LLMs lack internal drives. Jenbina's behavior is driven by Maslow's Hierarchy of Needs, from physiological survival to self-actualization.
3. **No memory** — LLMs forget between sessions. Jenbina remembers people, places, events, and conversations across a hybrid database system.

The result is something between a Tamagotchi and HAL — a virtual being with its own needs, goals, and the reasoning power of an LLM.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                          │
│                                                                      │
│   Streamlit home screen: chat timeline + live status rail            │
│   Environment, Console, Debug Info and Admin pages                   │
│   Firebase Authentication + Google OAuth                             │
└──────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────┐
│                              HEARTBEAT                               │
│                                                                      │
│   One shared Jenbina, hosted by one process at a time                │
│   A beat every 15 minutes, sleep and wake, private chat turns        │
└──────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────┐
│                           COGNITION LAYER                            │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ Meta-Cognition   │  │ Inner Monologue  │  │ Curiosity        │    │
│  │ Self-reflection  │  │ Stream of        │  │ Exploration and  │    │
│  │ Bias detection   │  │ consciousness    │  │ learning         │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ Action Decision  │  │ State Analysis   │  │ Asimov Check     │    │
│  │ Need-based       │  │ Growth stage     │  │ Safety           │    │
│  │ prioritization   │  │ assessment       │  │ guardrails       │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────┐
│                             CORE SYSTEMS                             │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ Person           │  │ Emotions         │  │ Goals, Planning  │    │
│  │ Needs, state,    │  │ Mood, effect on  │  │ and Learning     │    │
│  │ conversations    │  │ behavior         │  │                  │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ World            │  │ Social Cognition │  │ Identity         │    │
│  │ Palo Alto        │  │ Relationships    │  │ Self-narrative   │    │
│  │ or Minecraft     │  │                  │  │                  │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────┐
│                         HYBRID MEMORY SYSTEM                         │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ ChromaDB         │  │ Neo4j            │  │ SQLite           │    │
│  │                  │  │                  │  │                  │    │
│  │ Semantic memory  │  │ Relationship     │  │ Her saved state, │    │
│  │ via vector       │  │ graph between    │  │ life events,     │    │
│  │ embeddings and   │  │ people, places,  │  │ needs history,   │    │
│  │ similarity       │  │ events           │  │ accounts,        │    │
│  │ search           │  │                  │  │ conversations    │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────────────────────────────────────────┐
│                         OUTSIDE HER PROCESS                          │
│                                                                      │
│   OpenAI (gpt-5.2 / gpt-5-nano): every LLM call                      │
│   Minecraft, optional: Node bridge (Mineflayer) + private server     │
└──────────────────────────────────────────────────────────────────────┘
```

## Key Systems

### A Continuous Life (the heartbeat)
Jenbina is one being, not a simulation someone steps through:

- **One Jenbina** — every account talks to the same being and sees the same life. One process hosts her at a time: the app, or the standalone `run_heartbeat.py`.
- **Beats** — while her host is running she takes a moment of life (a "beat") every 15 minutes: she looks at her world, thinks, decides, acts, and her needs and mood move with what happened.
- **Sleep and wake** — she falls asleep and wakes on her own rhythm. Asleep, she takes no decisions and makes no LLM calls; a message can wake her.
- **Honest lost time** — when her host was not running, she notices the gap on return instead of pretending it did not happen, and is not punished for it.
- **Private conversations** — what one person says to her stays out of her conversations with everyone else, and chat stays responsive while a beat is under way.
- **A bounded bill** — beats are capped per day (80 by default) and back off when the LLM provider is failing.

### The Home Screen
One screen answers two questions: what is she doing right now, and what happened between you and in her day.

- **Timeline** — your conversation interleaved with her persisted life events: thoughts, actions, mood changes, goals, plans, moves, sleep, waking, and gaps.
- **Status rail** — live cards for what she is doing now (with her portrait and vitals), her heartbeat, and her mind (goals, plans, lessons, and what she knows about you).
- A Blade Runner 2049-inspired skin; debug material lives on separate pages.

### Maslow's Hierarchy of Needs
The core motivation engine. Jenbina progresses through five levels of needs, each with satisfaction tracking, decay rates, and growth stage progression:

| Level | Needs | Examples |
|-------|-------|----------|
| 1. Physiological | Survival basics | Hunger, thirst, sleep, health, shelter |
| 2. Safety | Security | Stability, protection, order |
| 3. Social | Belonging | Friendship, love, connection |
| 4. Esteem | Recognition | Self-esteem, confidence, achievement |
| 5. Self-Actualization | Growth | Creativity, purpose, meaning |

Needs decay over time and drive action selection — Jenbina prioritizes what she needs most.

### Hybrid Memory System
Three databases working together to mirror how human memory works:

- **ChromaDB** — Vector database for semantic/contextual memory. Stores conversations as embeddings and retrieves relevant context via similarity search.
- **Neo4j** — Graph database tracking relationships between people, locations, and events. Knows who Jenbina has met, where she's been, and how interactions connect.
- **SQLite** — Her saved state and the log of her life, needs history, user accounts, and conversation persistence.

### Cognition Layer
- **Meta-Cognition** — Self-reflection, cognitive bias detection, strategy optimization
- **Inner Monologue** — Stream-of-consciousness thinking before decisions
- **Action Decision Chain** — Selects actions based on need priority and world state
- **Asimov Safety Check** — Validates actions against ethical guardrails
- **Curiosity System** — Drives exploration and learning behavior
- **Goals, Planning and Working Memory** — Short-, mid- and long-term goals, plans toward them, and a short-term context for the current moment

### Her World
Jenbina lives in one of two worlds, chosen with `JENBINA_WORLD`.

**Palo Alto (default)** — a world described to her, based on Palo Alto, CA:
- Real location data (parks, cafes, libraries, venues)
- Weather simulation and day/night cycles
- Dynamic event generation
- Mood factors influenced by environment

**Minecraft (`JENBINA_WORLD=minecraft`)** — a real, persistent world on a private server:
- Each beat she looks at the actual world, picks one of the actions it makes possible, does it there, and is credited only for what really happened.
- She can look around, explore, chop wood, craft tools, mine stone, hunt, eat, drink, dig a shelter, walk home, rest, and sleep.
- Her inventory, her body and everything she changed are still there on the next beat. Her hunger follows her food bar, so she has to find food and eat it.
- Her world starts with her: her mind starts the Minecraft server and the bridge when it starts, and stops them when it stops.
- She need not be alone there. Mira and Tobin, two [Mindcraft](https://github.com/mindcraft-bots/mindcraft) agents, can live in the same world. She sees who is near, is shown what they said, and can talk with one of them inside a beat; she remembers who she has met. Her lines there are written by a prompt that reads nothing told to her in private.
- You can watch her in a browser, and no Minecraft account is needed.

```
Her mind (Python)  ⇄  Bridge (Node, Mineflayer)  ⇄  Minecraft server 1.21.4  ⇄  Mira, Tobin (Mindcraft, optional)
  observe, decide       her body: observe, act, say    the world, on this machine only    the others who live there
```

Setup, settings and the world's rules are in **[minecraft/README.md](minecraft/README.md)**.

### Emotion & Social Systems
- Emotional state tracking that influences behavior and responses
- Social cognition with relationship strength tracking
- Identity and self-narrative that evolve with experiences
- Insight generation for personal growth recommendations
- Proactive messages: she can reach out first to someone she has talked with recently

## Tech Stack

| Component | Technology | |
|-----------|------------|---|
| Language | Python 3.10+ | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) |
| Web UI | Streamlit | ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?logo=streamlit&logoColor=white) |
| LLM Orchestration | LangChain | ![LangChain](https://img.shields.io/badge/-LangChain-1C3C3C?logo=langchain&logoColor=white) |
| LLM | OpenAI (gpt-5.2, gpt-5-nano) | ![OpenAI](https://img.shields.io/badge/-OpenAI-412991?logo=openai&logoColor=white) |
| Vector Memory | ChromaDB | ![ChromaDB](https://img.shields.io/badge/-ChromaDB-FF6F00) |
| Graph Memory | Neo4j | ![Neo4j](https://img.shields.io/badge/-Neo4j-4581C3?logo=neo4j&logoColor=white) |
| Relational DB | SQLite | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white) |
| Auth | Firebase + Google OAuth | ![Firebase](https://img.shields.io/badge/-Firebase-FFCA28?logo=firebase&logoColor=black) |
| Web Search | SerpAPI | ![SerpAPI](https://img.shields.io/badge/-SerpAPI-23B5E5) |
| Minecraft world (optional) | Minecraft Java server 1.21.4, Node 18+, Mineflayer | ![Node.js](https://img.shields.io/badge/-Node.js-5FA04E?logo=nodedotjs&logoColor=white) |
| Testing | pytest, pytest-playwright, `node --test` | ![pytest](https://img.shields.io/badge/-pytest-0A9EDC?logo=pytest&logoColor=white) ![Playwright](https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white) |
| CI/CD | GitHub Actions | ![GitHub Actions](https://img.shields.io/badge/-GitHub_Actions-2088FF?logo=githubactions&logoColor=white) |

## Project Structure

```
jenbina/
├── core/                     # Main application
│   ├── app.py                # Streamlit entry point: the home screen
│   ├── simulation_runner.py  # One beat of her life, with no UI
│   ├── connect.py            # LLM provider connections
│   ├── heartbeat/            # One shared being: host, rhythm, sleep, storage
│   ├── timeline/             # The log of her life events
│   ├── person/               # Persona representation & state
│   ├── needs/                # Maslow's hierarchy implementation
│   ├── memory/               # Hybrid memory (Chroma + Neo4j + SQLite)
│   ├── working_memory/       # Short-term context
│   ├── cognition/            # Meta-cognition, decisions, safety checks
│   ├── environment/          # The Palo Alto world: locations, weather, events
│   │   └── minecraft/        # The Minecraft world: bridge client, scene, launcher
│   ├── emotions/             # Emotional state tracking
│   ├── social/               # Social cognition & relationships
│   ├── identity/             # Self-narrative & personal identity
│   ├── goals/                # Goal setting & prioritization
│   ├── planning/             # Plans toward goals
│   ├── learning/             # Experience tracking & lesson extraction
│   ├── insights/             # Growth insights & recommendations
│   ├── research/             # Research on the people she talks to
│   ├── interaction/          # Chat handler & guardrails
│   ├── auth/                 # Firebase auth & user database
│   ├── ui/                   # Timeline, status rail, theme, sprites
│   └── pages/                # Environment, Console, Debug Info, Admin
├── minecraft/                # Her Minecraft world
│   ├── bridge/               # Node bridge (Mineflayer): her body in the world
│   ├── setup_server.sh       # Download and configure the private server
│   ├── run_server.sh         # Start the server by hand
│   └── README.md             # Setup, settings, the world's rules
├── tests/                    # Unit, integration, and E2E tests
├── assets/                   # Portraits, sprites and static files
├── docs/plans/               # Design and implementation documents
├── jenbina_memory/           # Persistent data directory (gitignored)
├── run_app.py                # Launcher for the app
├── run_heartbeat.py          # Host her without a UI
├── requirements.txt
├── .env.example              # Template for settings and keys
├── INSTALL.md                # Detailed installation guide
└── system_design_schema.md   # System design documentation
```

## Quick Start

```bash
git clone https://github.com/motya770/jenbina
cd jenbina
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your_openai_api_key_here"
streamlit run core/app.py
```

Her heart beats for as long as the app is running. For detailed setup instructions (Neo4j, environment variables, API keys), see **[INSTALL.md](INSTALL.md)**.

### Without the UI

`run_heartbeat.py` hosts her with no browser. Only one process can host her at a time, so stop the app first.

```bash
python run_heartbeat.py          # keep her heart running
python run_heartbeat.py --once   # take one beat and exit
```

### In Minecraft

This needs Java 21 or newer and Node 18 or newer. Set the world up once; the server will not start until you accept the [Minecraft EULA](https://www.minecraft.net/en-us/eula), which is what `--accept-eula` does.

```bash
./minecraft/setup_server.sh --accept-eula
cd minecraft/bridge && npm install && cd ../..
```

Then start her with the Minecraft world switched on. The server and the bridge start with her and stop with her.

```bash
JENBINA_WORLD=minecraft python run_heartbeat.py
```

Or with the app:

```bash
JENBINA_WORLD=minecraft streamlit run core/app.py
```

To give her company there, set up Mira and Tobin once; after that they start and stop with her world:

```bash
./minecraft/setup_inhabitants.sh
```

See **[minecraft/README.md](minecraft/README.md)** for watching her in a browser, for the company she keeps, and for every setting.

### Settings

All settings are environment variables; `.env.example` lists them. `run_heartbeat.py` also reads a `.env` file in the project root; the app reads only the environment it is started with. The ones that shape her life:

| Variable | Default | Meaning |
|----------|---------|---------|
| `OPENAI_API_KEY` | — | Required for every LLM call |
| `JENBINA_BEAT_MINUTES` | `15` | Minutes between beats while she is awake |
| `JENBINA_MAX_BEATS_PER_DAY` | `80` | Daily cap on beats |
| `JENBINA_DISABLE_SLEEP` | `0` | `1` keeps her awake |
| `JENBINA_WORLD` | `palo_alto` | `minecraft` moves her into the Minecraft world |
| `JENBINA_MINECRAFT_STAY_ONLINE` | `0` | `1` keeps her logged in to Minecraft between beats |
| `JENBINA_MINECRAFT_AUTOSTART` | `1` | `0` if you start the Minecraft server and the bridge yourself |
| `JENBINA_MINECRAFT_INHABITANTS` | `1` | `0` leaves Mira and Tobin out of her Minecraft world |
| `JENBINA_MINECRAFT_TALKS_PER_DAY` | `12` | How many talks she may begin there in a day |

### Tests

```bash
python -m pytest tests/test_*.py -v --tb=short --cov=core   # Python unit tests (what CI runs)
cd minecraft/bridge && npm test                             # the bridge's unit tests
```

## The Two-Brain Architecture

Jenbina's cognition is split into two modules inspired by neuroscience:

**Reptile Brain** — The motivational core:
- Needs monitoring based on Maslow's hierarchy
- Action selection prioritized by urgency and growth stage
- Character development that evolves from experiences
- Goal-setting (immediate, short-term, long-term)

**Neocortex** — The reasoning layer:
- LLM-powered logical reasoning and language
- Interprets commands from the Reptile Brain
- Considers personal preferences and past experiences
- Interacts with her world

## Background

This project implements an artificial intelligence system that simulates a human persona. According to the persona's desires, goals, and needs, the system performs actions aligned with these objectives. It retains memories of past events and simulates a person's character, influencing its actions and goals.

The concept draws from electronic Tamagotchi toys of the 1990s — but instead of a user caring for the virtual being, Jenbina is self-sustaining, integrating the logical apparatus of an LLM to reason about her own needs and make decisions autonomously.

## Future Directions

- Autobiographical memory of her own life, and memory consolidation during sleep
- Real stakes: consequences when her needs go unmet
- More beings like her in her world, and things to do together with the ones who live there
- Integrating multiple LLMs with different specializations into a unified system
- Dynamic learning system that adds new actions and needs over time
- Shifting persona focus to other roles (e.g., rescue robot, companion)
- Embodiment in a mobile robot capable of physical interaction

## Creator

Created by **Matthew Kudelin** (Matvei Kudelin)

Open source, non-profit AGI simulation (patented).
