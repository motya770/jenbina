# Jenbina

[![Run Unit Tests](https://github.com/motya770/jenbina/actions/workflows/run-tests.yml/badge.svg)](https://github.com/motya770/jenbina/actions/workflows/run-tests.yml)
[![E2E Tests](https://github.com/motya770/jenbina/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/motya770/jenbina/actions/workflows/e2e-tests.yml)
[![codecov](https://codecov.io/gh/motya770/jenbina/branch/main/graph/badge.svg)](https://codecov.io/gh/motya770/jenbina)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-4581C3?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Auth-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/e6sRPpyc)

**Open-source AGI simulation with personality, motivation, and memory.**

Jenbina is a self-sustaining virtual persona that simulates human-like cognition using LLMs, a hybrid memory system, and Maslow's Hierarchy of Needs. Unlike standard chatbots, Jenbina has her own personality, internal drives, emotions, and long-term memory of people and events.

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
│                         PRESENTATION LAYER                          │
│                                                                      │
│   Streamlit Web UI — Chat, Simulation View, Debug Pages              │
│   Firebase Authentication + Google OAuth                             │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                        COGNITION LAYER                               │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Meta-Cognition│  │Inner Monologue│  │  Curiosity   │              │
│  │ Self-reflect  │  │ Stream of    │  │  System      │              │
│  │ Bias detect   │  │ consciousness│  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │Action Decision│  │State Analysis│  │ Asimov Check │              │
│  │ Need-based    │  │ Growth stage │  │ Safety guard │              │
│  │ prioritization│  │ assessment   │  │ rails        │              │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                          CORE SYSTEMS                                │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │    Person     │  │  Emotions    │  │   Goals &    │              │
│  │ Needs, state, │  │ Mood, affect │  │   Learning   │              │
│  │ conversations │  │ on behavior  │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Environment  │  │   Social     │  │  Identity &  │              │
│  │ Locations,    │  │  Cognition   │  │  Self-       │              │
│  │ weather, events│  │ Relationships│  │  Narrative   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                     HYBRID MEMORY SYSTEM                             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   ChromaDB   │  │    Neo4j     │  │    SQLite    │               │
│  │              │  │              │  │              │               │
│  │ Semantic     │  │ Relationship │  │ Time-series  │               │
│  │ memory via   │  │ graph between│  │ events,      │               │
│  │ vector       │  │ people,      │  │ needs history,│               │
│  │ embeddings   │  │ places,      │  │ user accounts,│               │
│  │ & similarity │  │ events       │  │ conversations │               │
│  │ search       │  │              │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                       LLM PROVIDERS                                  │
│                                                                      │
│  OpenAI (gpt-5.2 / gpt-5-nano)  ·  Ollama (llama3.2:3b local)      │
└──────────────────────────────────────────────────────────────────────┘
```

## Key Systems

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
- **SQLite** — Time-series storage for chronological events, needs history, user accounts, and conversation persistence.

### Cognition Layer
- **Meta-Cognition** — Self-reflection, cognitive bias detection, strategy optimization
- **Inner Monologue** — Stream-of-consciousness thinking before decisions
- **Action Decision Chain** — Selects actions based on need priority and world state
- **Asimov Safety Check** — Validates actions against ethical guardrails
- **Curiosity System** — Drives exploration and learning behavior

### Environment Simulation
Jenbina exists in a simulated world (based on Palo Alto, CA) with:
- Real location data (parks, cafes, libraries, venues)
- Weather simulation and day/night cycles
- Dynamic event generation
- Mood factors influenced by environment

### Emotion & Social Systems
- Emotional state tracking that influences behavior and responses
- Social cognition with relationship strength tracking
- Identity and self-narrative that evolve with experiences
- Insight generation for personal growth recommendations

## Tech Stack

| Component | Technology | |
|-----------|------------|---|
| Language | Python 3.10+ | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) |
| Web UI | Streamlit | ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?logo=streamlit&logoColor=white) |
| LLM Orchestration | LangChain | ![LangChain](https://img.shields.io/badge/-LangChain-1C3C3C?logo=langchain&logoColor=white) |
| LLM (Cloud) | OpenAI (gpt-5.2, gpt-5-nano) | ![OpenAI](https://img.shields.io/badge/-OpenAI-412991?logo=openai&logoColor=white) |
| LLM (Local) | Ollama + Llama 3.2 3B | ![Ollama](https://img.shields.io/badge/-Ollama-000000?logo=ollama&logoColor=white) |
| Vector Memory | ChromaDB | ![ChromaDB](https://img.shields.io/badge/-ChromaDB-FF6F00) |
| Graph Memory | Neo4j | ![Neo4j](https://img.shields.io/badge/-Neo4j-4581C3?logo=neo4j&logoColor=white) |
| Relational DB | SQLite | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white) |
| Auth | Firebase + Google OAuth | ![Firebase](https://img.shields.io/badge/-Firebase-FFCA28?logo=firebase&logoColor=black) |
| Web Search | SerpAPI | ![SerpAPI](https://img.shields.io/badge/-SerpAPI-23B5E5) |
| Testing | pytest, pytest-playwright | ![pytest](https://img.shields.io/badge/-pytest-0A9EDC?logo=pytest&logoColor=white) ![Playwright](https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white) |
| CI/CD | GitHub Actions | ![GitHub Actions](https://img.shields.io/badge/-GitHub_Actions-2088FF?logo=githubactions&logoColor=white) |

## Project Structure

```
jenbina/
├── core/                     # Main application
│   ├── app.py                # Streamlit entry point
│   ├── connect.py            # LLM provider connections
│   ├── person/               # Persona representation & state
│   ├── needs/                # Maslow's hierarchy implementation
│   ├── memory/               # Hybrid memory (Chroma + Neo4j + SQLite)
│   ├── cognition/            # Meta-cognition, decisions, safety checks
│   ├── environment/          # World simulation, locations, weather
│   ├── emotions/             # Emotional state tracking
│   ├── social/               # Social cognition & relationships
│   ├── identity/             # Self-narrative & personal identity
│   ├── goals/                # Goal setting & prioritization
│   ├── learning/             # Experience tracking & lesson extraction
│   ├── insights/             # Growth insights & recommendations
│   ├── interaction/          # Chat handler & guardrails
│   ├── auth/                 # Firebase auth & user database
│   ├── ui/                   # Streamlit UI components
│   └── pages/                # Multi-page app (Chat, Environment, Debug)
├── tests/                    # Unit, integration, and E2E tests
├── assets/                   # Images and static files
├── docs/                     # Documentation
├── jenbina_memory/           # Persistent data directory (gitignored)
├── requirements.txt
├── INSTALL.md                # Detailed installation guide
└── system_design_schema.md   # System design documentation
```

## Quick Start

```bash
git clone https://github.com/motya770/jenbina
cd jenbina
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run core/app.py
```

For detailed setup instructions (Ollama, Neo4j, environment variables, API keys), see **[INSTALL.md](INSTALL.md)**.

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
- Interacts with the simulated environment

## Background

This project implements an artificial intelligence system that simulates a human persona. According to the persona's desires, goals, and needs, the system performs actions aligned with these objectives. It retains memories of past events and simulates a person's character, influencing its actions and goals.

The concept draws from electronic Tamagotchi toys of the 1990s — but instead of a user caring for the virtual being, Jenbina is self-sustaining, integrating the logical apparatus of an LLM to reason about her own needs and make decisions autonomously.

## Future Directions

- Integrating multiple LLMs with different specializations into a unified system
- Dynamic learning system that adds new actions and needs over time
- Shifting persona focus to other roles (e.g., rescue robot, companion)
- Embodiment in a mobile robot capable of physical interaction

## Creator

Created by **Matthew Kudelin** (Matvei Kudelin)

Open source, non-profit AGI simulation (patented).
