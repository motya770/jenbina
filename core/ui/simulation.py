"""Simulation UI components and runner for Jenbina app"""
import streamlit as st
from contextlib import contextmanager
from datetime import datetime
import time
import json
from types import SimpleNamespace

from core.needs.maslow_needs import create_basic_needs_chain
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import create_world_description_system, create_comprehensive_world_state, get_world_state_summary
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
from core.emotions.emotion_analysis_chain import analyze_emotion_impact


def get_person_dict(person):
    """Get person state as dictionary for display"""
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


def display_person_state(person):
    """Display current person state"""
    st.write("### Current Jenbina State:")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")

    # Display emotional state
    dominant = person.emotion_system.get_dominant_emotions(3)
    st.write("**Emotional State:**")
    for emo in dominant:
        st.write(f"- {emo['name'].capitalize()}: {emo['intensity']}")
    all_emotions = person.emotion_system.get_emotional_state_summary()["emotions"]
    with st.container(border=True):
        st.caption("All Emotions")
        for name, val in all_emotions.items():
            st.write(f"- {name}: {val}")


def display_world_state(world_summary, world):
    """Display world state information"""
    st.write("**2. World State:**")
    st.write(f"Location: {world_summary['location']['name']}")
    st.write(f"Time of Day: {world_summary['time']['time_of_day']}")
    st.write(f"Weather: {world_summary['weather']['description']}")
    st.write(f"Temperature: {world_summary['weather']['temperature']:.1f}°C")
    st.write(f"Humidity: {world_summary['weather']['humidity']:.1f}%")
    st.write(f"Nearby Locations: {world_summary['environment']['nearby_locations_count']}")
    st.write(f"Open Locations: {world_summary['environment']['open_locations_count']}")
    st.write(f"Current Events: {world_summary['environment']['current_events_count']}")
    
    if world.last_descriptions:
        st.write(f"Previous Descriptions: {len(world.last_descriptions)} items")
    
    st.write("**World State (JSON):**")
    st.json(world_summary)


def display_meta_cognitive_insights(meta_cognitive_system, iteration):
    """Display meta-cognitive insights with expander toggle"""
    with st.container(border=True):
        st.caption("🧠 Meta-Cognitive Insights")
        meta_stats = meta_cognitive_system.get_meta_cognitive_stats()
        st.write(f"**Total Cognitive Processes:** {meta_stats['total_processes']}")
        st.write(f"**Total Insights:** {meta_stats['total_insights']}")
        
        st.write("**Cognitive Biases Detected:**")
        for bias, level in meta_stats['cognitive_biases'].items():
            if level > 0:
                st.write(f"- {bias}: {level:.2f}")
        
        if meta_stats['recent_insights']:
            st.write("**Recent Insights:**")
            for insight in meta_stats['recent_insights']:
                st.write(f"- **{insight['type']}**: {insight['description']}")


def display_learning_stats(person, iteration):
    """Display learning system stats"""
    if person.learning_system is None:
        return
    
    stats = person.learning_system.get_learning_stats()
    with st.container(border=True):
        st.caption("📚 Learning Stats")
        st.write(f"**Total Experiences:** {stats['total_experiences']}")
        st.write(f"**Active Lessons:** {stats['active_lessons']} / {stats['total_lessons']}")
        
        if stats['lessons']:
            st.write("**Learned Lessons:**")
            for lesson in stats['lessons']:
                confidence_bar = "█" * int(lesson['confidence'] * 10) + "░" * (10 - int(lesson['confidence'] * 10))
                st.write(
                    f"- [{lesson['category']}] {lesson['description']}\n"
                    f"  Confidence: {confidence_bar} {lesson['confidence']:.0%} | "
                    f"Confirmed: {lesson['times_confirmed']}x | "
                    f"Action: {lesson['recommended_action']}"
                )
        else:
            st.write("*No lessons learned yet. Jenbina needs more experiences.*")


