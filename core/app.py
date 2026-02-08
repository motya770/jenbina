"""
Jenbina - AGI Simulation Streamlit App

Main entry point for the Jenbina web interface.
"""
import streamlit as st
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# CONFIGURATION
# ============================================================================

# Environment configuration (Ollama disabled - using OpenAI)
# os.environ['OLLAMA_HOST'] = 'http://localhost:11434'  # Disabled - not using Ollama
os.environ['LANGSMITH_TRACING'] = 'true'
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY'] = "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"
os.environ['LANGSMITH_PROJECT'] = "jenbina"

# ============================================================================
# IMPORTS
# ============================================================================

from core.connect import get_llm, get_json_llm
from core.person.person import Person
from core.cognition.meta_cognition import MetaCognitiveSystem
from core.memory.conversation_memory import ChromaMemoryManager
from core.environment.environment_simulator import EnvironmentSimulator

# UI Components
from core.ui.sidebar import render_full_sidebar
from core.ui.simulation import (
    render_simulation_controls,
    run_simulation_loop,
    display_simulation_summary
)
from core.ui.chat import render_chat_interface

# ============================================================================
# INITIALIZATION
# ============================================================================

def init_llm():
    """Initialize LLM instances"""
    # Options: "openai" (GPT-4o-mini), "openai-advanced" (GPT-4o), "ollama" (local)
    llm = get_llm(provider="openai", temperature=1)
    llm_json_mode = get_json_llm(provider="openai", temperature=1)
    return llm, llm_json_mode


def init_session_state():
    """Initialize all session state variables"""
    # Person
    if 'person' not in st.session_state:
        person = Person()
        person.update_all_needs()
        # Initialize learning system with LLM
        _, llm_json_mode = init_llm()
        person.init_learning_system(llm_json_mode)
        person.init_goal_system(llm_json_mode)
        st.session_state.person = person
        st.session_state.action_history = []
        print(person)
    
    # Ensure learning system is initialized (for existing sessions)
    if st.session_state.person.learning_system is None:
        _, llm_json_mode = init_llm()
        st.session_state.person.init_learning_system(llm_json_mode)

    # Ensure goal system is initialized (for existing sessions)
    if st.session_state.person.goal_system is None:
        _, llm_json_mode = init_llm()
        st.session_state.person.init_goal_system(llm_json_mode)
    
    # Meta-cognitive system
    if 'meta_cognitive_system' not in st.session_state:
        _, llm_json_mode = init_llm()
        st.session_state.meta_cognitive_system = MetaCognitiveSystem(llm_json_mode)
    
    # Memory manager
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = ChromaMemoryManager()
    
    # Environment simulator
    if 'environment_simulator' not in st.session_state:
        st.session_state.environment_simulator = EnvironmentSimulator("Palo Alto, CA")
    
    # Simulation state
    if 'simulation_completed' not in st.session_state:
        st.session_state.simulation_completed = False
        st.session_state.needs_response = None
        st.session_state.world_description = None
        st.session_state.action_decision = None
        st.session_state.state_response = None
        st.session_state.simulation_history = []
        st.session_state.is_running = False


def update_session_state_from_results(results):
    """Update session state with simulation results"""
    if results:
        last_result = results[-1]
        st.session_state.simulation_history.extend(results)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""
    # Initialize session state
    init_session_state()
    
    # Initialize LLM
    llm, llm_json_mode = init_llm()
    
    # Get references from session state
    person = st.session_state.person
    meta_cognitive_system = st.session_state.meta_cognitive_system
    memory_manager = st.session_state.memory_manager
    environment_simulator = st.session_state.environment_simulator
    
    # ========================================================================
    # PAGE LAYOUT
    # ========================================================================
    
    st.title("Jenbina:")
    
    # Render sidebar and get debug mode setting
    debug_mode = render_full_sidebar(environment_simulator, memory_manager, debug_mode=True)
    
    # Create main layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("System Stages and Responses")
        
        # --------------------------------------------------------------------
        # SIMULATION CONTROLS
        # --------------------------------------------------------------------
        controls = render_simulation_controls()
        
        if controls["run_loop"] or controls["single_run"]:
            iterations = controls["num_iterations"] if controls["run_loop"] else 1
            
            # Run simulation
            results = run_simulation_loop(
                person=person,
                llm_json_mode=llm_json_mode,
                meta_cognitive_system=meta_cognitive_system,
                iterations=iterations,
                delay_seconds=controls["delay_seconds"]
            )
            
            # Update session state
            st.session_state.simulation_history.extend(results)
            
            if results:
                # Store last result in session state for chat context
                last = results[-1]
                st.session_state.action_decision = last.get("action_decision")
                st.session_state.needs_response = last.get("needs_state")
            
            # Display summary
            display_simulation_summary(st.session_state.simulation_history, iterations, person=person)
            
            # Mark as completed
            st.session_state.simulation_completed = True
        
        # --------------------------------------------------------------------
        # CHAT INTERFACE
        # --------------------------------------------------------------------
        render_chat_interface(
            person=person,
            llm=llm,
            memory_manager=memory_manager,
            debug_mode=debug_mode
        )


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
else:
    # When imported by Streamlit, run main
    main()
