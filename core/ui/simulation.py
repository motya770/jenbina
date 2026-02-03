"""Simulation UI components and runner for Jenbina app"""
import streamlit as st
from datetime import datetime
import time

from core.needs.maslow_needs import create_basic_needs_chain
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import create_world_description_system, create_comprehensive_world_state, get_world_state_summary
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain


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
        }
    }


def display_person_state(person):
    """Display current person state"""
    st.write("### Current Jenbina State:")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")


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


def run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration):
    """Run a single simulation iteration and return results"""
    iteration_start_time = datetime.now()
    
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
    
    # Update person's needs
    person.update_all_needs()
    
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
        "iteration_duration": iteration_duration
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


def display_simulation_summary(simulation_history, iterations):
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
                else:
                    chosen = str(action)[:100]
                st.write(f"- Iteration {record['iteration']}: {chosen}")
            
            # Show needs evolution
            st.write("**Needs Evolution:**")
            for record in simulation_history[-iterations:]:
                needs = record.get("needs_state", {})
                overall = needs.get("overall_satisfaction", 0)
                st.write(f"- Iteration {record['iteration']}: Overall Satisfaction {overall:.1f}%")


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
