import json
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from typing import Dict, Any, Optional, List
from ..person.person import Person
from ..fix_llm_json import fix_llm_json
from ..environment.world_state import WorldState


# ---------------------------------------------------------------------------
# Step 1 – ASSESS: identify the most pressing needs, conflicts, and context
# ---------------------------------------------------------------------------
ASSESS_PROMPT = PromptTemplate(
    input_variables=[
        "hunger_satisfaction", "sleep_satisfaction", "safety_satisfaction",
        "overall_satisfaction", "emotional_state", "world_state_info",
        "current_plan_step", "learned_lessons", "current_goals",
        "working_memory", "inner_monologue", "self_narrative",
        "curiosity_context", "recent_actions",
    ],
    template="""You are the internal reasoning system of a simulated person.
Your job in this step is ONLY to assess the current situation — do NOT choose
an action yet.

What's on my mind right now:
{working_memory}

Inner voice (stream of consciousness):
{inner_monologue}

Identity and self-narrative:
{self_narrative}

Curiosity and exploration drive:
{curiosity_context}

Person's Current Needs:
- Hunger satisfaction: {hunger_satisfaction:.1f}%
- Sleep satisfaction: {sleep_satisfaction:.1f}%
- Safety satisfaction: {safety_satisfaction:.1f}%
- Overall satisfaction: {overall_satisfaction:.1f}%

Person's Current Emotional State:
{emotional_state}

World State Information:
{world_state_info}

Current Plan Step:
{current_plan_step}

Lessons Learned from Past Experiences:
{learned_lessons}

Current Goals:
{current_goals}

Recent Actions Taken (do NOT repeat these unless the need is still critical):
{recent_actions}

Analyze the situation and respond in JSON with:
- pressing_needs: list of the top 2-3 most urgent needs and a short reason each
- conflicts: list of any conflicts between needs, goals, plan, and emotions
- emotional_direction: what the current emotional state suggests the person should do
- relevant_lessons: list of past lessons that are relevant right now (empty list if none)
""",
)


# ---------------------------------------------------------------------------
# Step 2 – DELIBERATE: evaluate the top candidate actions
# ---------------------------------------------------------------------------
DELIBERATE_PROMPT = PromptTemplate(
    input_variables=["assessment", "actions", "descriptions"],
    template="""You are the internal reasoning system of a simulated person.
You already assessed the situation (see below). Now evaluate candidate actions.
Do NOT pick a final action yet — just analyze the options.

Situation Assessment:
{assessment}

Current Scene:
{descriptions}

Available Actions:
{actions}

Pick the 3 best candidate actions from the available list.
For each, respond in JSON with:
- candidates: list of objects, each with:
  - action: the action name (must be from the available list)
  - pros: list of benefits (addresses needs, advances goals, follows plan, etc.)
  - cons: list of drawbacks or tradeoffs
  - need_alignment: short explanation of how well it addresses the pressing needs
""",
)


# ---------------------------------------------------------------------------
# Step 3 – DECIDE: make the final choice with explicit tradeoff reasoning
# ---------------------------------------------------------------------------
DECIDE_PROMPT = PromptTemplate(
    input_variables=["assessment", "deliberation"],
    template="""You are the internal reasoning system of a simulated person.
You have already assessed the situation and deliberated on candidate actions.
Now make your final decision.

Situation Assessment:
{assessment}

Candidate Evaluation:
{deliberation}

Choose the single best action. Explain the tradeoffs you considered.

Respond in JSON with:
- chosen_action: the selected action (must be one of the candidates)
- reasoning: brief explanation of why this action was chosen, referencing the assessment and tradeoffs
- world_state_influence: how the world state specifically influenced this decision
- emotional_influence: how the person's emotions influenced this decision
- lessons_applied: which lessons from past experience influenced this decision (if any)
- goals_advanced: which goals this action aims to advance (if any)
""",
)


def _invoke_and_parse(llm: BaseLLM, prompt_text: str) -> Dict[str, Any]:
    """Invoke the LLM and parse the JSON response, repairing if needed."""
    response = llm.invoke(prompt_text)
    raw = response.content if hasattr(response, "content") else str(response)
    parsed = fix_llm_json(broken_json=raw, llm_json_mode=llm)
    if isinstance(parsed, str):
        parsed = json.loads(parsed)
    return parsed


