"""Simulation UI components and runner for Jenbina app"""
import streamlit as st
from datetime import datetime
import time
import html
import json
import math
import re
import os
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

from core.needs.maslow_needs import create_basic_needs_chain
from core.needs.maslow_decision_chain import create_maslow_action_executor
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import create_world_description_system, create_comprehensive_world_state, get_world_state_summary
from core.environment.location_system import PaloAltoLocationSystem
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.timeline import (
    ACTION,
    THOUGHT,
    record_action,
    record_goal_changes,
    record_mood,
    record_move,
    record_plan_finished,
    record_plan_step,
    record_replan,
    record_thought,
    snapshot_goals,
)
from core.simulation_runner import HEADLINE_NEEDS, credit_completed_plan, match_action_key
from core.ui.chat import get_event_log, send_proactive_message
from core.ui.pixel_theme import action_icon, delta_badge_html, event_html, icon_html, sprite_html
from core.ui.timeline import action_details_text, first_sentence


# Painterly portraits, one per state (``jenbina_<state>.png``). The pixel
# sprite for the same state is looked up by name through ``sprite_html``.
IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "portraits"
)
PORTRAIT_WIDTH = 256


def _get_image_path(name):
    """Get absolute path to a Jenbina image."""
    return os.path.join(IMAGES_DIR, name)


def get_jenbina_image_for_action(chosen_action):
    """Determine which Jenbina image to show based on the chosen action."""
    action_lower = chosen_action.lower() if chosen_action else ""

    # Action-based mapping
    action_map = [
        (["eat", "food", "cook", "meal", "snack", "breakfast", "lunch", "dinner", "hungry"], "jenbina_eat.png"),
        (["drink", "water", "thirst", "hydrat", "beverage", "tea", "coffee"], "jenbina_drink.png"),
        (["walk", "move", "explor", "travel", "wander", "go to", "visit", "roam", "stroll"], "jenbina_walks.png"),
        (["sleep", "rest", "nap", "bed", "doze"], "jenbina_sleep.png"),
        (["talk", "chat", "convers", "speak", "social", "friend", "greet", "discuss"], "jenbina_talk.png"),
        (["read", "study", "learn", "book", "research", "reflect", "meditat", "think", "journal"], "jenbina_read.png"),
    ]

    for keywords, image_name in action_map:
        for kw in keywords:
            if kw in action_lower:
                return _get_image_path(image_name)

    return None  # No action-specific image matched