def display_goal_stats(person, iteration):
    """Display goal system stats"""
    if person.goal_system is None:
        return

    stats = person.goal_system.get_goal_stats()
    with st.container(border=True):
        st.caption("🎯 Goal Stats")
        st.write(f"**Active Goals:** {stats['active_goals']} | **Completed:** {stats['completed_goals']} | **Abandoned:** {stats['abandoned_goals']}")

        if stats['goals']:
            st.write("**Active Goals:**")
            for goal in stats['goals']:
                progress_bar = "█" * int(goal['progress'] * 10) + "░" * (10 - int(goal['progress'] * 10))
                st.write(
                    f"- [{goal['horizon']}] {goal['description']}\n"
                    f"  Progress: {progress_bar} {goal['progress']:.0%} | "
                    f"Confidence: {goal['confidence']:.0%} | "
                    f"Advanced: {goal['times_advanced']}x"
                )
        else:
            st.write("*No active goals. Jenbina needs more experiences to form goals.*")

        if stats['completed']:
            st.write("**Recently Completed:**")
            for goal in stats['completed']:
                st.write(f"- ✅ {goal['description']}")


def display_working_memory_stats(person, iteration):
    """Display working memory stats"""
    stats = person.working_memory.get_stats()
    with st.container(border=True):
        st.caption("🧠 Working Memory")
        st.write(f"**Focus:** {stats['focus']:.0f}% | **Capacity:** {stats['buffer_size']}/{stats['capacity']} | **Context Switches:** {stats['context_switches']}")
        if stats['items']:
            for item in stats['items']:
                bar_len = int(item['salience'] * 10)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                st.write(f"- [{item['source']}] {item['content']} | {bar} {item['salience']:.2f}")
        else:
            st.write("*Mind is clear.*")


def display_identity_stats(person, iteration):
    """Display self-narrative and identity stats."""
    if getattr(person, "self_narrative", None) is None:
        return

    stats = person.self_narrative.get_stats()
    with st.container(border=True):
        st.caption("🪞 Identity & Narrative")
        st.write(f"**Coherence:** {stats['identity_coherence']:.2f} | **Crisis:** {stats['identity_crisis_level']:.2f}")
        st.write("**Self Concept:**")
        for line in stats.get("self_concept", [])[:3]:
            st.write(f"- {line}")
        st.write("**Life Story:**")
        st.write(stats.get("life_story", ""))
        values = stats.get("values", {})
        if values:
            top = sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:5]
            st.write("**Top Values:**")
            for name, score in top:
                st.write(f"- {name}: {score:.2f}")


def display_curiosity_stats(person, iteration):
    """Display curiosity and exploration stats."""
    if getattr(person, "curiosity_system", None) is None:
        return

    stats = person.curiosity_system.get_stats()
    with st.container(border=True):
        st.caption("🔎 Curiosity & Exploration")
        st.write(
            f"**Curiosity:** {stats['curiosity_level']:.2f} | "
            f"**Boredom:** {stats['boredom_level']:.2f} | "
            f"**Novelty:** {stats['last_novelty_score']:.2f} | "
            f"**Explore?:** {'yes' if stats['should_explore'] else 'no'}"
        )
        if stats.get("open_questions"):
            st.write("**Open Questions:**")
            for q in stats["open_questions"][:3]:
                st.write(f"- {q}")
        if stats.get("suggested_explorations"):
            st.write("**Exploration Candidates:**")
            for a in stats["suggested_explorations"][:5]:
                st.write(f"- {a}")


def display_planning_stats(person, iteration):
    """Display planning system stats"""
    if person.planning_system is None:
        return

    stats = person.planning_system.get_planning_stats()
    with st.container(border=True):
        st.caption("📋 Planning Stats")
        st.write(f"**Active Plans:** {stats['active_plans']} | **Completed:** {stats['completed_plans']} | **Failed:** {stats['failed_plans']}")

        if stats['plans']:
            st.write("**Active Plans:**")
            for plan_data in stats['plans']:
                steps = plan_data.get('steps', [])
                current_idx = plan_data.get('current_step_index', 0)
                total = len(steps)
                completed_count = len([s for s in steps if s['status'] == 'completed'])
                st.write(
                    f"- **{plan_data['goal_description']}**\n"
                    f"  Step {current_idx + 1} of {total} | "
                    f"Completed: {completed_count}/{total} | "
                    f"Replanned: {plan_data.get('times_replanned', 0)}x"
                )
                for i, step in enumerate(steps):
                    icon = "✅" if step['status'] == 'completed' else "▶️" if step['status'] == 'active' else "⏳" if step['status'] == 'pending' else "❌"
                    st.write(f"  {icon} {step['description']} ({step['actual_cycles']}/{step['estimated_cycles']} cycles)")
        else:
            st.write("*No active plans.*")


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


