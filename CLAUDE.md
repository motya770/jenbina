# CLAUDE.md - Jenbina AGI Simulation

## Project Overview

Jenbina is an open-source AGI (Artificial General Intelligence) simulation — a self-sustaining virtual persona modeled as a "Tamagotchi" powered by LLMs. The system combines Maslow's Hierarchy of Needs, a hybrid memory architecture (ChromaDB + Neo4j + SQLite), emotional intelligence, and multi-layer cognition to simulate a being with personality, motivation, and memory.

- **Language:** Python 3.10+
- **UI Framework:** Streamlit
- **LLM Orchestration:** LangChain
- **LLM Provider:** OpenAI (GPT-5-nano, GPT-5.2)
- **Databases:** ChromaDB (vector), Neo4j (graph), SQLite (time-series)

## Repository Structure

```
jenbina/
├── core/                        # Main application package
│   ├── app.py                   # Streamlit entry point: the home screen (timeline + status rail)
│   ├── engine.py                # Simulation engine (experimental)
│   ├── person.py                # Person class definition
│   ├── connect.py               # LLM provider connections
│   ├── fix_llm_json.py          # JSON response fixing utility
│   ├── log_capture.py           # Logging utilities
│   ├── auth/                    # Authentication (Firebase, SQLite user DB)
│   ├── cognition/               # Decision-making, meta-cognition, inner monologue
│   ├── emotions/                # Emotional state management and analysis
│   ├── environment/             # World simulation, locations, dynamic events
│   │   └── minecraft/           # A real world: bridge client, scene and action builder, world provider, launcher for its processes
│   ├── goals/                   # Short/mid/long-term goal tracking
│   ├── heartbeat/               # One shared being, owned by one process; no Streamlit imports
│   │   ├── adoption.py          # One-time adoption of existing per-user state and history
│   │   ├── being.py             # Build or restore Person and initialise her subsystems
│   │   ├── host.py              # JenbinaHost: live Person, mind lock, lease, beats and chat turns
│   │   ├── outreach.py          # Select one eligible person for a proactive message
│   │   ├── rhythm.py            # Pure beat, sleep, wake, back-off and lost-time rules
│   │   └── store.py             # Shared state, life events, lease and per-account person keys
│   ├── identity/                # Self-narrative and self-concept
│   ├── insights/                # LLM-based insight generation
│   ├── interaction/             # Chat handling and safety guardrails
│   ├── learning/                # Experience recording and lesson extraction
│   ├── memory/                  # Hybrid memory system (ChromaDB + Neo4j + SQLite)
│   ├── needs/                   # Maslow's hierarchy implementation
│   ├── person/                  # Person dataclass and conversation tracking
│   ├── planning/                # Action planning system
│   ├── research/                # User research utilities
│   ├── social/                  # Social cognition modeling
│   ├── timeline/                # Event log of Jenbina's life: kinds, titles, EventLog, recording helpers
│   ├── working_memory/          # Short-term context management
│   ├── ui/                      # Streamlit UI components
│   │   ├── admin.py             # Shared local-request and admin access checks
│   │   ├── live.py              # Guarded fragment rendering and refresh interval
│   │   ├── timeline.py          # The chat timeline: messages and life events merged, markers, rows
│   │   ├── rail.py              # The status rail: Now card, heartbeat card, mind card
│   │   ├── pixel_theme.py       # Theme CSS (Blade Runner 2049 hologram skin) + event-row/marker/pill HTML helpers
│   │   └── sprites/             # Pixel art strings, palette, Pillow builder (art.py, build.py)
│   └── pages/                   # Streamlit multi-page navigation
│       ├── 3_Environment.py
│       ├── 4_Console.py
│       └── 5_Debug_Info.py
├── tests/                       # Test suite (24 test modules)
│   ├── test_*.py                # Unit tests for all subsystems
│   ├── e2e/                     # End-to-end Playwright tests
│   ├── run_tests.py             # Test runner (unittest discovery)
│   └── run_chain_tests.py       # LangChain integration tests
├── minecraft/                   # Her Minecraft world (see minecraft/README.md)
│   ├── bridge/                  # Node bridge (Mineflayer): her body, a localhost HTTP API with observe and act
│   ├── setup_server.sh          # Download and configure the private 1.21.4 server (EULA only with --accept-eula)
│   ├── run_server.sh            # Start the server
│   └── server/                  # The server and the world itself (ignored by git)
├── docs/plans/                  # Design and planning documents
├── .github/workflows/           # CI/CD pipelines
├── assets/                      # Static assets (favicon, jenbina_nav.png face crop for the sidebar and tab icon)
│   ├── portraits/               # Painterly Jenbina portraits, one per state (jenbina_<state>.png)
│   └── sprites/                 # Committed pixel sprite sheets and 8x8 icons (python -m core.ui.sprites.build)
├── old/                         # Legacy/archived code
├── requirements.txt             # Runtime Python dependencies (what Railway installs)
├── requirements-dev.txt         # requirements.txt plus pytest, coverage, Playwright
├── railway.toml                 # Railway service config: start command, health check (see DEPLOY.md)
├── .railway/railway.ts          # Railway Infrastructure as Code: service + volume (replaces railway.toml, see DEPLOY.md)
├── DEPLOY.md                    # How Jenbina is deployed to Railway: one-time setup, env vars, redeploy
├── run_app.py                   # Launcher script
├── run_heartbeat.py             # Standalone heartbeat host (alternative to the app process)
├── run_jenbina.py               # Alternative launcher
├── clear_chromadb.py            # Utility: clear vector database
├── clear_memory.py              # Utility: clear memory system
├── .env.example                 # Environment variable template
└── .streamlit/config.toml       # Streamlit theme configuration
```

