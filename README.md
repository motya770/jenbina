# Jenbina

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

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Web UI | Streamlit |
| LLM Orchestration | LangChain |
| LLM (Cloud) | OpenAI (gpt-5.2, gpt-5-nano) |
| LLM (Local) | Ollama + Llama 3.2 3B |
| Vector Memory | ChromaDB |
| Graph Memory | Neo4j |
| Relational DB | SQLite |
| Auth | Firebase + Google OAuth |
| Web Search | SerpAPI |
| Testing | pytest, pytest-playwright |
| CI/CD | GitHub Actions |

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
