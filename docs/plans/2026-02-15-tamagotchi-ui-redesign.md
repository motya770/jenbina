# Tamagotchi UI Redesign

**Date:** 2026-02-15
**Status:** Approved
**Approach:** Streamlit overhaul with custom CSS (no framework change)

## Problem

The simulation UI is overwhelming: too much information at once, visually plain, and hard to follow what Jenbina is doing. The current layout renders ~30+ visible sections across multiple column grids with raw JSON dumps.

## Design

### Layout: Single-Column "Tamagotchi Screen"

Replace the multi-column grid with a focused, centered layout:

```
┌─────────────────────────────────────┐
│         🌤️ Palo Alto · Morning      │  Environment ribbon (one line)
├─────────────────────────────────────┤
│          ┌──────────┐               │
│          │  Jenbina  │              │  Centered character (350px)
│          │  (image)  │              │
│          └──────────┘               │
│     "I should probably eat..."      │  Inner monologue as thought bubble
│                                     │
│  🍔 ████████░░  78%   😴 ███░░░ 35% │  Needs as colored game bars
│  🛡️ ██████████  95%   💕 █████░ 65% │
│                                     │
│  😊 Joy · 😮 Surprise              │  Emotions as chips/tags
├─────────────────────────────────────┤
│  ▶ Jenbina decided to eat breakfast │  Action as narrative sentence
│    "Hunger is critical..."          │  Reasoning as subtitle
│  📈 Satisfaction: 62% → 68% (+6%)  │  Outcome delta
├─────────────────────────────────────┤
│  📚 Goals · 📋 Plans · 🧠 Memory   │  Collapsible details
└─────────────────────────────────────┘
```

### Visual Style: Playful Tamagotchi Aesthetic

- **Background:** Soft pastel cream (#FFF8F0)
- **Cards:** Rounded corners, subtle shadow, white background
- **Needs bars:** Color gradient red → yellow → green based on satisfaction. Critical needs (<30%) get a pulse animation.
- **Emotions:** Colored pill/chip tags, only shown if intensity > 15
- **Action:** Styled "story card" with bold action, muted reasoning, delta badge
- **Accent color:** Warm pink/coral (#FF8FAB)
- **Character:** Centered, larger (350px), soft rounded frame

### Information Hierarchy (3 Tiers)

**Tier 1 — Always visible:**
- Environment ribbon (location, time, weather)
- Jenbina image + action caption
- Inner monologue thought bubble
- 6 needs as progress bars
- Top 2-3 emotions as chips
- Action narrative + reasoning + satisfaction delta

**Tier 2 — Auto-expand when interesting, collapsed otherwise:**
- Learning (expand if new lesson or satisfaction delta > 5%)
- Goals (expand if goal advanced or created)
- Plans (expand if step completed or replanned)
- Curiosity (expand if should_explore is true)

**Tier 3 — Always collapsed (debug/power users):**
- Raw JSON responses
- Chain-of-thought reasoning trace
- Safety/Asimov check
- State analysis
- Working memory, meta-cognition
- Full emotion list, person/world JSON

### Implementation Scope

**Modified file:** `core/ui/simulation.py`

Changes:
1. Add `inject_tamagotchi_css()` — all custom CSS in one function
2. Add `render_needs_bars()` — colored HTML progress bars replacing `display_person_state()`
3. Add `render_emotion_chips()` — pill tags for emotions
4. Add `render_action_narrative()` — story-style action display
5. Add `render_environment_ribbon()` — single-line world state replacing `display_world_state()`
6. Refactor `run_single_iteration()` — new Tamagotchi layout, same computation flow
7. Move all raw JSON into `st.expander("Debug")` blocks
8. Add auto-expand logic for Tier 2 sections
9. Update `display_simulation_summary()` to match narrative style

**Untouched:**
- All backend logic (cognition, needs, emotions, learning, goals, planning)
- Computation flow and LLM call order in `run_single_iteration()`
- Other pages (Chat, Environment, Console)
- Image mapping logic
- No new dependencies