## Architecture

The system follows a layered architecture:

```
UI Layer (Streamlit pages & components)
    ↓
Interaction Layer (chat_handler, guardrails)
    ↓
Cognition Layer (action decisions, meta-cognition, inner monologue)
    ↓
Core Systems (Person, Needs, Memory, Emotions, Goals, Learning)
    ↓
Database Layer (ChromaDB, Neo4j, SQLite)
    ↓
LLM Integration (LangChain → OpenAI)
```

### Key Subsystems

- **Needs (`core/needs/`):** 5-level Maslow hierarchy with 26+ individual needs, automatic decay, and growth progression.
- **Memory (`core/memory/`):** Hybrid system — ChromaDB for semantic search, Neo4j for relationship graphs, SQLite for chronological tracking.
- **Cognition (`core/cognition/`):** Meta-cognition (self-reflection, bias detection), inner monologue (4 thought modes), action decision chains, Asimov safety checks.
- **Emotions (`core/emotions/`):** Emotional state tracking and LLM-powered emotion analysis.
- **Environment (`core/environment/`):** World simulation with locations (Palo Alto-based), weather, and dynamic events. With `JENBINA_WORLD=minecraft`, `core/environment/minecraft/` replaces it with a private Minecraft world: the scene and the available actions are read from the world, and needs are credited from what actually happened there.
- **Goals (`core/goals/`):** Short/mid/long-term objective generation and tracking.
- **Learning (`core/learning/`):** Experience recording, lesson extraction, confidence tracking.

## Common Commands

### Running the Application

```bash
# Primary method — run from project root
cd core && streamlit run app.py

# Or use launcher scripts
python run_app.py
python run_jenbina.py
```

From the project root, the standalone runner can host Jenbina without a UI.
Only one process can host her at a time; stop the app host before using it.

```bash
# Keep her heart running
python run_heartbeat.py

# Take one beat and exit
python run_heartbeat.py --once

# Choose whose saved Jenbina to adopt on the first start
python run_heartbeat.py --adopt-user-id 3
```

### Minecraft world

Her Minecraft world needs two extra processes: the server and the Node
bridge. Her mind starts both when it starts and stops the ones it started when
it stops (`core/environment/minecraft/launcher.py`); ones already running are
used and left running. The setup is never done for you. Full notes are in
`minecraft/README.md`.

```bash
# Once: download and configure the server, then install the bridge's packages
./minecraft/setup_server.sh --accept-eula
cd minecraft/bridge && npm install

# Each time: her mind; the world starts with it (output in minecraft/logs/)
JENBINA_WORLD=minecraft python run_heartbeat.py --once

# Or start the world yourself and keep it up between runs
./minecraft/run_server.sh
node minecraft/bridge/bridge.js

# The bridge's unit tests (CI does not run them)
cd minecraft/bridge && npm test
```

### Running Tests

```bash
# Run all unit tests with pytest (preferred, matches CI)
python -m pytest tests/test_*.py -v --tb=short --cov=core

# Run all tests via the test runner script
python tests/run_tests.py

# Run a specific test file
python -m pytest tests/test_maslow_needs.py -v

# Run LangChain integration tests (requires LLM access)
python tests/run_chain_tests.py
```

### Utility Commands

```bash
# Clear ChromaDB vector database
python clear_chromadb.py

# Clear all memory
python clear_memory.py
```

