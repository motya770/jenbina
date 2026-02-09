# Planning System Design

Jenbina decomposes goals into multi-step plans and executes them across cycles, enabling chain-of-thought reasoning like "to eat, I need to go to the store, but first I need money, so first I need to work."

The planning layer sits between the goal system and the action decision chain. Each cycle, it feeds the current step to the action decision as a strong suggestion. The action decision can still override for urgent needs.

## Data Structures

### PlanStep

| Field | Type | Description |
|---|---|---|
| description | str | What to do ("go to the store") |
| action_hint | str | Suggested action for the action decision chain |
| expected_outcome | str | What success looks like |
| estimated_cycles | int | LLM's estimate of how many cycles this takes |
| actual_cycles | int | Counter, incremented each cycle the step is active |
| status | str | "pending", "active", "completed", "failed" |
| failure_reason | str | Why it failed (if applicable) |

### Plan

| Field | Type | Description |
|---|---|---|
| goal_description | str | The goal this plan serves |
| goal_id | int | Index into GoalSystem.goals |
| steps | list[PlanStep] | Ordered list of steps |
| current_step_index | int | Which step we're on |
| status | str | "active", "completed", "failed", "replanned" |
| times_replanned | int | Counter (capped at MAX_REPLANS) |
| created_at | float | Timestamp |

### Step completion detection

After each cycle, compare the experience's need deltas against the current step. If the action decision chose the step's action_hint and satisfaction improved, mark step completed and advance. If the step exceeds 2x estimated_cycles, trigger replan.

## PlanningSystem Class

### Configuration

- MAX_ACTIVE_PLANS = 3 (one per horizon)
- MAX_REPLANS = 3 per plan
- STUCK_MULTIPLIER = 2.0 (replan if actual_cycles > estimated_cycles * 2)

### Methods

1. **create_plan(goal, needs, emotions, world_context)** — LLM call that decomposes a goal into 2-6 ordered steps with action hints and cycle estimates. Only creates a plan if the goal doesn't already have one.

2. **get_current_step()** — Returns the active step from the highest-priority active plan. Priority: short-term first, then mid, then long.

3. **evaluate_step(experience)** — Called after each cycle. Checks if current step was advanced. Marks completed and advances, or increments actual_cycles.

4. **check_for_replan()** — If current step is stuck (exceeded 2x estimate) or overridden 3+ consecutive cycles, triggers replan().

5. **replan(plan, current_needs, world_context)** — LLM call that generates a new plan from current state given what's been accomplished and why the step failed. Increments times_replanned. If at MAX_REPLANS, abandons plan.

6. **format_plan_for_prompt()** — Formats current step as directive for action decision prompt.

7. **to_dict() / from_dict()** — Serialization.

## LLM Prompts

### Plan Generation Prompt

Input: goal description, current needs, emotions, world context, learned lessons.

Output:
```json
{
  "steps": [
    {"description": "Find a job opportunity", "action_hint": "look for work", "expected_outcome": "have a job lead", "estimated_cycles": 2},
    {"description": "Work to earn money", "action_hint": "work", "expected_outcome": "earn income", "estimated_cycles": 3}
  ]
}
```

### Replan Prompt

Input: original goal, completed steps so far, failed step with reason, current needs/world context.

Output: new steps array starting from current state.

## Integration

- Action decision prompt gets `{current_plan_step}` variable, placed above goals and lessons (highest priority)
- Format: "Current Plan Step (follow this unless urgent needs override): Goal: X. Step N of M: Y. Suggested action: Z."
- Person gets a `planning_system` field, initialized like learning_system
- Simulation loop: after goal generation, create plans for active goals
- Short-term goals get planned immediately
- Mid/long-term goals wait until source needs drop below 50%
- Plan completion advances goal progress by +0.3
- Plan abandonment (MAX_REPLANS exceeded) reduces goal confidence by -0.2
