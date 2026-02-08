# Working Memory Design

A short-term buffer of 3-7 items representing what Jenbina is currently thinking about. Items enter based on salience (urgency/importance), not LLM calls. Focus degrades with fatigue (tied to sleep need) and context switching has a cost.

## Data Structure: WorkingMemoryItem

| Field | Type | Description |
|---|---|---|
| content | str | Description ("hunger is critically low") |
| source | str | "need", "emotion", "plan_step", "goal", "experience", "environment" |
| salience | float | 0.0 to 1.0 |
| entered_at | float | Timestamp |
| source_id | str | Optional link back (need name, goal index) |

## Salience Calculation

- Needs: (100 - satisfaction) / 100 * level_weight (physio=1.0, safety=0.8, social=0.6, esteem=0.4, self-act=0.2)
- Emotions: intensity / 100 for top 2 dominant emotions
- Plan step: 0.7 if active
- Goals: (1 - progress) * confidence * 0.5
- Experience: 0.6 for most recent, decays to 0 after 3 cycles
- Environment: 0.5 for notable conditions

## Focus

- focus = clamp(sleep_satisfaction * 0.8 + 20, 30, 100)
- Buffer capacity: floor(3 + 4 * (focus / 100))
- Context switch penalty: -5 when top item changes source between cycles

## WorkingMemorySystem Methods

1. update() — main per-cycle method, calculates everything
2. get_focus() / get_buffer()
3. format_for_prompt() — for action decision injection
4. get_stats() / to_dict() / from_dict()

## Integration

- Person gets working_memory field (no LLM needed)
- Action decision prompt gets {working_memory} at the top
- Simulation loop calls update() before action decision
- Focus displayed in UI