### Deploying

The app runs on Railway; `DEPLOY.md` has the one-time setup, the env var table and the redeploy command (`railway up` from the repo root).

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # app + test tooling; requirements.txt alone is the production set
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API access |
| `OPENAI_CHAT_MODEL` | Model selection (e.g., `openai-advanced`) |
| `SERPAPI_API_KEY` | Web search integration |
| `FIREBASE_API_KEY` | Firebase authentication |
| `FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `JENBINA_BEAT_MINUTES` | Minutes between awake beats (default: `15`) |
| `JENBINA_MAX_BEATS_PER_DAY` | Daily cap on awake beat attempts, including manual steps (default: `80`) |
| `JENBINA_LLM_TIMEOUT_SECONDS` | Timeout for each LLM call in seconds (default: `60`, with one retry) |
| `JENBINA_DISABLE_SLEEP` | Set to `1` to keep her awake, including in E2E tests (default: `0`, sleep enabled) |
| `JENBINA_WORLD` | `minecraft` makes her live in a private Minecraft world (default: `palo_alto`, the described world) |
| `JENBINA_MINECRAFT_BRIDGE_URL` | Where the Node bridge listens (default: `http://127.0.0.1:3010`) |
| `JENBINA_MINECRAFT_STAY_ONLINE` | Set to `1` to keep her logged in to Minecraft between beats (default: `0`, she is in the world only while looking and acting) |
| `JENBINA_MINECRAFT_AUTOSTART` | Set to `0` to start the Minecraft server and the bridge yourself (default: `1`, her mind starts and stops them) |
| `JENBINA_ADOPT_USER_ID` | On the very first start only: the user id whose saved Jenbina becomes the one Jenbina (default: the real account with the most experiences; the E2E test login is never picked automatically) |

## Code Conventions

### Naming

- **Classes:** PascalCase — `MaslowNeedsSystem`, `InnerMonologue`, `HybridMemorySystem`
- **Functions/Methods:** snake_case — `get_needs_snapshot()`, `add_message()`
- **Constants:** UPPER_SNAKE_CASE — `DELIBERATION_NEED_THRESHOLD`
- **Enums:** UPPER_SNAKE_CASE values — `ThoughtMode.DELIBERATION`

### Patterns

- **Dataclasses** used extensively for data structures (with `@dataclass`)
- **LangChain chains** for all LLM-driven workflows (decision, analysis, emotion)
- **Factory functions** for creating specialized systems (e.g., `create_world_description_system()`)
- **Type hints** throughout (Python 3.10+ syntax)
- **Module `__init__.py`** files export public APIs; respect the public interface in `core/__init__.py`

### File Organization

- Each subdirectory under `core/` is a self-contained module with its own `__init__.py`
- LangChain chain definitions live alongside the system they serve (e.g., `maslow_decision_chain.py` in `needs/`)
- UI components are in `core/ui/`, page routing in `core/pages/`
- Tests mirror the module structure: `test_maslow_needs.py` tests `core/needs/maslow_needs.py`

## CI/CD

GitHub Actions workflows (`.github/workflows/`):

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| `run-tests.yml` | PR to main/master/develop | Unit tests with coverage (Python 3.10 and 3.11, pytest) |
| `test-suite.yml` | Manual / scheduled | Full test suite execution |
| `e2e-tests.yml` | Manual / scheduled | End-to-end tests with Playwright |
| `feedback-loop-test.yml` | Manual / scheduled | Feedback loop testing |

The primary CI gate is `run-tests.yml` which runs `python -m pytest tests/test_*.py -v --tb=short --cov=core` on every PR.

## Testing Guidelines

- All unit tests are in `tests/test_*.py` and use `unittest.TestCase`
- Tests should not require external services (LLM, databases) — mock them
- Chain/integration tests in `tests/run_chain_tests.py` do require LLM access
- E2E tests in `tests/e2e/` use Playwright and require a running Streamlit server
- Test naming convention: `test_<module_name>.py` matching `core/<module>/`

## Important Considerations

