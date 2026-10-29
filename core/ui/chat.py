"""Chat UI components for Jenbina app"""
import streamlit as st
from datetime import datetime
from core.interaction.chat_handler import (
    handle_chat_interaction,
    generate_proactive_message,
    generate_first_greeting,
    generate_return_greeting,
    history_context,
)
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.auth.user_db import UserDatabase
from core.ui.shared_init import save_person_state
from core.timeline import EventLog, record_mood
from core.ui.pixel_theme import stage_pill_html


def check_proactive_message(person):
    """Check if Jenbina should initiate a message based on her current state.

    Returns a trigger context dict or None.
    """
    display_name = _get_user_display_name()

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


def send_proactive_message(person, llm):
    """Orchestrator: check triggers, generate message, store in history."""
    triggers = check_proactive_message(person)
    if not triggers:
        return None

    try:
        # Recent actions and world context from the simulation history
        recent_actions, world_context = history_context(st.session_state.get("simulation_history", []))

        message = generate_proactive_message(
            person, llm, triggers,
            display_name=_get_user_display_name(),
            recent_actions=recent_actions,
            world_context=world_context,
        )
        if not message:
            return None

        display_name = _get_user_display_name()
        person.send_message(display_name, message, "proactive")

        # Store in SQLite
        user_db, user_id = _get_user_db_and_id()
        if user_db and user_id:
            user_db.store_message(user_id, "Jenbina", message, "proactive_message")

        print(f"Proactive message sent: {message[:80]}...")
        return message
    except Exception as e:
        print(f"Proactive message failed: {e}")
        return None


def check_return_greeting(person, llm=None):
    """Check how long since last visit and return an appropriate greeting, or None."""
    if st.session_state.get("showed_return_greeting"):
        return None

    now = datetime.now()
    last = person.last_visit_time
    person.last_visit_time = now
    display_name = _get_user_display_name()

    if last is None:
        # First-time user
        st.session_state.showed_return_greeting = True
        if llm is not None:
            return generate_first_greeting(person, llm, display_name)
        return None

    gap = now - last
    gap_hours = gap.total_seconds() / 3600

    if gap_hours < 1:
        return None

    st.session_state.showed_return_greeting = True

    # Use LLM-generated greeting if available
    if llm is not None:
        return generate_return_greeting(person, llm, gap_hours, display_name)

    # Fallback static greetings
    if gap_hours < 6:
        return "You're back!"
    elif gap_hours < 24:
        return "I missed you today..."
    elif gap_hours < 72:
        return "It's been a while..."
    else:
        days = int(gap.total_seconds() / 86400)
        return f"I was worried you forgot about me... it's been {days} days."


def _get_user_display_name() -> str:
    """Return the authenticated user's display name, or 'User' as fallback."""
    user = st.session_state.get("current_user")
    if user:
        return user.get("display_name") or user.get("email", "User")
    return "User"


def _get_user_db_and_id():
    """Return (UserDatabase, user_id) if authenticated, else (None, None)."""
    user = st.session_state.get("current_user")
    if not user:
        return None, None
    user_db = st.session_state.get("user_db")
    if user_db is None:
        user_db = UserDatabase()
        st.session_state.user_db = user_db
    return user_db, user["id"]


def get_event_log() -> EventLog:
    """The session's event log, built once from the logged-in user (an
    in-memory log when there is no user)."""
    user_db, user_id = _get_user_db_and_id()
    log = st.session_state.get("event_log")
    if log is None or getattr(log, "user_id", None) != user_id:
        log = EventLog(user_db, user_id)
        st.session_state["event_log"] = log
    return log


def ensure_outreach(person, llm) -> None:
    """Let Jenbina speak first when she should: the return greeting, and the
    once-per-session proactive message. Both land in the conversation with
    their own message types so the timeline can label them."""
    display_name = _get_user_display_name()
    greeting = check_return_greeting(person, llm)
    if greeting:
        person.send_message(display_name, greeting, "greeting")

    if not st.session_state.get("proactive_checked"):
        st.session_state.proactive_checked = True
        proactive_msg = send_proactive_message(person, llm)
        if proactive_msg:
            save_person_state()