@contextmanager
def _card(title: str):
    """Render a bordered card with a bold title."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        yield


def run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration):
    """Run a single simulation iteration with live-updating card grid.

    Each card computes its data then renders immediately so the UI
    updates progressively as each LLM call completes.
    """
    iteration_start_time = datetime.now()
    iter_num = iteration + 1
    print(f"\n{'='*60}")
    print(f"  🔄 ITERATION {iter_num}")
    print(f"{'='*60}")

    # ── SNAPSHOT BEFORE ─────────────────────────────────────────────────
    needs_before = person.get_needs_snapshot()
    emotions_before = person.get_emotions_snapshot()
    satisfaction_before = person.maslow_needs.get_overall_satisfaction()
    print(f"\n📸 Snapshot | Satisfaction: {satisfaction_before:.1f}%")

    # ==================================================================
    # Environment row — fast local data, render immediately
    # ==================================================================
    print(f"\n{'─'*40}")
    print(f"  🌍 Stage 1: Environment")
    print(f"{'─'*40}")
    person_dict = get_person_dict(person)
    world = create_comprehensive_world_state(person_location="Jenbina's House")
    world_summary = get_world_state_summary(world)
    print(f"  👤 Person: {person.name} | Satisfaction: {satisfaction_before:.1f}%")
    print(f"  📍 Location: {world_summary['location']['name']}")
    print(f"  🕐 Time: {world_summary['time']['time_of_day']}")
    print(f"  🌤️  Weather: {world_summary['weather']['description']} ({world_summary['weather']['temperature']:.0f}°C)")

    env_left, env_right = st.columns(2)
    with env_left:
        with _card("Person State"):
            display_person_state(person)
            with st.container(border=True):
                st.caption("Person JSON")
                st.json(person_dict)
    with env_right:
        with _card("World State"):
            display_world_state(world_summary, world)

    # ==================================================================
    # Row 1 — Perception & Context  (compute → display per card)
    # ==================================================================
    r1c1, r1c2, r1c3 = st.columns(3)

    # Card 1: Needs Analysis (LLM call → display)
    print(f"\n{'─'*40}")
    print(f"  🧠 Stage 2: Perception & Context")
    print(f"{'─'*40}")
    print(f"  📊 [2a] Analyzing basic needs...")
    needs_response = create_basic_needs_chain(llm_json_mode, person.maslow_needs)
    print(f"  ✅ Needs analysis complete")
    _print_json("📊 Needs Response", needs_response)
    with r1c1:
        with _card("Needs Analysis"):
            st.write(needs_response)

    # Card 2: Context — world description LLM + working memory update → display
    print(f"  🌐 [2b] Generating world description...")
    world_chain = create_world_description_system(llm_json_mode)
    world_response = world_chain(person, world)
    print(f"  ✅ World description complete")
    _print_json("🌐 World Description", world_response)

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

    print(f"  🧩 [2c] Updating working memory...")
    wm_text = person.working_memory.format_for_prompt()
    print(f"  ✅ Working memory updated")
    plan_text = person.planning_system.format_plan_for_prompt() if person.planning_system is not None else "No active plan."
    goals_text = person.goal_system.format_goals_for_prompt() if person.goal_system is not None else "No goals set yet."
    lessons_text = "No lessons learned yet."
    if person.learning_system is not None:
        lessons_text = person.learning_system.format_lessons_for_prompt(
            needs=needs_before, emotions=emotions_before
        )

    curiosity_text = "Curiosity is low; prioritize practical actions."
    if getattr(person, "curiosity_system", None) is not None:
        available_actions = []
        try:
            world_data = json.loads(world_response) if isinstance(world_response, str) else {}
            available_actions = world_data.get("list_of_actions", []) if isinstance(world_data, dict) else []
        except Exception:
            available_actions = []

        recent_actions = []
        for record in st.session_state.get("simulation_history", [])[-6:]:
            action = (record.get("action_decision", {}) or {}).get("chosen_action")
            if action:
                recent_actions.append(action)

        person.curiosity_system.observe_cycle(
            needs=needs_before,
            world_context=world_ctx_wm,
            available_actions=available_actions,
            recent_actions=recent_actions,
        )
        curiosity_text = person.curiosity_system.format_for_prompt()

    inner_voice_text = "No inner thoughts at the moment."
    if person.inner_monologue is not None:
        print(f"  🧠 [2d] Generating inner monologue...")
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
        world_context_str = (
            f"Location: {world_summary.get('location', {}).get('name', 'Unknown')}, "
            f"Time: {world_summary.get('time', {}).get('time_of_day', 'unknown')}, "
            f"Weather: {world_summary.get('weather', {}).get('description', 'unknown')}"
        )

        last_action = "Nothing in particular."
        if st.session_state.get("simulation_history"):
            prev = st.session_state["simulation_history"][-1].get("action_decision", {})
            if isinstance(prev, dict):
                last_action = prev.get("chosen_action", last_action)

        person.inner_monologue.think(
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
        inner_voice_text = person.inner_monologue.format_for_prompt()
        print(f"  ✅ Inner monologue generated")

    with r1c2:
        with _card("Context"):
            if wm_text != "Mind is clear — no particular focus.":
                st.caption("Working Memory")
                st.info(wm_text)
            if plan_text != "No active plan.":
                st.caption("Current Plan Step")
                st.info(plan_text)
            if goals_text != "No goals set yet.":
                st.caption("Current Goals")
                st.info(goals_text)
            if lessons_text != "No lessons learned yet.":
                st.caption("Lessons Applied")
                st.info(lessons_text)
            if curiosity_text != "Curiosity is low; prioritize practical actions.":
                st.caption("Curiosity")
                st.info(curiosity_text)
            if inner_voice_text != "No inner thoughts at the moment.":
                st.caption("Inner Voice")
                st.info(inner_voice_text)

    # Card 3: Action Decision (LLM call → display)
    print(f"\n{'─'*40}")
    print(f"  ⚡ Stage 3: Action Decision")
    print(f"{'─'*40}")
    print(f"  🤔 Running meta-cognitive action chain...")
    action_response = create_meta_cognitive_action_chain(
        llm=llm_json_mode,
        person=person,
        world_description=world_response,
        meta_cognitive_system=meta_cognitive_system,
        world_state=world
    )
    chosen = action_response.get('chosen_action', '?') if isinstance(action_response, dict) else str(action_response)[:50]
    print(f"  ✅ Action chosen: {chosen}")
    if getattr(person, "curiosity_system", None) is not None and isinstance(action_response, dict):
        person.curiosity_system.update_after_action(action_response.get("chosen_action", ""))
    _print_json("⚡ Action Response", action_response)
    with r1c3:
        with _card("Action Decision"):
            st.write(action_response)
            # Display chain-of-thought reasoning trace
            trace = action_response.get("reasoning_trace", []) if isinstance(action_response, dict) else []
            if trace:
                with st.container(border=True):
                    st.caption("Chain of Thought")
                    step_labels = {"assess": "Assess", "deliberate": "Deliberate", "decide": "Decide"}
                    for entry in trace:
                        if isinstance(entry, dict):
                            label = step_labels.get(entry.get("step", ""), entry.get("step", ""))
                            st.write(f"**{label}:**")
                            output = entry.get("output", entry)
                            st.json(output)
                        else:
                            st.write(str(entry))
            display_meta_cognitive_insights(meta_cognitive_system, iteration)

    # ==================================================================
    # Row 2 — Checks & Analysis  (compute → display per card)
    # ==================================================================
    r2c1, r2c2, r2c3 = st.columns(3)

    # Card 1: Safety Check (LLM call → display)
    print(f"\n{'─'*40}")
    print(f"  🛡️  Stage 4: Checks & Analysis")
    print(f"{'─'*40}")
    print(f"  ⚖️  [4a] Running Asimov safety check...")
    asimov_chain = create_asimov_check_system(llm_json_mode)
    asimov_response = asimov_chain(action_response)
    print(f"  ✅ Safety check complete")
    _print_json("⚖️  Asimov Response", asimov_response)
    with r2c1:
        with _card("Safety Check"):
            st.write(asimov_response)

    # Card 2: State Analysis (LLM call → display)
    print(f"  🔍 [4b] Analyzing state changes...")
    state_response = create_state_analysis_system(
        llm_json_mode,
        action_decision=action_response,
        compliance_check=asimov_response
    )
    print(f"  ✅ State analysis complete")
    _print_json("🔍 State Analysis", state_response)
    with r2c2:
        with _card("State Analysis"):
            st.write(state_response)

    # Card 3: Emotions (LLM call → display)
    print(f"  💭 [4c] Analyzing emotional impact...")
    action_situation = f"Action taken: {action_response.get('chosen_action', 'unknown')}. Reasoning: {action_response.get('reasoning', '')}"
    emotion_adjustments = analyze_emotion_impact(
        llm=llm_json_mode,
        situation=action_situation,
        emotion_system=person.emotion_system,
        maslow_needs=person.maslow_needs,
    )
    if emotion_adjustments:
        person.emotion_system.apply_adjustments(emotion_adjustments)
        print(f"  ✅ Emotions: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
        _print_json("💭 Emotion Adjustments", emotion_adjustments)
    else:
        print(f"  ✅ No significant emotional changes")
    with r2c3:
        with _card("Emotions"):
            if emotion_adjustments:
                st.write("Changes: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
            else:
                st.write("No significant emotional changes.")

    # ==================================================================
    # Post-processing: needs update, experience recording, goals, plans
    # ==================================================================
    print(f"\n{'─'*40}")
    print(f"  📝 Stage 5: Learning & Updates")
    print(f"{'─'*40}")
    print(f"  🔄 Updating needs & decaying emotions...")
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

    learning_messages = []
    goal_messages = []
    plan_messages = []
    lesson_stats = {}
    experience = None

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
            step_result = person.planning_system.evaluate_step(experience)
            if step_result == "step_completed":
                plan_messages.append("📋 Plan step completed!")
                current = person.planning_system.get_current_step()
                if current:
                    _, next_step = current
                    plan_messages.append(f"Next step: {next_step.description}")
                else:
                    for p in person.planning_system.plans:
                        if p.status == "completed" and p.goal_id is not None:
                            plan_messages.append(f"📋 Plan completed: {p.goal_description}")
                            if person.goal_system is not None:
                                for g in person.goal_system.goals:
                                    if g.description == p.goal_description and g.is_active():
                                        g.advance(0.3)
                                        break
            elif step_result == "step_overridden":
                plan_messages.append("📋 Plan step overridden by urgent needs.")

            replan_result = person.planning_system.check_for_replan(
                needs=needs_after, world_context=world_ctx,
            )
            if replan_result is not None:
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
    # Row 3 — Learning (display after post-processing completes)
    # ==================================================================
    with _card("Learning"):
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            for msg in learning_messages:
                st.write(msg)
            if not learning_messages:
                st.write("*No learning updates.*")
        with lc2:
            if goal_messages:
                st.caption("Goals Advanced")
                for msg in goal_messages:
                    st.write(msg)
        with lc3:
            if plan_messages:
                st.caption("Plan Updates")
                for msg in plan_messages:
                    st.write(msg)

    # --- Stats expanders (full width below grid) ---
    display_learning_stats(person, iteration)
    display_goal_stats(person, iteration)
    display_planning_stats(person, iteration)
    display_working_memory_stats(person, iteration)
    display_identity_stats(person, iteration)
    display_curiosity_stats(person, iteration)

    iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
    print(f"\n{'='*60}")
    print(f"  ✅ ITERATION {iter_num} COMPLETE — {iteration_duration:.2f}s")
    print(f"{'='*60}\n")
    st.success(f"Iteration {iter_num} completed in {iteration_duration:.2f}s")

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


def run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations, delay_seconds):
    """Run the simulation loop for specified iterations"""
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Container for all iterations
    iterations_container = st.container()
    
    results = []
    
    for iteration in range(iterations):
        # Update progress
        progress = (iteration + 1) / iterations
        progress_bar.progress(progress)
        status_text.text(f"🔄 Running iteration {iteration + 1} of {iterations}...")
        
        with iterations_container:
            # Create expander for each iteration
            with st.expander(f"📍 Iteration {iteration + 1} of {iterations}", expanded=(iteration == iterations - 1)):
                result = run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration)
                
                # Store iteration record
                iteration_record = {
                    "iteration": iteration + 1,
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": result["iteration_duration"],
                    "action_decision": result["action_decision"],
                    "needs_state": result["person_dict"]["maslow_needs"],
                    "emotions_state": result["person_dict"].get("emotions", {}),
                    "world_summary": result["world_summary"]
                }
                results.append(iteration_record)
        
        # Wait before next iteration (except for the last one)
        if iteration < iterations - 1:
            status_text.text(f"⏳ Waiting {delay_seconds} seconds before next iteration...")
            time.sleep(delay_seconds)
    
    # Simulation completed
    progress_bar.progress(1.0)
    status_text.text(f"✅ Simulation completed! Ran {iterations} iteration(s).")
    
    return results


def display_simulation_summary(simulation_history, iterations, person=None):
    """Display summary of simulation history"""
    st.success(f"🎉 Completed {iterations} simulation cycles!")
    
    if len(simulation_history) > 0:
        with st.expander("📊 Simulation History Summary", expanded=True):
            st.write(f"**Total Iterations:** {len(simulation_history)}")
            
            # Show action decisions across iterations
            st.write("**Action Decisions:**")
            for record in simulation_history[-iterations:]:
                action = record.get("action_decision", {})
                if isinstance(action, dict):
                    chosen = action.get("chosen_action", "Unknown")
                    lessons_applied = action.get("lessons_applied", "")
                else:
                    chosen = str(action)[:100]
                    lessons_applied = ""
                
                delta = record.get("satisfaction_delta", 0)
                delta_icon = "📈" if delta >= 0 else "📉"
                st.write(f"- Iteration {record['iteration']}: {chosen} {delta_icon} ({delta:+.1f}%)")
                if lessons_applied:
                    st.write(f"  *Lessons applied: {lessons_applied}*")
            
            # Show needs evolution
            st.write("**Needs Evolution:**")
            for record in simulation_history[-iterations:]:
                needs = record.get("needs_state", {})
                overall = needs.get("overall_satisfaction", 0)
                st.write(f"- Iteration {record['iteration']}: Overall Satisfaction {overall:.1f}%")
            
            # Show learning summary
            if person is not None and person.learning_system is not None:
                stats = person.learning_system.get_learning_stats()
                st.write("---")
                st.write(f"**📚 Learning Summary:**")
                st.write(f"- Total experiences recorded: {stats['total_experiences']}")
                st.write(f"- Active lessons: {stats['active_lessons']}")
                
                if stats['lessons']:
                    st.write("**Learned Lessons:**")
                    for lesson in stats['lessons']:
                        st.write(f"- **{lesson['description']}** (confidence: {lesson['confidence']:.0%}, confirmed {lesson['times_confirmed']}x)")

            if person is not None and person.goal_system is not None:
                goal_stats = person.goal_system.get_goal_stats()
                st.write(f"**🎯 Goal Summary:**")
                st.write(f"- Active goals: {goal_stats['active_goals']}")
                st.write(f"- Completed goals: {goal_stats['completed_goals']}")
                st.write(f"- Abandoned goals: {goal_stats['abandoned_goals']}")
                if goal_stats['goals']:
                    st.write("**Active Goals:**")
                    for goal in goal_stats['goals']:
                        st.write(f"- [{goal['horizon']}] **{goal['description']}** (progress: {goal['progress']:.0%}, confidence: {goal['confidence']:.0%})")

            if person is not None and person.planning_system is not None:
                plan_stats = person.planning_system.get_planning_stats()
                st.write(f"**📋 Planning Summary:**")
                st.write(f"- Active plans: {plan_stats['active_plans']}")
                st.write(f"- Completed plans: {plan_stats['completed_plans']}")
                st.write(f"- Failed plans: {plan_stats['failed_plans']}")
                if plan_stats['plans']:
                    st.write("**Active Plans:**")
                    for p in plan_stats['plans']:
                        steps = p.get('steps', [])
                        done = len([s for s in steps if s['status'] == 'completed'])
                        st.write(f"- **{p['goal_description']}** ({done}/{len(steps)} steps done, replanned {p.get('times_replanned', 0)}x)")


def render_simulation_controls():
    """Render simulation control UI and return settings"""
    st.write("### Simulation Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_iterations = st.number_input("Iterations", min_value=1, max_value=20, value=5, step=1)
    
    with col2:
        delay_seconds = st.number_input("Delay (seconds)", min_value=1, max_value=60, value=3, step=1)
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Align with other inputs
        run_loop = st.button("🔄 Run Simulation Loop", type="primary")
    
    single_run = st.button("▶️ Run Single Iteration")
    
    return {
        "num_iterations": num_iterations,
        "delay_seconds": delay_seconds,
        "run_loop": run_loop,
        "single_run": single_run
    }
