# Deep Emotional Mirror — Wow Effect Design

## Goal

Make Jenbina create a "holy shit" moment mid-conversation where users feel genuinely understood — not through a party trick, but through unexpectedly perceptive observations informed by who they actually are.

## Target Audience

General users / friends. The wow needs to be emotional and immediate.

## Architecture Overview

```
Google Login
    |
    +-- Capture email, name, photo (existing)
    |
    +-- Background: Web Search API -> raw results
    |       |
    |       +-- GPT-5.2 -> user_dossier (psychological profile)
    |               |
    |               +-- Stored in PersonModel (social cognition)
    |
    +-- First Greeting: GPT-5.2 + dossier -> personalized, curious greeting

Conversation Flow
    |
    +-- Chat Model: GPT-5.2 (upgraded from nano)
    |       |
    |       +-- Enhanced prompt with: dossier + goals + inner monologue
    |           + self-narrative + lessons + curiosity state
    |
    +-- InsightSystem (new)
    |       |
    |       +-- Triggers: 2-3 messages in, max 3 per session
    |       +-- Input: dossier + conversation + relationship + emotions + narrative
    |       +-- Output: one deep observation, woven into response naturally
    |
    +-- Return Greeting: GPT-5.2 generated (replaces static messages)
    |       |
    |       +-- References: her goals, last conversation, her emotional state
    |
    +-- Inner Life Surfacing (prompt engineering)
            |
            +-- Spontaneous tangents from her interests
            +-- Opinions and disagreement
            +-- Lives her state, doesn't narrate it

Internal Mechanics (unchanged, stay on GPT-5-nano)
    |
    +-- Needs decisions (JSON mode)
    +-- Action selection
    +-- Emotion analysis
```

## Component Details

### 1. User Research System

Triggered on first login (or when dossier is empty/stale).

- **Input**: User's name + email domain from Google OAuth
- **Research**: Web search API (SerpAPI or Serper.dev) searches for the user
- **Processing**: GPT-5.2 extracts a psychological profile from public info:
  - Likely personality traits and values
  - Communication style
  - What motivates this person
  - What they might be insecure about
- **Storage**: `user_dossier` dict in the existing `PersonModel` (social cognition system), persisted via SQLite
- **Fallback**: If no results found, dossier enriches over time through conversation

### 2. Model Upgrade

Switch user-facing interactions to GPT-5.2:

- Chat responses: GPT-5.2
- Insight generation: GPT-5.2
- Proactive messages: GPT-5.2
- JSON-mode operations (needs, actions, emotions): Stay on GPT-5-nano

New env var: `OPENAI_CHAT_MODEL` (default `gpt-5.2`)

### 3. Insight Generation System

New `InsightSystem` subsystem.

**Trigger conditions:**
- At least 2-3 messages exchanged in current conversation
- Max 3 insights per conversation session

**Generation:**
- Separate GPT-5.2 call when triggered
- Input: user dossier + last 10 messages + relationship model + Jenbina's emotions + self-narrative
- Prompt: "Generate ONE deep observation about this person. Not a compliment. Not advice. An observation that shows you see something they might not see themselves. Like something a close friend would say after a long pause."
- Output: single sentence woven into the next response naturally

**Anti-patterns (enforced via prompt):**
- No generic therapy-speak
- No parroting what the user just said
- No unsolicited advice
- Must reference something specific (dossier, conversation, or both)
- Must come from Jenbina's perspective, colored by her personality and emotions

### 4. Enhanced Greeting

**First-time user:**
- GPT-5.2 generates greeting with access to dossier
- Prompt: "You're meeting this person for the first time. You've heard things about them. Don't list facts. Greet them like someone genuinely curious — reference something that intrigued you, ask a question that shows you're not starting from zero."
- Example: Instead of "I see you work at a startup" -> "I have a feeling you're someone who builds things. Am I wrong?"

**Returning user:**
- Replace static messages with GPT-5.2 generated greetings
- References: what Jenbina was "doing" while they were gone (goals/planning), something from last conversation, her current emotional state
- Example: "I've been thinking about what you said about your sister. Also I tried learning about astronomy while you were gone — did you know Saturn has 146 moons? That feels excessive."

### 5. Inner Life Surfacing

No new subsystems — prompt engineering on existing systems.

**Chat prompt enrichment includes:**
- Jenbina's current goals
- Recent inner monologue thoughts
- Self-narrative
- Recent lessons learned
- Curiosity state (bored of what, interested in what)
- Instruction: "You have an inner life. Reference it when natural. Don't narrate your state — live it."

**Behavioral changes:**
- Spontaneous tangents from her own interests
- Opinions and disagreement (no people-pleasing)
- Pushes back respectfully when she disagrees based on her values

## New Dependencies

- Web search API: SerpAPI or Serper.dev (env var for API key)
- GPT-5.2 as chat model (env var change)

## Files to Create

- `insight_system.py` — InsightSystem class
- `user_research.py` — web search + dossier generation

## Files to Modify

- Auth/login flow — add research trigger after login
- Social cognition model — add `user_dossier` field to `PersonModel`
- Chat handler — upgrade model, enrich prompt, integrate insights
- Greeting system — replace static messages with GPT-5.2 generated
- Config/env — new API keys and model setting
