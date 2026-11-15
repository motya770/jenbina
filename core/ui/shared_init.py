"""Shared initialization logic for all Jenbina pages."""
import streamlit as st
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('LANGSMITH_TRACING', os.getenv('LANGSMITH_TRACING', 'false'))
os.environ.setdefault('LANGSMITH_ENDPOINT', os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com'))
os.environ.setdefault('LANGSMITH_PROJECT', os.getenv('LANGSMITH_PROJECT', 'jenbina'))
if os.getenv('LANGSMITH_API_KEY'):
    os.environ.setdefault('LANGSMITH_API_KEY', os.getenv('LANGSMITH_API_KEY'))

from core.connect import get_llm, get_json_llm
from core.heartbeat.host import JenbinaHost, process_host
from core.heartbeat.store import BeingStore
from core.memory.conversation_memory import ChromaMemoryManager
from core.environment.environment_simulator import EnvironmentSimulator
from core.auth.user_db import UserDatabase
from core.ui.auth_page import render_auth_page, render_user_header


def init_llm():
    """Initialize the chat LLM and the JSON-mode LLM for cognition."""
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "openai-advanced")
    llm = get_llm(provider=chat_model, temperature=1, max_tokens=600)
    llm_json_mode = get_json_llm(provider="openai", temperature=1)
    return llm, llm_json_mode


def _adopt_user_id() -> int | None:
    """JENBINA_ADOPT_USER_ID: whose saved Jenbina to adopt on the very first start."""
    try:
        return int(os.environ["JENBINA_ADOPT_USER_ID"])
    except (KeyError, ValueError):
        return None


def _build_host() -> JenbinaHost:
    llm, llm_json_mode = init_llm()
    insight_llm = get_llm(provider="openai-advanced", temperature=0.8, max_tokens=500)
    return JenbinaHost(BeingStore(), UserDatabase(), llm, llm_json_mode, insight_llm,
                       adopt_user_id=_adopt_user_id())


def get_host() -> JenbinaHost:
    """One host per process; retry ownership on later visits if it was refused.

    Not a Streamlit cache: clearing the cache or hot-reloading this module must
    not create a second host beside the one whose heart is already beating.
    """
    host = process_host(_build_host)
    if not host.hosting:
        host.start()
    return host


def save_person_state():
    """Persist the shared being through her owner."""
    get_host().save()


def init_session_state():
    """Initialize session resources; the host owns the live mind."""
    if 'action_history' not in st.session_state:
        st.session_state.action_history = []

    # Deep Emotional Mirror: background research on first login. Capture the
    # host and account here: worker threads must never use Streamlit state.
    if "user_research_done" not in st.session_state:
        st.session_state.user_research_done = True
        user = st.session_state.get("current_user")
        host = get_host()
        if user and host.person.social_cognition is not None:
            display_name = user.get("display_name") or user.get("email", "User")
            email = user.get("email", "")
            person_key = host.person_key(user)
            # Read without the mind lock: a page load must never wait for a beat.
            known = host.person.social_cognition.models.get(person_key)
            has_dossier = bool(known and known.user_dossier)
            if not has_dossier:
                import threading

                def _run_research():
                    try:
                        from core.research.user_research import research_user
                        insight_llm = get_llm(provider="openai-advanced", temperature=0.5, max_tokens=1000)
                        dossier = research_user(insight_llm, display_name, email)
                        if dossier:
                            with host.lock:
                                if host.hosting:
                                    model = host.person.social_cognition.get_or_create_model(person_key)
                                    model.user_dossier = dossier
                                    host.save()
                            print(f"User research complete for {display_name}")
                    except Exception as e:
                        print(f"Background user research failed: {e}")

                threading.Thread(target=_run_research, daemon=True).start()

    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = ChromaMemoryManager()
    if 'environment_simulator' not in st.session_state:
        st.session_state.environment_simulator = EnvironmentSimulator("Palo Alto, CA")
    if 'showed_return_greeting' not in st.session_state:
        st.session_state.showed_return_greeting = False


def require_auth():
    """Authenticate, then connect the session to the hosted Jenbina.

    Set env var JENBINA_SKIP_AUTH=1 to bypass Google SSO (for E2E tests).
    """
    if os.environ.get("JENBINA_SKIP_AUTH") == "1":
        if "authenticated" not in st.session_state:
            user_db = UserDatabase()
            st.session_state.user_db = user_db
            user = user_db.create_or_update_user(
                firebase_uid="test:e2e@test.local",
                email="e2e@test.local",
                display_name="E2E Test User",
                photo_url="",
                provider="test",
            )
            st.session_state.authenticated = True
            st.session_state.current_user = user
    else:
        if not render_auth_page():
            return False
        render_user_header(st.session_state.current_user)

    host = get_host()
    if not host.hosting:
        st.info("Jenbina is already living in another process. This window cannot reach her until that one stops.")
        return False
    st.session_state.person = host.person
    st.session_state.meta_cognitive_system = host.meta_cognitive_system
    init_session_state()
    return True
