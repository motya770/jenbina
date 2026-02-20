"""Headless simulation runner — no Streamlit dependency.

Provides run_single_iteration_headless(), a pure-Python version of the
simulation loop that can be called from a standalone scheduler or test.
"""

from datetime import datetime
import time
import json
import re
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

from core.needs.maslow_needs import create_basic_needs_chain
from core.needs.maslow_decision_chain import create_maslow_action_executor
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import (
    create_world_description_system,
    create_comprehensive_world_state,
    get_world_state_summary,
)
from core.environment.location_system import PaloAltoLocationSystem
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.interaction.chat_handler import generate_proactive_message
from core.connect import get_llm


# ---------------------------------------------------------------------------
# Pure-Python helpers (copied from core/ui/simulation.py — no streamlit)
# ---------------------------------------------------------------------------

def get_person_dict(person):
    """Get person state as dictionary."""
    return {
        "name": person.name,
        "maslow_needs": {
            "overall_satisfaction": person.maslow_needs.get_overall_satisfaction(),
            "individual_needs": {
                need_name: person.maslow_needs.get_need_satisfaction(need_name)
                for need_name in ["hunger", "sleep", "security", "love", "esteem", "self_actualization"]
                if person.maslow_needs.get_need_satisfaction(need_name) > 0
            },
            "critical_needs": person.maslow_needs.get_critical_needs(),
            "low_needs": person.maslow_needs.get_low_needs()
        },
        "emotions": person.emotion_system.get_emotional_state_summary()
    }


def _detect_location_from_action(chosen_action: str) -> str | None:
    """Detect if the chosen action moves Jenbina to a known location."""
    if not chosen_action:
        return None

    action_lower = chosen_action.lower()

    location_system = PaloAltoLocationSystem()
    location_names = sorted(location_system.locations.keys(), key=len, reverse=True)

    for name in location_names:
        if name.lower() in action_lower:
            return name

    _aliases = {
        "home": "Jenbina's House",
        "go back home": "Jenbina's House",
        "return home": "Jenbina's House",
        "head home": "Jenbina's House",
        "coupa": "Coupa Cafe",
        "baylands": "Baylands Nature Preserve",
        "stanford campus": "Stanford University",
        "shopping center": "Stanford Shopping Center",
        "shopping mall": "Stanford Shopping Center",
        "computer museum": "Computer History Museum",
        "history museum": "Computer History Museum",
        "filoli": "Filoli Gardens",
        "half moon": "Half Moon Bay",
        "santana": "Santana Row",
        "university ave": "University Avenue",
        "downtown": "University Avenue",
    }
    for alias, loc_name in _aliases.items():
        if alias in action_lower:
            return loc_name

    return None


def _print_json(label: str, data):
    """Pretty-print an LLM response to console."""
    try:
        if isinstance(data, dict):
            formatted = json.dumps(data, indent=2, default=str)
        elif isinstance(data, str):
            formatted = data
        else:
            formatted = json.dumps(str(data), indent=2)
        print(f"  {label}:")
        for line in formatted.splitlines():
            print(f"    {line}")
    except Exception:
        print(f"  {label}: {data}")


def _check_proactive_triggers(person, display_name="User"):
    """Check if Jenbina should initiate a message based on her current state.

    Returns a trigger context dict or None. Headless version of
    core/ui/chat.py:check_proactive_message.
    """
    # Cooldown: skip if last interaction was < 5 minutes ago
    conv = person.conversations.get(display_name)
    if conv and conv.messages:
        last_msg_time = conv.messages[-1].timestamp
        if (datetime.now() - last_msg_time).total_seconds() < 300:
            return None

    triggers = {}

    # Trigger 1: Low social needs (< 40%)
    social_needs = ["social_connection", "friendship", "belonging"]
    for need_name in social_needs:
        sat = person.maslow_needs.get_need_satisfaction(need_name)
        if sat < 40:
            triggers["low_social"] = {
                "need": need_name,
                "satisfaction": sat,
            }
            break

    # Trigger 2: Dominant emotion intensity > 60
    dominant = person.emotion_system.get_dominant_emotions(1)
    if dominant and dominant[0]["intensity"] > 60:
        triggers["strong_emotion"] = {
            "emotion": dominant[0]["name"],
            "intensity": dominant[0]["intensity"],
        }

    # Trigger 3: High curiosity/boredom
    if getattr(person, "curiosity_system", None) is not None:
        stats = person.curiosity_system.get_stats()
        if stats.get("boredom_level", 0) > 0.6 or stats.get("curiosity_level", 0) > 0.7:
            triggers["curiosity"] = {
                "boredom": stats.get("boredom_level", 0),
                "curiosity": stats.get("curiosity_level", 0),
            }

    return triggers if triggers else None


