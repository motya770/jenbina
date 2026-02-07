"""Simulation UI components and runner for Jenbina app"""
import streamlit as st
from datetime import datetime
import time
import json

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
    with st.expander("All Emotions", expanded=False):
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
    """Display meta-cognitive insights with checkbox toggle"""
    show_meta = st.checkbox(
        f"🧠 Show Meta-Cognitive Insights", 
        value=False, 
        key=f"meta_insights_{iteration}"
    )
    if show_meta:
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
    show_learning = st.checkbox(
        f"📚 Show Learning Stats",
        value=False,
        key=f"learning_stats_{iteration}"
    )
    if show_learning:
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


def run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration):
    """Run a single simulation iteration and return results"""
    iteration_start_time = datetime.now()
    
    # ── SNAPSHOT BEFORE ─────────────────────────────────────────────────
    needs_before = person.get_needs_snapshot()
    emotions_before = person.get_emotions_snapshot()
    satisfaction_before = person.maslow_needs.get_overall_satisfaction()
    
    # Display person state
    display_person_state(person)
    
    # JSON representation
    person_dict = get_person_dict(person)
    st.write("**Person Object (JSON):**")
    st.json(person_dict)
    
    # Basic needs analysis
    st.write("**1. Basic Needs Analysis:**")
    needs_response = create_basic_needs_chain(llm_json_mode, person.maslow_needs)
    st.write(needs_response)
    
    # World state and description
    world = create_comprehensive_world_state(person_location="Jenbina's House")
    world_summary = get_world_state_summary(world)
    display_world_state(world_summary, world)
    
    # World description from LLM
    st.write("**2.1 World Description:**")
    world_chain = create_world_description_system(llm_json_mode)
    world_response = world_chain(person, world)
    st.write(world_response)
    
    # Show learned lessons (if any) before making a decision
    if person.learning_system is not None:
        lessons_text = person.learning_system.format_lessons_for_prompt(
            needs=needs_before,
            emotions=emotions_before
        )
        if lessons_text != "No lessons learned yet.":
            st.write("**2.5 Lessons Applied to Decision:**")
            st.info(lessons_text)
    
    # Enhanced action decision with meta-cognition
    st.write("**3. Action Decision (with Meta-Cognition):**")
    action_response = create_meta_cognitive_action_chain(
        llm=llm_json_mode,
        person=person,
        world_description=world_response,
        meta_cognitive_system=meta_cognitive_system,
        world_state=world
    )
    st.write(action_response)
    
    # Meta-cognitive insights
    display_meta_cognitive_insights(meta_cognitive_system, iteration)
    
    # Asimov compliance check
    st.write("**5. Asimov Compliance Check:**")
    asimov_chain = create_asimov_check_system(llm_json_mode)
    asimov_response = asimov_chain(action_response)
    st.write(asimov_response)
    
    # State analysis
    st.write("**4. State Analysis:**")
    state_response = create_state_analysis_system(
        llm_json_mode,
        action_decision=action_response,
        compliance_check=asimov_response
    )
    st.write(state_response)

    # Emotion analysis based on action outcome
    st.write("**6. Emotion Analysis:**")
    action_situation = f"Action taken: {action_response.get('chosen_action', 'unknown')}. Reasoning: {action_response.get('reasoning', '')}"
    emotion_adjustments = analyze_emotion_impact(
        llm=llm_json_mode,
        situation=action_situation,
        emotion_system=person.emotion_system,
        maslow_needs=person.maslow_needs,
    )
    if emotion_adjustments:
        person.emotion_system.apply_adjustments(emotion_adjustments)
        st.write("Emotion changes: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
    else:
        st.write("No significant emotional changes.")

    # Update person's needs (also decays emotions and lessons)
    person.update_all_needs()
    
    # ── SNAPSHOT AFTER ──────────────────────────────────────────────────
    needs_after = person.get_needs_snapshot()
    emotions_after = person.get_emotions_snapshot()
    satisfaction_after = person.maslow_needs.get_overall_satisfaction()
    
    # ── RECORD EXPERIENCE ───────────────────────────────────────────────
    if person.learning_system is not None:
        chosen_action = action_response.get("chosen_action", "unknown") if isinstance(action_response, dict) else str(action_response)
        reasoning = action_response.get("reasoning", "") if isinstance(action_response, dict) else ""
        
        world_ctx = {
            "location": world_summary.get("location", {}).get("name", "unknown"),
            "time_of_day": world_summary.get("time", {}).get("time_of_day", "unknown"),
            "weather": world_summary.get("weather", {}).get("description", "unknown"),
        }
        
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
        
        # Show experience delta
        st.write("**7. Learning - Experience Recorded:**")
        sat_delta = satisfaction_after - satisfaction_before
        delta_icon = "📈" if sat_delta >= 0 else "📉"
        st.write(f"{delta_icon} Satisfaction: {satisfaction_before:.1f}% → {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        
        # Show lesson count
        stats = person.learning_system.get_learning_stats()
        st.write(f"📚 Active lessons: {stats['active_lessons']} | Total experiences: {stats['total_experiences']}")
    
    # Show learning stats toggle
    display_learning_stats(person, iteration)
    
    # Calculate duration
    iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
    st.write(f"✅ Iteration {iteration + 1} completed in {iteration_duration:.2f}s")
    
    # Return results for session state
    return {
        "needs_response": needs_response,
        "world_description": world_response,
        "action_decision": action_response,
        "state_response": state_response,
        "person_dict": person_dict,
        "world_summary": world_summary,
        "iteration_duration": iteration_duration,
        "satisfaction_delta": satisfaction_after - satisfaction_before,
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
