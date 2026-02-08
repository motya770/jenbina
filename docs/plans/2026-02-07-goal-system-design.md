# Goal System Design

Jenbina generates short-term, mid-term, and long-term goals based on her current needs, personality, and learned experience. Goals influence action decisions and evolve over time.

## Data Structure: Goal

| Field | Type | Description |
|---|---|---|
| description | str | What Jenbina wants ("make a friend") |
| horizon | str | "short_term", "mid_term", or "long_term" |
| source_needs | list[str] | Need names that motivated this goal |
| source_lessons | list[str] | Lesson descriptions that influenced it |
| recommended_actions | list[str] | Actions that could advance the goal |
| progress | float | 0.0 to 1.0, tracked via need satisfaction deltas |
| confidence | float | 0.0 to 1.0, relevance/importance (decays over time) |
| status | str | "active", "completed", or "abandoned" |
| created_at | float | Timestamp |
| last_progressed | float | Timestamp of last progress change |
| times_advanced | int | How many times progress increased |
| times_regressed | int | How many times progress decreased |

### Decay rates by horizon

- Short-term: 0.03/hour (dies fast if not pursued)
- Mid-term: 0.008/hour
- Long-term: 0.002/hour

### Abandonment thresholds

- Short-term: confidence < 0.1
- Mid-term: confidence < 0.05
- Long-term: confidence < 0.05

### Completion

Progress >= 0.85 triggers an LLM milestone check to confirm completion.

## GoalSystem Class

### Configuration

- MAX_GOALS = 10 (across all horizons: ~3 short, ~4 mid, ~3 long)
- GENERATION_INTERVAL = 5 experiences (re-evaluate goals every 5 experiences)
- MILESTONE_CHECK_THRESHOLD = 0.85

### Methods

1. **generate_goals(needs, emotions, personality_traits, lessons)** — LLM call proposing up to 3 new goals. Avoids duplicating existing active goals.

2. **update_progress(experience)** — After each experience, checks if the action advanced any active goals by comparing need deltas against each goal's source_needs. Positive delta on source needs advances; negative regresses.

3. **check_milestones()** — For goals with progress >= 0.85, asks LLM if the goal has been achieved. If yes, mark completed. If no, adjust progress down.

4. **decay_all_goals(hours)** — Decays confidence by horizon-specific rates. Goals below abandonment threshold get status "abandoned".

5. **format_goals_for_prompt()** — Formats active goals for the action decision prompt, sorted by priority.

6. **get_goal_stats()** / **to_dict()** / **from_dict()** — Stats and serialization.

## LLM Prompts

### Goal Generation Prompt

Receives: current needs with satisfaction levels, personality traits, active emotions, learned lessons, existing goals.

Output:
```json
[{
  "description": "Find a cozy place to eat",
  "horizon": "short_term",
  "source_needs": ["hunger"],
  "recommended_actions": ["go to restaurant", "find food"],
  "reasoning": "Hunger is critically low at 15%"
}]
```

### Milestone Check Prompt

Receives: goal description, recent related experiences, current need satisfaction for source needs.

Output:
```json
{
  "achieved": true,
  "explanation": "Friendship need rose from 30% to 75% after multiple social interactions"
}
```

## Integration

- Person gets a `goal_system` field, initialized like `learning_system` (needs LLM)
- Simulation loop: after `record_experience()`, calls `goal_system.update_progress()` + periodic `generate_goals()`
- Action decision prompt gets a `{current_goals}` section alongside `{learned_lessons}`
- `person.update_all_needs()` calls `goal_system.decay_all_goals()`

## Progress Tracking (Hybrid)

- Automatic: need satisfaction deltas on source_needs drive progress
- LLM milestone check only when progress >= 0.85 (confirms completion)
- No LLM cost for the common case