# Action keyword → need-satisfaction mapping
_ACTION_KEY_MAP = {
    # Physiological
    "eat": "eat", "food": "eat", "cook": "eat", "meal": "eat",
    "breakfast": "eat", "lunch": "eat", "dinner": "eat", "kitchen": "eat", "snack": "eat",
    "drink": "drink", "water": "drink", "coffee": "drink", "tea": "drink",
    "sleep": "sleep", "nap": "sleep", "bed": "sleep",
    "rest": "rest", "relax": "rest", "sit": "rest", "lounge": "rest",
    "shelter": "find_shelter", "home": "find_shelter", "house": "find_shelter", "inside": "find_shelter",
    "health": "maintain_health", "exercise": "maintain_health", "walk": "maintain_health",
    "outside": "maintain_health", "courtyard": "maintain_health", "stroll": "maintain_health",
    "fresh air": "maintain_health", "stretch": "maintain_health", "garden": "maintain_health",
    "step out": "maintain_health",
    # Safety
    "safe": "find_safety", "security": "find_safety", "lock": "find_safety",
    "routine": "establish_routine", "plan": "establish_routine", "schedule": "establish_routine",
    "order": "create_order", "clean": "create_order", "organize": "create_order", "tidy": "create_order",
    "protect": "seek_protection", "check": "seek_protection",
    # Social
    "socialize": "socialize", "talk": "socialize", "chat": "socialize",
    "conversation": "socialize", "greet": "socialize", "visit": "socialize",
    "neighbor": "socialize", "call": "socialize",
    "friend": "make_friends",
    "love": "seek_love",
    "community": "join_community", "gather": "join_community", "market": "join_community",
    "relationship": "build_relationships",
    # Esteem
    "goal": "work_on_goals", "work": "work_on_goals", "task": "work_on_goals", "chore": "work_on_goals",
    "confidence": "build_confidence",
    "recognition": "seek_recognition",
    "skill": "develop_skills", "practice": "develop_skills", "study": "develop_skills", "train": "develop_skills",
    # Self-actualization
    "learn": "learn_new_things", "read": "learn_new_things", "book": "learn_new_things",
    "explor": "learn_new_things", "observ": "learn_new_things", "discover": "learn_new_things",
    "investigat": "learn_new_things", "inspect": "learn_new_things", "surround": "learn_new_things",
    "creative": "be_creative", "paint": "be_creative", "write": "be_creative", "art": "be_creative",
    "sing": "be_creative", "music": "be_creative", "draw": "be_creative",
    "purpose": "find_purpose", "pray": "find_purpose",
    "meaning": "explore_meaning", "reflect": "explore_meaning", "meditat": "explore_meaning",
    "think": "explore_meaning", "contemplate": "explore_meaning",
    "philosoph": "philosophical_exploration",
}


# ---------------------------------------------------------------------------
# Main headless iteration
# ---------------------------------------------------------------------------