def handle_user_input(person, llm, memory_manager, debug_mode, user_input):
    """Handle one submitted chat message and return the chat result, or
    ``None`` when there is no input. The caller reads ``st.chat_input``."""
    display_name = _get_user_display_name()

    if user_input:
        print("User input:", user_input)
        update_system_stage("listening…")

        # Store the user message in person's communication history
        person.receive_message(display_name, user_input, "text")

        # Store in SQLite
        user_db, user_id = _get_user_db_and_id()
        if user_db and user_id:
            user_db.store_message(user_id, display_name, user_input, "user_message")

        # Get conversation history for context (last 200 messages from SQLite)
        update_system_stage("remembering…")
        recent_context = ""
        if user_db and user_id:
            db_messages = user_db.get_messages(user_id, limit=200)
            recent_context = "\n".join([
                f"{msg['sender']}: {msg['content']}"
                for msg in db_messages
            ])

        # Recent actions from the simulation history
        recent_actions, _ = history_context(st.session_state.get("simulation_history", []))

        # Handle chat interaction
        update_system_stage("replying…")
        chat_result = handle_chat_interaction(
            st=st,
            llm=llm,
            needs_response=st.session_state.needs_response,
            world_description=st.session_state.world_description,
            action_decision=st.session_state.action_decision,
            state_response=st.session_state.state_response,
            user_input=user_input,
            person_state=person.get_current_state(),
            conversation_context=recent_context,
            memory_manager=memory_manager,
            debug_mode=debug_mode,
            emotional_state=person.emotion_system.get_emotional_state_summary(),
            user_id=st.session_state.get("current_user", {}).get("id"),
            person=person,
            conversation_partner_name=display_name,
            recent_actions=recent_actions,
        )

        print(chat_result)

        # Analyze emotion impact from the conversation
        if chat_result and "assistant_response" in chat_result:
            person.send_message(display_name, chat_result["assistant_response"], "text")

            # Display context stats banner
            recent_count = chat_result.get("recent_messages_count", 0)
            semantic_count = chat_result.get("semantic_docs_count", 0)
            st.toast(f"Context: {recent_count} recent messages + {semantic_count} semantically relevant", icon="📚")

            # Store Jenbina's reply in SQLite
            if user_db and user_id:
                user_db.store_message(user_id, "Jenbina", chat_result["assistant_response"], "jenbina_response")

            try:
                update_system_stage("feeling…")
                chat_situation = f"User said: \"{user_input}\". Jenbina responded: \"{chat_result['assistant_response']}\""
                emotions_before = person.get_emotions_snapshot()
                emotion_adjustments = analyze_emotion_impact(
                    llm=llm,
                    situation=chat_situation,
                    emotion_system=person.emotion_system,
                    maslow_needs=person.maslow_needs,
                )
                if emotion_adjustments:
                    person.emotion_system.apply_adjustments(emotion_adjustments)
                    record_mood(get_event_log(), emotions_before, person.get_emotions_snapshot(), "chat")
            except Exception as e:
                print(f"Emotion analysis after chat failed: {e}")

            # Satisfy social needs based on relationship closeness
            try:
                if getattr(person, "social_cognition", None) is not None:
                    model = person.social_cognition.get_or_create_model(display_name)
                    trust = model.relationship.trust
                    closeness = model.relationship.closeness
                    avg_factor = max(0.3, (trust + closeness) / 200)
                    person.maslow_needs.satisfy_need("social_connection", 15 * avg_factor, source="chat")
                    person.maslow_needs.satisfy_need("friendship", 10 * avg_factor, source="chat")
                    person.maslow_needs.satisfy_need("belonging", 8 * avg_factor, source="chat")
                    person.maslow_needs.satisfy_need("self_esteem", 5, source="chat")
                    print(f"Chat need satisfaction: factor={avg_factor:.2f} (trust={trust:.1f}, closeness={closeness:.1f})")
            except Exception as e:
                print(f"Chat need satisfaction failed: {e}")

        update_system_stage("idle")

        # Add to action history
        if "user_message" in chat_result:
            st.session_state.action_history.append({
                "role": "user",
                "content": chat_result["user_message"]
            })
        st.session_state.action_history.append({
            "role": "assistant",
            "content": chat_result["assistant_response"]
        })

        return chat_result

    return None


def update_system_stage(stage: str):
    """Update the system stage one-liner in real time."""
    st.session_state["system_stage"] = stage
    placeholder = st.session_state.get("_stage_placeholder")
    if placeholder is not None:
        placeholder.markdown(stage_pill_html(stage), unsafe_allow_html=True)


