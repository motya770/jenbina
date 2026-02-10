"""Shared initialization logic for all Jenbina pages."""
import streamlit as st
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ['LANGSMITH_TRACING'] = 'true'
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY'] = "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"
os.environ['LANGSMITH_PROJECT'] = "jenbina"

from core.connect import get_llm, get_json_llm
from core.person.person import Person
from core.cognition.meta_cognition import MetaCognitiveSystem
from core.memory.conversation_memory import ChromaMemoryManager
from core.environment.environment_simulator import EnvironmentSimulator
from core.auth.user_db import UserDatabase
from core.ui.auth_page import render_auth_page, render_user_header


def init_llm():
    """Initialize LLM instances."""
    llm = get_llm(provider="openai", temperature=1)
    llm_json_mode = get_json_llm(provider="openai", temperature=1)
    return llm, llm_json_mode


def _load_or_create_person(user_db: UserDatabase, user_id: int) -> Person:
    """Load a user's Person state from SQLite, or create a fresh one."""
    _, llm_json_mode = init_llm()
    saved_json = user_db.load_person_state(user_id)
    if saved_json:
        person = Person.deserialize(saved_json, llm_json_mode)
    else:
        person = Person()
        person.update_all_needs()
    if person.learning_system is None:
        person.init_learning_system(llm_json_mode)
    if person.goal_system is None:
        person.init_goal_system(llm_json_mode)
    if person.planning_system is None:
        person.init_planning_system(llm_json_mode)
    return person


def save_person_state():
    """Persist the current Person state to SQLite for the logged-in user."""
    user = st.session_state.get("current_user")
    person = st.session_state.get("person")
    if user and person:
        user_db = st.session_state.get("user_db")
        if user_db is None:
            user_db = UserDatabase()
            st.session_state.user_db = user_db
        user_db.save_person_state(user["id"], person.serialize())


def init_session_state():
    """Initialize all session state variables."""
    if 'person' not in st.session_state:
        user = st.session_state.get("current_user")
        if user:
            user_db = st.session_state.get("user_db", UserDatabase())
            st.session_state.user_db = user_db
            person = _load_or_create_person(user_db, user["id"])
        else:
            person = Person()
            person.update_all_needs()
            _, llm_json_mode = init_llm()
            person.init_learning_system(llm_json_mode)
            person.init_goal_system(llm_json_mode)
            person.init_planning_system(llm_json_mode)
        st.session_state.person = person
        st.session_state.action_history = []
        print(person)

    # Ensure systems are initialized for existing sessions
    if st.session_state.person.learning_system is None:
        _, llm_json_mode = init_llm()
        st.session_state.person.init_learning_system(llm_json_mode)
    if st.session_state.person.planning_system is None:
        _, llm_json_mode = init_llm()
        st.session_state.person.init_planning_system(llm_json_mode)
    if st.session_state.person.goal_system is None:
        _, llm_json_mode = init_llm()
        st.session_state.person.init_goal_system(llm_json_mode)

    if 'meta_cognitive_system' not in st.session_state:
        _, llm_json_mode = init_llm()
        st.session_state.meta_cognitive_system = MetaCognitiveSystem(llm_json_mode)
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = ChromaMemoryManager()
    if 'environment_simulator' not in st.session_state:
        st.session_state.environment_simulator = EnvironmentSimulator("Palo Alto, CA")

    if 'simulation_completed' not in st.session_state:
        st.session_state.simulation_completed = False
        st.session_state.needs_response = None
        st.session_state.world_description = None
        st.session_state.action_decision = None
        st.session_state.state_response = None
        st.session_state.simulation_history = []
        st.session_state.is_running = False


def require_auth():
    """Auth gate + session init. Returns False if not logged in."""
    if not render_auth_page():
        return False
    user = st.session_state.current_user
    render_user_header(user)
    init_session_state()
    return True