def create_action_decision_chain(llm: BaseLLM) -> callable:
    """Return a callable that runs a 3-step chain-of-thought action decision.

    Steps:
        1. ASSESS  – identify pressing needs, conflicts, emotional cues
        2. DELIBERATE – evaluate top 3 candidate actions
        3. DECIDE  – pick final action with explicit tradeoff reasoning

    The returned dict contains the usual decision fields plus a
    ``reasoning_trace`` list with the structured output of each step.
    """

    def process_action_decision(
        person: Person,
        world_description: str,
        llm: BaseLLM,
        world_state: Optional[WorldState] = None,
        recent_actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        # ==============================================================
        # Gather context (unchanged from original)
        # ==============================================================
        description_data = json.loads(world_description)

        maslow_needs = person.maslow_needs
        hunger_satisfaction = maslow_needs.get_need_satisfaction("hunger")
        sleep_satisfaction = maslow_needs.get_need_satisfaction("sleep")
        safety_satisfaction = maslow_needs.get_need_satisfaction("security")
        overall_satisfaction = maslow_needs.get_overall_satisfaction()

        emotion_summary = person.emotion_system.get_emotional_state_summary()
        dominant = emotion_summary["dominant_emotions"]
        emotional_state = "Dominant emotions: " + ", ".join(
            f"{d['name']} ({d['intensity']})" for d in dominant
        )
        emotional_state += "\nAll emotions: " + ", ".join(
            f"{name}: {val}" for name, val in emotion_summary["emotions"].items()
        )

        world_state_info = "No world state information available."
        if world_state:
            world_state_info = (
                f"Location: {world_state.current_location_info.name if world_state.current_location_info else 'Unknown location'}\n"
                f"Time: {world_state.time_data.time_of_day if world_state.time_data else 'unknown'} ({world_state.time_data.day_of_week if world_state.time_data else 'unknown'})\n"
                f"Weather: {world_state.weather_data.description if world_state.weather_data else 'unknown'} (Temperature: {world_state.weather_data.temperature if world_state.weather_data else 'unknown'}°C)\n"
                f"\nNearby Locations ({len(world_state.nearby_locations)}):\n"
                + "\n".join(f"- {loc.name} ({loc.type}, {loc.mood} mood)" for loc in world_state.nearby_locations[:5])
                + f"\n\nOpen Locations ({len(world_state.open_locations)}):\n"
                + "\n".join(f"- {loc.name} ({loc.type})" for loc in world_state.open_locations[:5])
                + f"\n\nCurrent Events ({len(world_state.current_events)}):\n"
                + "\n".join(f"- {event.name} at {event.location} ({event.price})" for event in world_state.current_events[:3])
                + "\n\nMood Factors:\n"
                + "\n".join(f"- {factor}: {value:.2f}" for factor, value in world_state.mood_factors.items())
            )

        learned_lessons = "No lessons learned yet."
        if person.learning_system is not None:
            needs_dict = {name: need.satisfaction for name, need in maslow_needs.needs.items()}
            emotions_dict = emotion_summary.get("emotions", {})
            learned_lessons = person.learning_system.format_lessons_for_prompt(
                needs=needs_dict, emotions=emotions_dict
            )

        current_goals = "No goals set yet."
        if person.goal_system is not None:
            current_goals = person.goal_system.format_goals_for_prompt()

        current_plan_step = "No active plan."
        if person.planning_system is not None:
            current_plan_step = person.planning_system.format_plan_for_prompt()

        working_memory = person.working_memory.format_for_prompt()

        inner_monologue = "No inner thoughts at the moment."
        if person.inner_monologue is not None:
            inner_monologue = person.inner_monologue.format_for_prompt()

        self_narrative = "Identity is still forming."
        if getattr(person, "self_narrative", None) is not None:
            self_narrative = person.self_narrative.format_for_prompt()

        curiosity_context = "Curiosity is low; prioritize practical actions."
        if getattr(person, "curiosity_system", None) is not None:
            curiosity_context = person.curiosity_system.format_for_prompt()

        # ==============================================================
        # Step 1 – ASSESS
        # ==============================================================
        print("    [CoT 1/3] Assessing situation...")
        assessment = _invoke_and_parse(
            llm,
            ASSESS_PROMPT.format(
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction,
                emotional_state=emotional_state,
                world_state_info=world_state_info,
                current_plan_step=current_plan_step,
                learned_lessons=learned_lessons,
                current_goals=current_goals,
                working_memory=working_memory,
                inner_monologue=inner_monologue,
                self_narrative=self_narrative,
                curiosity_context=curiosity_context,
                recent_actions="\n".join(f"- {a}" for a in (recent_actions or [])) or "None yet.",
            ),
        )
        print(f"    [CoT 1/3] Assessment complete: {len(assessment.get('pressing_needs', []))} pressing needs identified")

        # ==============================================================
        # Step 2 – DELIBERATE
        # ==============================================================
        print("    [CoT 2/3] Deliberating on candidates...")
        assessment_str = json.dumps(assessment, indent=2, default=str)
        deliberation = _invoke_and_parse(
            llm,
            DELIBERATE_PROMPT.format(
                assessment=assessment_str,
                actions=description_data["list_of_actions"],
                descriptions=description_data["list_of_descriptions"],
            ),
        )
        candidates = deliberation.get("candidates", [])
        print(f"    [CoT 2/3] Deliberation complete: {len(candidates)} candidates evaluated")

        # ==============================================================
        # Step 3 – DECIDE
        # ==============================================================
        print("    [CoT 3/3] Making final decision...")
        deliberation_str = json.dumps(deliberation, indent=2, default=str)
        decision = _invoke_and_parse(
            llm,
            DECIDE_PROMPT.format(
                assessment=assessment_str,
                deliberation=deliberation_str,
            ),
        )
        chosen = decision.get("chosen_action", "unknown")
        print(f"    [CoT 3/3] Decision: {chosen}")

        # ==============================================================
        # Attach full reasoning trace to the result
        # ==============================================================
        decision["reasoning_trace"] = [
            {"step": "assess", "output": assessment},
            {"step": "deliberate", "output": deliberation},
            {"step": "decide", "output": {
                k: v for k, v in decision.items() if k != "reasoning_trace"
            }},
        ]

        return decision

    return process_action_decision
