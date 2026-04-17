# CLAUDE.md - Jenbina AGI Simulation

## Project Overview

Jenbina is an open-source AGI (Artificial General Intelligence) simulation — a self-sustaining virtual persona modeled as a "Tamagotchi" powered by LLMs. The system combines Maslow's Hierarchy of Needs, a hybrid memory architecture (ChromaDB + Neo4j + SQLite), emotional intelligence, and multi-layer cognition to simulate a being with personality, motivation, and memory.

- **Language:** Python 3.10+
- **UI Framework:** Streamlit
- **LLM Orchestration:** LangChain
- **LLM Providers:** OpenAI (GPT-5-nano, GPT-5.2), Ollama (Llama 3.2 3B)
- **Databases:** ChromaDB (vector), Neo4j (graph), SQLite (time-series)

## Repository Structure

```
jenbina/
├── core/                        # Main application package
│   ├── app.py                   # Streamlit entry point
│   ├── engine.py                # Simulation engine (experimental)
│   ├── person.py                # Person class definition
│   ├── connect.py               # LLM provider connections
│   ├── fix_llm_json.py          # JSON response fixing utility
│   ├── log_capture.py           # Logging utilities
│   ├── auth/                    # Authentication (Firebase, SQLite user DB)
│   ├── cognition/               # Decision-making, meta-cognition, inner monologue
│   ├── emotions/                # Emotional state management and analysis
│   ├── environment/             # World simulation, locations, dynamic events
│   ├── goals/                   # Short/mid/long-term goal tracking
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
│   ├── working_memory/          # Short-term context management
│   ├── ui/                      # Streamlit UI components
│   └── pages/                   # Streamlit multi-page navigation
│       ├── 2_Chat.py
│       ├── 3_Environment.py
│       ├── 4_Console.py
│       └── 5_Debug_Info.py
├── tests/                       # Test suite (24 test modules)
│   ├── test_*.py                # Unit tests for all subsystems
│   ├── e2e/                     # End-to-end Playwright tests
│   ├── run_tests.py             # Test runner (unittest discovery)
│   └── run_chain_tests.py       # LangChain integration tests
├── docs/plans/                  # Design and planning documents
├── .github/workflows/           # CI/CD pipelines
├── assets/                      # Static assets (favicon, images)
├── old/                         # Legacy/archived code
├── requirements.txt             # Python dependencies
├── run_app.py                   # Launcher script
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
LLM Integration (LangChain → OpenAI / Ollama)
```

### Key Subsystems

- **Needs (`core/needs/`):** 5-level Maslow hierarchy with 26+ individual needs, automatic decay, and growth progression.
- **Memory (`core/memory/`):** Hybrid system — ChromaDB for semantic search, Neo4j for relationship graphs, SQLite for chronological tracking.
- **Cognition (`core/cognition/`):** Meta-cognition (self-reflection, bias detection), inner monologue (4 thought modes), action decision chains, Asimov safety checks.
- **Emotions (`core/emotions/`):** Emotional state tracking and LLM-powered emotion analysis.
- **Environment (`core/environment/`):** World simulation with locations (Palo Alto-based), weather, and dynamic events.
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

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# For local LLM support (optional)
ollama pull llama3.2:3b-instruct-fp16
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
| `run-tests.yml` | PR to main/master/develop | Unit tests with coverage (Python 3.10, pytest) |
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
- **Streamlit State:** The UI relies on `st.session_state` for persisting simulation state across reruns. Be careful with session state keys in `core/ui/shared_init.py`.
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