def get_jenbina_image_for_emotion(person):
    """Determine which Jenbina image to show based on dominant emotion."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return _get_image_path("jenbina_base.png")

    top_emotion = dominant[0]["name"].lower()
    intensity = dominant[0]["intensity"]

    if top_emotion == "joy" and intensity > 30:
        return _get_image_path("jenbina_smile.png")
    elif top_emotion == "sadness" and intensity > 30:
        return _get_image_path("jenbina_sad.png")
    elif top_emotion == "anger" and intensity > 30:
        return _get_image_path("jenbina_angry.png")
    elif top_emotion == "fear" and intensity > 30:
        return _get_image_path("jenbina_scary.png")
    elif top_emotion == "surprise" and intensity > 30:
        return _get_image_path("jenbina_surprised.png")

    return _get_image_path("jenbina_base.png")


def _portrait_path(state):
    """The portrait file for ``state``, the ``base`` portrait if that is missing, else None."""
    for candidate in (state, "base"):
        path = os.path.join(IMAGES_DIR, f"jenbina_{candidate}.png")
        if os.path.isfile(path):
            return path
    return None


def display_jenbina_image(image_path, caption=None, width=PORTRAIT_WIDTH):
    """Show the painterly portrait for the state named by ``image_path`` in a
    game window, with the half-size animated pixel sprite and the caption in
    a status strip underneath.

    The state is the file name without ``jenbina_`` and ``.png``, so legacy
    paths keep working; unknown names fall back to ``base``. Without any
    portrait on disk only the sprite strip is shown.
    """
    name = os.path.basename(str(image_path or ""))
    state = name[len("jenbina_"):] if name.startswith("jenbina_") else name
    if state.endswith(".png"):
        state = state[:-4]
    portrait = _portrait_path(state)
    if portrait:
        st.image(portrait, width=width)
    st.markdown(sprite_html(state, caption, scale=2), unsafe_allow_html=True)


# Weather keyword -> icon name; the first match wins, so specific words come first.
_WEATHER_ICONS = {
    "storm": "storm",
    "snow": "snow",
    "rain": "rain",
    "fog": "fog",
    "wind": "wind",
    "sunny": "sunny",
    "clear": "sunny",
    "cloudy": "cloudy",
    "overcast": "cloudy",
}
_DEFAULT_WEATHER_ICON = "cloudy"


def _weather_icon(description):
    text = (description or "").lower()
    for keyword, icon in _WEATHER_ICONS.items():
        if keyword in text:
            return icon
    return _DEFAULT_WEATHER_ICON


NEED_SEGMENTS = 10


def render_needs_bars(person):
    """Render Maslow needs as ten-segment pixel bars with 8x8 icons."""
    # (css key, label, need in MaslowNeedsSystem): the css key names the row's
    # class and icon; Esteem and Growth show one representative need of their level.
    needs_config = [
        ("hunger", "Hunger", "hunger"),
        ("sleep", "Sleep", "sleep"),
        ("security", "Safety", "security"),
        ("love", "Social", "love"),
        ("esteem", "Esteem", "self_esteem"),
        ("self_actualization", "Growth", "personal_growth"),
    ]

    rows = []
    for need_name, label, need_key in needs_config:
        satisfaction = person.maslow_needs.get_need_satisfaction(need_key)
        if satisfaction is None or (isinstance(satisfaction, float) and math.isnan(satisfaction)):
            satisfaction = 0
        pct = max(0, min(100, satisfaction))
        filled = int((pct + 5) // NEED_SEGMENTS)   # round half up: 85% shows 9 segments, not 8

        if pct < 30:
            level = " need-critical"
        elif pct < 60:
            level = " need-mid"
        else:
            level = ""
        row_class = f"need-row need-{need_name}{level}"

        segments = (
            '<span class="need-seg on"></span>' * filled
            + '<span class="need-seg"></span>' * (NEED_SEGMENTS - filled)
        )
        rows.append(
            f'<div class="{row_class}">{icon_html(need_name, alt=label)}'
            f'<span class="need-label">{label}</span>'
            f'<div class="need-segs">{segments}</div>'
            f'<span class="need-pct">{pct:.0f}%</span></div>'
        )

    st.markdown("".join(rows), unsafe_allow_html=True)


def _css_token(name):
    """Lower-case ``name`` reduced to [a-z0-9_] so it is safe inside a class attribute."""
    return re.sub(r"[^a-z0-9_]", "", str(name).lower())


def render_emotion_chips(person):
    """Render the strongest emotions (above 15, at most four) as square badges."""
    all_emotions = person.emotion_system.get_emotional_state_summary().get("emotions", {})
    visible = sorted(
        [(name, val) for name, val in all_emotions.items() if val > 15],
        key=lambda x: x[1],
        reverse=True,
    )[:4]

    if not visible:
        return

    chips = "".join(
        f'<span class="emotion-chip emotion-{_css_token(name)}">{icon_html(name.lower(), alt=name)}'
        f'{html.escape(name.capitalize())} {intensity:.0f}</span>'
        for name, intensity in visible
    )
    st.markdown(f'<div class="emotion-chips">{chips}</div>', unsafe_allow_html=True)


POSITIVE_EMOTIONS = {"joy", "trust", "anticipation", "surprise"}


def render_mood_indicator(person):
    """Render a square badge with Jenbina's dominant mood: green when positive, red otherwise."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return

    emotion_name = str(dominant[0]["name"]).lower()
    intensity = int(dominant[0]["intensity"])
    polarity = "mood-positive" if emotion_name in POSITIVE_EMOTIONS else "mood-negative"

    st.markdown(
        f'<span class="mood-badge {polarity}">{icon_html(emotion_name, alt=emotion_name)}'
        f'{html.escape(emotion_name.capitalize())} {intensity}</span>',
        unsafe_allow_html=True,
    )


def get_person_dict(person):
    """Get person state as dictionary for display"""
    return {
        "name": person.name,
        "maslow_needs": {
            "overall_satisfaction": person.maslow_needs.get_overall_satisfaction(),
            "individual_needs": {
                need_name: person.maslow_needs.get_need_satisfaction(need_name)
                for need_name in HEADLINE_NEEDS
            },
            "critical_needs": person.maslow_needs.get_critical_needs(),
            "low_needs": person.maslow_needs.get_low_needs()
        },
        "emotions": person.emotion_system.get_emotional_state_summary()
    }


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