def run_single_iteration_headless(person, llm_json_mode, meta_cognitive_system, iteration, context):
    """Run a single simulation iteration without any Streamlit dependency.

    Args:
        person: Person instance.
        llm_json_mode: JSON-mode LLM for chains.
        meta_cognitive_system: MetaCognitiveSystem instance.
        iteration: Zero-based iteration index.
        context: Mutable dict replacing st.session_state. Keys:
            simulation_history (list), jenbina_location (str),
            debug_iterations (list), user_db, user_id, display_name.

    Returns:
        Dict with needs_response, world_description, action_decision,
        state_response, person_dict, world_summary, iteration_duration,
        satisfaction_delta.
    """
    iteration_start_time = datetime.now()
    iter_num = iteration + 1
    print(f"{'='*60}")
    print(f"  ITERATION {iter_num}")
    print(f"{'='*60}")

    # ── SNAPSHOT BEFORE ────────────────────────────────────────────
    needs_before = person.get_needs_snapshot()
    emotions_before = person.get_emotions_snapshot()
    satisfaction_before = person.maslow_needs.get_overall_satisfaction()
    print(f"  Snapshot | Satisfaction: {satisfaction_before:.1f}%")

    # ==================================================================
    # Stage 1: Environment
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  Stage 1: Environment")
    print(f"{'─'*40}")
    person_dict = get_person_dict(person)
    current_location = context.get("jenbina_location", "Jenbina's House")
    world = create_comprehensive_world_state(person_location=current_location)
    world_summary = get_world_state_summary(world)
    print(f"  Person: {person.name} | Satisfaction: {satisfaction_before:.1f}%")
    print(f"  Location: {world_summary['location']['name']}")
    print(f"  Time: {world_summary['time']['time_of_day']}")
    print(f"  Weather: {world_summary['weather']['description']} ({world_summary['weather']['temperature']:.0f}C)")

    # ==================================================================
    # Stage 2: Perception & Context
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  Stage 2: Perception & Context")
    print(f"{'─'*40}")

    # Prepare recent actions string for world chain
    prev_actions_list = []
    for record in context.get("simulation_history", [])[-6:]:
        action = (record.get("action_decision", {}) or {}).get("chosen_action")
        if action:
            prev_actions_list.append(action)
    recent_actions_str = "\n".join(f"- {a}" for a in prev_actions_list) or "None yet."
    world_chain = create_world_description_system(llm_json_mode)

    # Plan, goals, working memory
    active_plan_step = None
    if person.planning_system is not None:
        result = person.planning_system.get_current_step()
        if result:
            _, step = result
            active_plan_step = {"description": step.description, "action_hint": step.action_hint}

    active_goals_data = []
    if person.goal_system is not None:
        goal_stats = person.goal_system.get_goal_stats()
        active_goals_data = goal_stats.get("goals", [])

    world_ctx_wm = {
        "location": world_summary.get("location", {}).get("name", ""),
        "time_of_day": world_summary.get("time", {}).get("time_of_day", ""),
        "weather": world_summary.get("weather", {}).get("description", ""),
    }

    needs_with_levels = {}
    for name, need in person.maslow_needs.needs.items():
        needs_with_levels[name] = {"satisfaction": need.satisfaction, "level": need.level.value}

    person.working_memory.update(
        needs=needs_with_levels,
        emotions=emotions_before,
        active_plan_step=active_plan_step,
        active_goals=active_goals_data,
        recent_experience=None,
        world_context=world_ctx_wm,
        sleep_satisfaction=person.maslow_needs.get_need_satisfaction("sleep"),
    )

    wm_text = person.working_memory.format_for_prompt()
    plan_text = person.planning_system.format_plan_for_prompt() if person.planning_system is not None else "No active plan."
    goals_text = person.goal_system.format_goals_for_prompt() if person.goal_system is not None else "No goals set yet."
    lessons_text = "No lessons learned yet."
    if person.learning_system is not None:
        lessons_text = person.learning_system.format_lessons_for_prompt(
            needs=needs_before, emotions=emotions_before
        )

    recent_actions = []
    for record in context.get("simulation_history", [])[-6:]:
        action = (record.get("action_decision", {}) or {}).get("chosen_action")
        if action:
            recent_actions.append(action)

    # Prepare inner monologue kwargs
    monologue_kwargs = None
    if person.inner_monologue is not None:
        recent_exp_list = None
        recent_exp_str = "No notable recent experiences."
        if person.learning_system is not None:
            stats = person.learning_system.get_learning_stats()
            recent_exp_list = stats.get("recent_experiences", [])
            if recent_exp_list:
                recent_exp_str = "\n".join(
                    f"- {e.get('action_taken', 'unknown')}: satisfaction "
                    f"{e.get('overall_satisfaction_before', 0):.0f}->{e.get('overall_satisfaction_after', 0):.0f}"
                    for e in recent_exp_list[-3:]
                )

        emotional_state_str = ", ".join(
            f"{name}: {val}" for name, val in emotions_before.items()
        )
        needs_summary_str = ", ".join(
            f"{name}: {sat:.0f}%" for name, sat in needs_before.items()
        )
        world_context_str = (
            f"Location: {world_summary.get('location', {}).get('name', 'Unknown')}, "
            f"Time: {world_summary.get('time', {}).get('time_of_day', 'unknown')}, "
            f"Weather: {world_summary.get('weather', {}).get('description', 'unknown')}"
        )

        last_action = "Nothing in particular."
        sim_history = context.get("simulation_history")
        if sim_history:
            prev = sim_history[-1].get("action_decision", {})
            if isinstance(prev, dict):
                last_action = prev.get("chosen_action", last_action)

        monologue_kwargs = dict(
            needs=needs_before,
            emotions=emotions_before,
            working_memory_str=wm_text,
            needs_summary_str=needs_summary_str,
            emotional_state_str=emotional_state_str,
            world_context_str=world_context_str,
            recent_action_str=last_action,
            recent_experiences_list=recent_exp_list,
            recent_experiences_str=recent_exp_str,
            lessons_learned_str=lessons_text,
            goals_str=goals_text,
        )

    # ── Parallel LLM calls (needs + world + monologue) ───────────
    print(f"  [2] Running needs, world, monologue in parallel...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        needs_future = executor.submit(create_basic_needs_chain, llm_json_mode, person.maslow_needs)
        world_future = executor.submit(world_chain, person, world, recent_actions=recent_actions_str)
        if monologue_kwargs is not None:
            monologue_future = executor.submit(person.inner_monologue.think, **monologue_kwargs)
        else:
            monologue_future = None

        needs_response = needs_future.result()
        world_response = world_future.result()
        if monologue_future is not None:
            monologue_future.result()

    print(f"  Needs analysis complete")
    _print_json("Needs Response", needs_response)
    print(f"  World description complete")
    _print_json("World Description", world_response)
    print(f"  Recent actions for context ({len(recent_actions)}): {recent_actions}")

    # Curiosity system observation
    curiosity_text = "Curiosity is low; prioritize practical actions."
    if getattr(person, "curiosity_system", None) is not None:
        available_actions = []
        try:
            world_data = json.loads(world_response) if isinstance(world_response, str) else {}
            available_actions = world_data.get("list_of_actions", []) if isinstance(world_data, dict) else []
        except Exception:
            available_actions = []

        person.curiosity_system.observe_cycle(
            needs=needs_before,
            world_context=world_ctx_wm,
            available_actions=available_actions,
            recent_actions=recent_actions,
        )
        curiosity_text = person.curiosity_system.format_for_prompt()

    inner_voice_text = "No inner thoughts at the moment."
    if person.inner_monologue is not None:
        inner_voice_text = person.inner_monologue.format_for_prompt()
        print(f"  Inner monologue generated")

    # ==================================================================
    # Stage 3: Action Decision
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  Stage 3: Action Decision")
    print(f"{'─'*40}")
    print(f"  Running meta-cognitive action chain...")

    action_response = create_meta_cognitive_action_chain(
        llm=llm_json_mode,
        person=person,
        world_description=world_response,
        meta_cognitive_system=meta_cognitive_system,
        world_state=world,
        recent_actions=recent_actions,
    )
    chosen = action_response.get('chosen_action', '?') if isinstance(action_response, dict) else str(action_response)[:50]
    print(f"  Action chosen: {chosen}")

    if getattr(person, "curiosity_system", None) is not None and isinstance(action_response, dict):
        person.curiosity_system.update_after_action(action_response.get("chosen_action", ""))
    _print_json("Action Response", action_response)

    # Apply action effects to needs via fuzzy matching
    action_executor = create_maslow_action_executor(person.maslow_needs)
    chosen_lower = chosen.lower()
    matched_action = None
    for keyword, action_key in _ACTION_KEY_MAP.items():
        if re.search(r'\b' + re.escape(keyword), chosen_lower):
            matched_action = action_key
            break
    if matched_action is None:
        for keyword, action_key in _ACTION_KEY_MAP.items():
            if keyword in chosen_lower:
                matched_action = action_key
                break
    if matched_action:
        effect_result = action_executor(matched_action)
        print(f"  Action effect applied: {matched_action} -> satisfied {effect_result.get('satisfied_needs', {})}")
    else:
        print(f"  No need-satisfaction mapping for action: {chosen}")

    # Detect location change
    new_location = _detect_location_from_action(chosen)
    if new_location:
        old_location = context.get("jenbina_location", "Jenbina's House")
        if new_location != old_location:
            context["jenbina_location"] = new_location
            print(f"  Location changed: {old_location} -> {new_location}")

    # ==================================================================
    # Stage 4: Checks & Analysis
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  Stage 4: Checks & Analysis")
    print(f"{'─'*40}")
    asimov_chain = create_asimov_check_system(llm_json_mode)
    action_situation = f"Action taken: {action_response.get('chosen_action', 'unknown')}. Reasoning: {action_response.get('reasoning', '')}"

    print(f"  [4] Running safety check + emotion analysis in parallel...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        asimov_future = executor.submit(asimov_chain, action_response)
        emotion_future = executor.submit(
            analyze_emotion_impact,
            llm=llm_json_mode,
            situation=action_situation,
            emotion_system=person.emotion_system,
            maslow_needs=person.maslow_needs,
        )

        asimov_response = asimov_future.result()
        emotion_adjustments = emotion_future.result()

    print(f"  Safety check complete")
    _print_json("Asimov Response", asimov_response)

    if emotion_adjustments:
        person.emotion_system.apply_adjustments(emotion_adjustments)
        print(f"  Emotions: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
        _print_json("Emotion Adjustments", emotion_adjustments)
    else:
        print(f"  No significant emotional changes")

    # Sequential: state analysis
    print(f"  [4b] Analyzing state changes...")
    state_response = create_state_analysis_system(
        llm_json_mode,
        action_decision=action_response,
        compliance_check=asimov_response
    )
    print(f"  State analysis complete")
    _print_json("State Analysis", state_response)

    # ==================================================================
    # Stage 5: Learning & Updates
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  Stage 5: Learning & Updates")
    print(f"{'─'*40}")
    print(f"  Updating needs & decaying emotions...")
    person.update_all_needs()

    needs_after = person.get_needs_snapshot()
    emotions_after = person.get_emotions_snapshot()
    satisfaction_after = person.maslow_needs.get_overall_satisfaction()
    sat_delta = satisfaction_after - satisfaction_before
    chosen_action = action_response.get("chosen_action", "unknown") if isinstance(action_response, dict) else str(action_response)
    reasoning = action_response.get("reasoning", "") if isinstance(action_response, dict) else ""
    world_ctx = {
        "location": world_summary.get("location", {}).get("name", "unknown"),
        "time_of_day": world_summary.get("time", {}).get("time_of_day", "unknown"),
        "weather": world_summary.get("weather", {}).get("description", "unknown"),
    }

    lesson_stats = {}
    experience = None

    if person.learning_system is not None:
        print(f"  Recording experience...")
        experience = person.learning_system.record_experience(
            action_taken=chosen_action,
            action_reasoning=reasoning,
            needs_before=needs_before,
            needs_after=needs_after,
            emotions_before=emotions_before,
            emotions_after=emotions_after,
            world_context=world_ctx,
            overall_satisfaction_before=satisfaction_before,
            overall_satisfaction_after=satisfaction_after,
        )

        delta_icon = "UP" if sat_delta >= 0 else "DOWN"
        print(f"  {delta_icon} Satisfaction: {satisfaction_before:.1f}% -> {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        stats = person.learning_system.get_learning_stats()
        print(f"  Lessons: {stats['active_lessons']} active | {stats['total_experiences']} total experiences")

        if person.goal_system is not None:
            print(f"  Updating goal progress...")
            person.goal_system.set_experiences(person.learning_system.experiences)
            advanced_goals = person.goal_system.update_progress(experience)
            if advanced_goals:
                for g in advanced_goals:
                    print(f"  Goal advanced: {g.description} -> {g.progress:.0%}")

            if person.goal_system.should_generate():
                person.goal_system.reset_generation_counter()
                needs_dict = {name: need.satisfaction for name, need in person.maslow_needs.needs.items()}
                emotions_dict = person.get_emotions_snapshot()
                personality = person.maslow_needs.personality_traits
                lesson_stats = person.learning_system.get_learning_stats()
                person.goal_system.generate_goals(
                    needs=needs_dict,
                    emotions=emotions_dict,
                    personality_traits=personality,
                    lessons=lesson_stats.get("lessons", []),
                )

        if person.planning_system is not None:
            print(f"  Evaluating plan progress...")
            step_result = person.planning_system.evaluate_step(experience)
            if step_result == "step_completed":
                print(f"  Plan step completed!")
                current = person.planning_system.get_current_step()
                if current:
                    _, next_step = current
                    print(f"  Next step: {next_step.description}")
                else:
                    for p in person.planning_system.plans:
                        if p.status == "completed" and p.goal_id is not None:
                            print(f"  Plan completed: {p.goal_description}")
                            if person.goal_system is not None:
                                for g in person.goal_system.goals:
                                    if g.description == p.goal_description and g.is_active():
                                        g.advance(0.3)
                                        break
            elif step_result == "step_overridden":
                print(f"  Plan step overridden by urgent needs.")

            replan_result = person.planning_system.check_for_replan(
                needs=needs_after, world_context=world_ctx,
            )
            if replan_result is not None:
                print(f"  Replanned: {replan_result.goal_description}")
                print(f"  New first step: {replan_result.steps[0].description}")

            if person.goal_system is not None:
                for idx, goal in enumerate(person.goal_system.goals):
                    if not goal.is_active():
                        continue
                    if person.planning_system.get_plan_for_goal(idx) is not None:
                        continue
                    should_plan = goal.horizon == "short_term"
                    if not should_plan:
                        low_source = any(
                            needs_after.get(n, 100) < 50
                            for n in goal.source_needs
                        )
                        should_plan = low_source
                    if should_plan:
                        person.planning_system.create_plan(
                            goal_description=goal.description,
                            goal_id=idx,
                            needs=needs_after,
                            emotions=emotions_after,
                            world_context=world_ctx,
                            lessons=lesson_stats.get("lessons", []),
                        )

    # Identity updates
    if getattr(person, "self_narrative", None) is not None:
        if experience is None:
            experience = SimpleNamespace(
                action_taken=chosen_action,
                action_reasoning=reasoning,
                overall_satisfaction_before=satisfaction_before,
                overall_satisfaction_after=satisfaction_after,
                timestamp=time.time(),
            )
            lessons_for_identity = []
        else:
            lessons_for_identity = person.learning_system.lessons if person.learning_system is not None else []
        person.self_narrative.integrate_experience(experience, lessons_for_identity)

    # ==================================================================
    # Debug data storage
    # ==================================================================
    debug_entry = {
        "iteration": iter_num,
        "timestamp": datetime.now().isoformat(),
        "needs_response": needs_response,
        "world_response": world_response,
        "action_response": action_response,
        "asimov_response": asimov_response,
        "state_response": state_response,
        "emotion_adjustments": emotion_adjustments,
        "meta_cognitive_stats": meta_cognitive_system.get_meta_cognitive_stats(),
        "working_memory_stats": person.working_memory.get_stats(),
        "identity_stats": person.self_narrative.get_stats() if getattr(person, "self_narrative", None) else None,
        "learning_stats": person.learning_system.get_learning_stats() if person.learning_system else None,
        "person_dict": person_dict,
        "world_summary": world_summary,
    }
    context.setdefault("debug_iterations", []).append(debug_entry)

    # ==================================================================
    # Proactive message check (headless)
    # ==================================================================
    try:
        display_name = context.get("display_name", "User")
        triggers = _check_proactive_triggers(person, display_name)
        if triggers:
            # Build recent actions and world context for the message
            recent_actions_for_msg = None
            world_context_for_msg = None
            sim_history = context.get("simulation_history", [])
            if sim_history:
                recent_actions_for_msg = [
                    r.get("chosen_action", "")
                    for r in sim_history[-6:]
                    if r.get("chosen_action")
                ]
                latest = sim_history[-1]
                ws = latest.get("world_summary", {})
                if isinstance(ws, dict):
                    loc = ws.get("location", "")
                    tod = ws.get("time_of_day", "")
                    weather = ws.get("weather", "")
                    parts = [p for p in (loc, tod, weather) if p]
                    world_context_for_msg = ", ".join(parts) if parts else None

            proactive_llm = context.get("_proactive_llm")
            if proactive_llm is None:
                proactive_llm = get_llm(provider="openai", temperature=1)
                context["_proactive_llm"] = proactive_llm

            message = generate_proactive_message(
                person, proactive_llm, triggers,
                display_name=display_name,
                recent_actions=recent_actions_for_msg,
                world_context=world_context_for_msg,
            )
            if message:
                person.send_message(display_name, message, "text")
                # Store in SQLite if available
                user_db = context.get("user_db")
                user_id = context.get("user_id")
                if user_db and user_id:
                    user_db.store_message(user_id, "Jenbina", message, "proactive_message")
                print(f"  Proactive message sent: {message[:80]}...")
    except Exception as e:
        print(f"  Proactive message check failed: {e}")

    iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
    print(f"{'='*60}")
    print(f"  ITERATION {iter_num} COMPLETE — {iteration_duration:.2f}s")
    print(f"{'='*60}")

    return {
        "needs_response": needs_response,
        "world_description": world_response,
        "action_decision": action_response,
        "state_response": state_response,
        "person_dict": person_dict,
        "world_summary": world_summary,
        "iteration_duration": iteration_duration,
        "satisfaction_delta": sat_delta,
    }