- **Safety:** The system includes Asimov-check chains (`core/cognition/asimov_check_chain.py`) and guardrails (`core/interaction/guardrails.py`). Maintain safety constraints when modifying cognition or interaction code.
- **LLM JSON Parsing:** LLM responses are parsed as JSON for structured decisions. The `fix_llm_json.py` utility handles malformed JSON from LLMs — use it when processing LLM output.
- **Memory Databases:** The hybrid memory system uses three databases simultaneously. Changes to memory schemas affect ChromaDB collections, Neo4j nodes/relationships, and SQLite tables.
- **Streamlit State:** The live `Person` belongs to the host in `core/heartbeat/host.py`. `st.session_state.person` is a reference to that shared object. Change her only inside `host.chat_turn(...)` or a beat so the mind lock protects her state; the host saves it.
- **Minecraft world:** A real world is a `world_provider` on the host (`core/environment/minecraft/provider.py`). The runner calls `observe` before any LLM call and `perform` after the decision; with no provider the Palo Alto code path is unchanged. Keep every Minecraft routine bounded and report failures honestly: she is credited only for what the bridge says happened. Never call the bridge with the mind lock held (use the `waiting` the runner passes, or ask for the logout as `_fall_asleep` does), and let only a host that still has her log her out.
- **No `.env` in VCS:** The `.env` file contains secrets and must never be committed. Use `.env.example` as the template.

## Superpowers Plugin

This project uses the **superpowers** Claude Code plugin for structured plan execution.

### Usage

Implementation plans in `docs/plans/` are designed to be executed with the `superpowers:executing-plans` sub-skill. Each plan document includes the directive:

```
> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
```

When Claude encounters this directive, it should use the superpowers plugin to execute the plan systematically — one task at a time, following each step within the task, running tests, and committing after each task.

### Plan Document Format

Plans in `docs/plans/` follow a consistent structure:

```
# Plan Title

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** <what the plan achieves>
**Architecture:** <high-level approach>
**Tech Stack:** <technologies involved>

---

### Task N: <task title>

**Files:**
- Modify: `path/to/file.py:line_range`
- Create: `path/to/new_file.py`

**Step 1: <step description>**
<code or instructions>

**Step 2: Run tests**
Run: `python -m pytest tests/test_xyz.py -v`
Expected: All PASS

**Step 3: Commit**
git add <files>
git commit -m "<conventional commit message>"
```

### Key Conventions

- **Task-by-task execution:** Complete and commit each task before moving to the next.
- **Test-driven:** Each task includes test verification steps. Run tests after each change.
- **Atomic commits:** Each task ends with a focused `git commit` using conventional commit messages (`feat:`, `fix:`, `docs:`, etc.).
- **File locations specified:** Tasks list exact files and line ranges to modify.
- **Backward compatibility:** New fields and features use defaults to avoid breaking existing tests.

### Existing Plans

| Plan | Description |
|------|-------------|
| `2026-02-15-tamagotchi-ui-implementation.md` | Tamagotchi UI redesign — CSS injection, rendering helpers, single-column layout |
| `2026-02-17-wow-effect-implementation.md` | Deep Emotional Mirror — user research, insight system, GPT-5.2 chat, dynamic greetings |
| `2026-02-18-llm-knowledge-enriched-dossier.md` | LLM knowledge-enriched dossiers — parallel web search + GPT knowledge query |
| `2026-10-27-pixel-art-ui-redesign.md` | Pixel art UI spec — handheld device shell, 48x48 animated sprite sheets, 8x8 icons, palette and states; revision 2 restores the portraits and switches to the candy arcade palette |
| `2026-10-27-pixel-art-ui-implementation.md` | Pixel art UI implementation — sprite pipeline, `core/ui/pixel_theme.py`, pixel markup in the simulation renderers |
| `2026-10-28-timeline-ui-redesign.md` | Timeline home screen spec — the chat timeline interleaved with Jenbina's persisted life events beside a live status rail; the Simulation and Chat pages merge |
| `2026-10-28-timeline-ui-implementation.md` | Timeline home screen implementation — `core/timeline/` event log, `core/ui/timeline.py`, `core/ui/rail.py`, runner refactor, home screen |
| `2026-11-14-blade-runner-theme-redesign.md` | Blade Runner 2049 skin proposal — replaces the candy arcade pixel skin with smoke, amber, ice and violet tokens, IBM Plex and Rajdhani type, kind tags instead of pixel icons; layout unchanged |
| `2026-11-15-heartbeat-design.md` | Heartbeat spec — one shared Jenbina, continuous beats, sleep and wake, honest lost time, private conversations and a live home screen |
| `2026-11-15-heartbeat-implementation.md` | Heartbeat implementation — shared storage, rhythm, host, state adoption, standalone runner, per-person chat privacy and live UI |
| `2026-11-17-minecraft-world-design.md` | Minecraft world spec — a private server, a Node bridge with observe and act, a scene and action list built from the world, needs credited from real outcomes |

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