def _detect_location_from_action(chosen_action: str) -> str | None:
    """Detect if the chosen action moves Jenbina to a known location.

    Returns the location name if a match is found, otherwise None.
    """
    if not chosen_action:
        return None

    action_lower = chosen_action.lower()

    # All known locations — order matters: check longer/more specific names first
    location_system = PaloAltoLocationSystem()
    location_names = sorted(location_system.locations.keys(), key=len, reverse=True)

    for name in location_names:
        if name.lower() in action_lower:
            return name

    # Keyword aliases for common references
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


def _now_hhmm() -> str:
    return datetime.now().strftime("%H:%M")


def run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration, rail=None, event_log=None):
    """Run a single simulation iteration.

    The computation happens here; the screen is updated through ``rail`` (a
    ``StatusRail``: stage pill, portrait, vitals, live timeline rows) and the
    events of the iteration are recorded in ``event_log``. Without a rail
    nothing is drawn; without a log the session's log is used.
    """
    from core.ui.rail import NullRail  # local import: rail.py imports this module's renderers
    rail = rail if rail is not None else NullRail()
    event_log = event_log if event_log is not None else get_event_log()

    iteration_start_time = datetime.now()
    iter_num = iteration + 1
    print(f"{'='*60}")
    print(f"  🔄 ITERATION {iter_num}")
    print(f"{'='*60}")

    # ── SNAPSHOT BEFORE ─────────────────────────────────────────────────
    needs_before = person.get_needs_snapshot()
    emotions_before = person.get_emotions_snapshot()
    satisfaction_before = person.maslow_needs.get_overall_satisfaction()
    print(f"📸 Snapshot | Satisfaction: {satisfaction_before:.1f}%")

    # ==================================================================
    # Environment row — fast local data, render immediately
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  🌍 Stage 1: Environment")
    print(f"{'─'*40}")
    rail.stage("looking around…")
    person_dict = get_person_dict(person)
    # Use tracked location (updated after each action) or default to home
    current_location = st.session_state.get("jenbina_location", "Jenbina's House")
    world = create_comprehensive_world_state(person_location=current_location)
    world_summary = get_world_state_summary(world)
    print(f"  👤 Person: {person.name} | Satisfaction: {satisfaction_before:.1f}%")
    print(f"  📍 Location: {world_summary['location']['name']}")
    print(f"  🕐 Time: {world_summary['time']['time_of_day']}")
    print(f"  🌤️  Weather: {world_summary['weather']['description']} ({world_summary['weather']['temperature']:.0f}°C)")

    # ── Status rail: place and portrait ───────────────────────────────
    rail.world_summary = world_summary
    rail.portrait(get_jenbina_image_for_emotion(person), caption=f"{person.name}")

    # ==================================================================
    # Stage 2 — Perception & Context  (compute, render later)
    # ==================================================================

    # ── Local prep for Stage 2 (sequential) ─────────────────────
    print(f"{'─'*40}")
    print(f"  🧠 Stage 2: Perception & Context")
    print(f"{'─'*40}")
    rail.stage("thinking…")

    # Prepare recent actions string for world chain
    prev_actions_list = []
    for record in st.session_state.get("simulation_history", [])[-6:]:
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
    for record in st.session_state.get("simulation_history", [])[-6:]:
        action = (record.get("action_decision", {}) or {}).get("chosen_action")
        if action:
            recent_actions.append(action)

    # Prepare inner monologue kwargs (local prep only)
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
                    f"{e.get('overall_satisfaction_before', 0):.0f}→{e.get('overall_satisfaction_after', 0):.0f}"
                    for e in recent_exp_list[-3:]
                )

        emotional_state_str = ", ".join(
            f"{name}: {val}" for name, val in emotions_before.items()
        )
        needs_summary_str = ", ".join(
            f"{name}: {sat:.0f}%" for name, sat in needs_before.items()
        )
        social_day_str = ""
        if getattr(person, "social_interaction_tracker", None) is not None:
            social_day_str = "\n" + person.social_interaction_tracker.format_for_prompt()
        world_context_str = (
            f"Location: {world_summary.get('location', {}).get('name', 'Unknown')}, "
            f"Time: {world_summary.get('time', {}).get('time_of_day', 'unknown')}, "
            f"Weather: {world_summary.get('weather', {}).get('description', 'unknown')}"
            f"{social_day_str}"
        )

        last_action = "Nothing in particular."
        if st.session_state.get("simulation_history"):
            prev = st.session_state["simulation_history"][-1].get("action_decision", {})
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
    print(f"  🚀 [2] Running needs, world, monologue in parallel...")
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
            monologue_future.result()  # mutates person.inner_monologue in-place

    print(f"  ✅ Needs analysis complete")
    _print_json("📊 Needs Response", needs_response)
    print(f"  ✅ World description complete")
    _print_json("🌐 World Description", world_response)
    print(f"  📋 Recent actions for context ({len(recent_actions)}): {recent_actions}")

    # Curiosity system observation (depends on world_response)
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
        print(f"  ✅ Inner monologue generated")

    # The thought goes to the timeline: persisted, and shown live
    thought_event = record_thought(event_log, person.inner_monologue)
    if thought_event is not None:
        rail.live_row(event_html(THOUGHT, first_sentence(thought_event.title)[0], meta=_now_hhmm()))

    # Card 3: Action Decision (LLM call → display)
    print(f"{'─'*40}")
    print(f"  ⚡ Stage 3: Action Decision")
    print(f"{'─'*40}")
    rail.stage("deciding…")
    print(f"  🤔 Running meta-cognitive action chain...")

    # Show thinking image while deciding
    rail.portrait(_get_image_path("jenbina_thinking.png"), caption=f"{person.name} is thinking...")

    action_response = create_meta_cognitive_action_chain(
        llm=llm_json_mode,
        person=person,
        world_description=world_response,
        meta_cognitive_system=meta_cognitive_system,
        world_state=world,
        recent_actions=recent_actions,
    )
    chosen = action_response.get('chosen_action', '?') if isinstance(action_response, dict) else str(action_response)[:50]
    print(f"  ✅ Action chosen: {chosen}")

    # Update avatar to reflect the chosen action (or fall back to emotion)
    action_image = get_jenbina_image_for_action(chosen)
    if action_image is None:
        action_image = get_jenbina_image_for_emotion(person)
    rail.portrait(action_image, caption=f"{person.name}: {chosen}")

    if getattr(person, "curiosity_system", None) is not None and isinstance(action_response, dict):
        person.curiosity_system.update_after_action(action_response.get("chosen_action", ""))
    _print_json("⚡ Action Response", action_response)

    # Apply action effects to needs via keyword matching (shared with the headless runner)
    action_executor = create_maslow_action_executor(person.maslow_needs)
    matched_action = match_action_key(chosen)
    if matched_action:
        effect_result = action_executor(matched_action)
        print(f"  🎯 Action effect applied: {matched_action} → satisfied {effect_result.get('satisfied_needs', {})}")
    else:
        print(f"  ⚠️  No need-satisfaction mapping for action: {chosen}")

    # Track social interactions from simulated actions
    _SOCIAL_ACTION_KEYS = {"socialize", "make_friends", "seek_love", "join_community", "build_relationships"}
    if matched_action in _SOCIAL_ACTION_KEYS and getattr(person, "social_interaction_tracker", None) is not None:
        dominant = person.emotion_system.get_dominant_emotions(1)
        tone = dominant[0]["name"].lower() if dominant else "neutral"
        # Map emotion names to simpler tone labels
        _tone_map = {"joy": "warm", "sadness": "melancholic", "anger": "tense",
                      "fear": "tense", "trust": "warm", "anticipation": "warm"}
        tone = _tone_map.get(tone, "neutral")
        person.social_interaction_tracker.record_social_action(
            action_description=chosen,
            emotional_tone=tone,
        )
        print(f"  👥 Social interaction recorded: {chosen} (tone: {tone})")


    # Detect if the action moves Jenbina to a new location
    new_location = _detect_location_from_action(chosen)
    if new_location:
        old_location = st.session_state.get("jenbina_location", "Jenbina's House")
        if new_location != old_location:
            st.session_state["jenbina_location"] = new_location
            print(f"  📍 Location changed: {old_location} → {new_location}")
            record_move(event_log, old_location, new_location)

    # ==================================================================
    # Stage 4 — Checks & Analysis  (compute only, render in debug)
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  🛡️  Stage 4: Checks & Analysis")
    print(f"{'─'*40}")
    rail.stage("checking…")
    asimov_chain = create_asimov_check_system(llm_json_mode)
    action_situation = f"Action taken: {action_response.get('chosen_action', 'unknown')}. Reasoning: {action_response.get('reasoning', '')}"

    # ── Parallel: asimov safety check + emotion analysis ─────────
    print(f"  🚀 [4] Running safety check + emotion analysis in parallel...")
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

    print(f"  ✅ Safety check complete")
    _print_json("⚖️  Asimov Response", asimov_response)

    if emotion_adjustments:
        person.emotion_system.apply_adjustments(emotion_adjustments)
        record_mood(event_log, emotions_before, person.get_emotions_snapshot(), "action")
        print(f"  ✅ Emotions: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
        _print_json("💭 Emotion Adjustments", emotion_adjustments)
    else:
        print(f"  ✅ No significant emotional changes")

    # ── Sequential: state analysis (depends on asimov_response) ──
    print(f"  🔍 [4b] Analyzing state changes...")
    state_response = create_state_analysis_system(
        llm_json_mode,
        action_decision=action_response,
        compliance_check=asimov_response
    )
    print(f"  ✅ State analysis complete")
    _print_json("🔍 State Analysis", state_response)

    # ==================================================================
    # Post-processing: needs update, experience recording, goals, plans
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  📝 Stage 5: Learning & Updates")
    print(f"{'─'*40}")
    rail.stage("learning…")
    print(f"  🔄 Updating needs & decaying emotions...")
    person.update_all_needs()

    needs_after = person.get_needs_snapshot()
    emotions_after = person.get_emotions_snapshot()
    satisfaction_after = person.maslow_needs.get_overall_satisfaction()
    sat_delta = satisfaction_after - satisfaction_before
    chosen_action = action_response.get("chosen_action", "unknown") if isinstance(action_response, dict) else str(action_response)
    reasoning = action_response.get("reasoning", "") if isinstance(action_response, dict) else ""

    rail.refresh(person)
    action_event = record_action(event_log, action_response, satisfaction_before, satisfaction_after, world_summary)
    rail.live_row(event_html(
        ACTION,
        action_event.title,
        meta=_now_hhmm(),
        badge=delta_badge_html(satisfaction_before, satisfaction_after),
        icon=action_icon(str(chosen_action)),
        details=("why?", action_details_text(reasoning, action_event.detail.get("lessons"))) or None,
    ))
    world_ctx = {
        "location": world_summary.get("location", {}).get("name", "unknown"),
        "time_of_day": world_summary.get("time", {}).get("time_of_day", "unknown"),
        "weather": world_summary.get("weather", {}).get("description", "unknown"),
    }

    learning_messages = []
    goal_messages = []
    plan_messages = []
    lesson_stats = {}
    experience = None
    goals_before = snapshot_goals(person.goal_system)

    if person.learning_system is not None:
        print(f"  📓 Recording experience...")
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

        delta_icon = "📈" if sat_delta >= 0 else "📉"
        learning_messages.append(f"{delta_icon} Satisfaction: {satisfaction_before:.1f}% → {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        stats = person.learning_system.get_learning_stats()
        learning_messages.append(f"📚 Active lessons: {stats['active_lessons']} | Total experiences: {stats['total_experiences']}")
        print(f"  {delta_icon} Satisfaction: {satisfaction_before:.1f}% → {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        print(f"  📚 Lessons: {stats['active_lessons']} active | {stats['total_experiences']} total experiences")

        if person.goal_system is not None:
            print(f"  🎯 Updating goal progress...")
            person.goal_system.set_experiences(person.learning_system.experiences)
            advanced_goals = person.goal_system.update_progress(experience)
            if advanced_goals:
                for g in advanced_goals:
                    goal_messages.append(f"🎯 {g.description} → {g.progress:.0%}")
                    print(f"  🎯 Goal advanced: {g.description} → {g.progress:.0%}")

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
            print(f"  📋 Evaluating plan progress...")
            step_before = person.planning_system.get_current_step()
            step_result = person.planning_system.evaluate_step(experience)
            if step_before:
                plan_before, step_obj = step_before
                record_plan_step(event_log, step_result, plan_before.goal_description, step_obj.description)
                if plan_before.status == "completed":
                    record_plan_finished(event_log, plan_before)
                    credit_completed_plan(plan_before, person.goal_system)
                    plan_messages.append(f"📋 Plan completed: {plan_before.goal_description}")
            if step_result == "step_completed":
                plan_messages.append("📋 Plan step completed!")
                current = person.planning_system.get_current_step()
                if current:
                    _, next_step = current
                    plan_messages.append(f"Next step: {next_step.description}")
            elif step_result == "step_overridden":
                plan_messages.append("📋 Plan step overridden by urgent needs.")

            replan_result = person.planning_system.check_for_replan(
                needs=needs_after, world_context=world_ctx,
            )
            if replan_result is not None:
                record_replan(event_log, replan_result)
                plan_messages.append(f"📋 Replanned: {replan_result.goal_description}")
                plan_messages.append(f"New first step: {replan_result.steps[0].description}")

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

    # Keep identity updates independent of learning-system availability
    # Goal events once, after plans had their say (finishing a plan advances its goal)
    record_goal_changes(event_log, goals_before, snapshot_goals(person.goal_system))

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

    # Final avatar update — reflect post-action emotional state
    final_image = get_jenbina_image_for_emotion(person)
    rail.portrait(final_image, caption=f"{person.name}")


    # ==================================================================
    # Store debug data in session state for the Debug Info page
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
        "curiosity_stats": person.curiosity_system.get_stats() if getattr(person, "curiosity_system", None) else None,
        "social_interaction_stats": (
            person.social_interaction_tracker.get_stats() if getattr(person, "social_interaction_tracker", None) else None
        ),
    }
    if "debug_iterations" not in st.session_state:
        st.session_state.debug_iterations = []
    st.session_state.debug_iterations.append(debug_entry)

    # Check if Jenbina wants to say something proactively
    try:
        llm = st.session_state.get("_proactive_llm")
        if llm is None:
            from core.connect import get_llm
            llm = get_llm(provider="openai", temperature=1)
            st.session_state._proactive_llm = llm
        send_proactive_message(person, llm)
    except Exception as e:
        print(f"  Proactive message check failed: {e}")

    iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
    print(f"{'='*60}")
    print(f"  ✅ ITERATION {iter_num} COMPLETE — {iteration_duration:.2f}s")
    print(f"{'='*60}")
    rail.stage(f"completed in {iteration_duration:.0f}s")

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


def run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations, delay_seconds,
                        rail=None, event_log=None):
    """Run ``iterations`` iterations back to back, ``delay_seconds`` apart.

    Progress shows in the rail's stage pill. Each iteration's record is
    appended to ``st.session_state.simulation_history`` right away so the next
    iteration sees it among its recent actions.
    """
    from core.ui.rail import NullRail  # local import: rail.py imports this module's renderers
    rail = rail if rail is not None else NullRail()
    event_log = event_log if event_log is not None else get_event_log()

    results = []
    for iteration in range(iterations):
        if iterations > 1:
            rail.stage(f"iteration {iteration + 1} of {iterations}")
        result = run_single_iteration(
            person, llm_json_mode, meta_cognitive_system, iteration, rail=rail, event_log=event_log
        )
        iteration_record = {
            "iteration": iteration + 1,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": result["iteration_duration"],
            "action_decision": result["action_decision"],
            "needs_state": result["person_dict"]["maslow_needs"],
            "emotions_state": result["person_dict"].get("emotions", {}),
            "world_summary": result["world_summary"],
            "satisfaction_delta": result["satisfaction_delta"],
        }
        results.append(iteration_record)
        if "simulation_history" not in st.session_state:
            st.session_state.simulation_history = []
        st.session_state.simulation_history.append(iteration_record)
        # What the chat reads afterwards: the latest world, decision, needs and state analysis
        st.session_state.world_description = result["world_description"]
        st.session_state.action_decision = result["action_decision"]
        st.session_state.state_response = result["state_response"]
        st.session_state.needs_response = iteration_record["needs_state"]

        if iteration < iterations - 1 and delay_seconds:
            rail.stage(f"waiting {delay_seconds}s…")
            time.sleep(delay_seconds)
    return results


