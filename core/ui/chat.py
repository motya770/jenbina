"""Chat UI components for Jenbina app"""
import streamlit as st
from datetime import datetime
from core.interaction.chat_handler import (
    handle_chat_interaction,
    generate_first_greeting,
    generate_return_greeting,
    history_context,
)
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.auth.user_db import UserDatabase
from core.heartbeat.host import ChatTurn
from core.timeline import record_mood
from core.ui.pixel_theme import stage_pill_html


def check_return_greeting(person, llm, person_key: str, now: datetime | None = None) -> str | None:
    """Check how long since last visit and return an appropriate greeting, or None."""
    if st.session_state.get("showed_return_greeting"):
        return None

    now = now or datetime.now()
    model = person.social_cognition.get_or_create_model(person_key)
    last = model.last_visit_time
    model.last_visit_time = now

    if last is None:
        # First-time user
        st.session_state.showed_return_greeting = True
        if llm is not None:
            return generate_first_greeting(person, llm, person_key)
        return None

    gap = now - last
    gap_hours = gap.total_seconds() / 3600

    if gap_hours < 1:
        return None

    st.session_state.showed_return_greeting = True

    # Use LLM-generated greeting if available
    if llm is not None:
        return generate_return_greeting(person, llm, gap_hours, person_key)

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


def ensure_greeting(host, user: dict, llm) -> None:
    """Greet on an awake, available mind; retry on a later refresh otherwise."""
    if st.session_state.get("showed_return_greeting"):
        return

    with host.greeting_turn(user) as turn:
        if turn is None:
            return
        greeting = check_return_greeting(host.person, llm, turn.person_key)
        if greeting:
            host.person.send_message(turn.person_key, greeting, "greeting")
        # Considered once per session, greeted or not. The timeline refreshes
        # every few seconds, and each further check would take the mind lock
        # and save her whole state again.
        st.session_state.showed_return_greeting = True


def handle_user_input(person, llm, memory_manager, debug_mode, user_input, turn: ChatTurn):
    """Handle one submitted chat message and return the chat result, or
    ``None`` when there is no input. The caller holds ``host.chat_turn``."""
    person_key = turn.person_key

    if user_input:
        print("User input:", user_input)
        update_system_stage("listening…")

        # Store the user message in person's communication history
        person.receive_message(person_key, user_input, "text")
        if getattr(person, "social_cognition", None) is not None:
            # A message is a visit: the next return greeting measures from here.
            person.social_cognition.get_or_create_model(person_key).last_visit_time = datetime.now()

        # Store in SQLite
        user_db, _ = _get_user_db_and_id()
        user_id = turn.user_id
        if user_db and user_id:
            user_db.store_message(user_id, _get_user_display_name(), user_input, "user_message")

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
        recent_actions, _ = history_context(turn.history)

        # Handle chat interaction
        update_system_stage("replying…")
        chat_result = handle_chat_interaction(
            st=st,
            llm=llm,
            needs_response=turn.last_responses.get("needs_response"),
            world_description=turn.last_responses.get("world_description"),
            action_decision=turn.last_responses.get("action_decision"),
            state_response=turn.last_responses.get("state_response"),
            user_input=user_input,
            person_state=person.get_current_state(partner=person_key),
            conversation_context=recent_context,
            memory_manager=memory_manager,
            debug_mode=debug_mode,
            emotional_state=person.emotion_system.get_emotional_state_summary(),
            user_id=user_id,
            person=person,
            conversation_partner_name=person_key,
            recent_actions=recent_actions,
        )

        print(chat_result)

        # Analyze emotion impact from the conversation
        if chat_result and "assistant_response" in chat_result:
            person.send_message(person_key, chat_result["assistant_response"], "text")

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
                    record_mood(turn.event_log, emotions_before, person.get_emotions_snapshot(), "chat")
            except Exception as e:
                print(f"Emotion analysis after chat failed: {e}")

            # Satisfy social needs based on relationship closeness
            try:
                if getattr(person, "social_cognition", None) is not None:
                    model = person.social_cognition.get_or_create_model(person_key)
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


