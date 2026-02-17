"""Chat UI components for Jenbina app"""
import streamlit as st
from datetime import datetime
from core.interaction.chat_handler import handle_chat_interaction, generate_proactive_message
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.auth.user_db import UserDatabase
from core.ui.shared_init import save_person_state


def display_person_state_compact(person):
    """Display current person state in compact form"""
    st.write("**Current State:**")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")
    dominant = person.emotion_system.get_dominant_emotions(3)
    emotions_str = ", ".join(f"{d['name']}: {d['intensity']}" for d in dominant)
    st.write(f"- Emotions: {emotions_str}")


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
        # Extract recent actions and world context from simulation history
        recent_actions = None
        world_context = None
        sim_history = st.session_state.get("simulation_history", [])
        if sim_history:
            recent_actions = [
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
                world_context = ", ".join(parts) if parts else None

        message = generate_proactive_message(
            person, llm, triggers,
            display_name=_get_user_display_name(),
            recent_actions=recent_actions,
            world_context=world_context,
        )
        if not message:
            return None

        display_name = _get_user_display_name()
        person.send_message(display_name, message, "text")

        # Store in SQLite
        user_db, user_id = _get_user_db_and_id()
        if user_db and user_id:
            user_db.store_message(user_id, "Jenbina", message, "proactive_message")

        print(f"Proactive message sent: {message[:80]}...")
        return message
    except Exception as e:
        print(f"Proactive message failed: {e}")
        return None


def check_return_greeting(person):
    """Check how long since last visit and return an appropriate greeting, or None."""
    if st.session_state.get("showed_return_greeting"):
        return None

    now = datetime.now()
    last = person.last_visit_time
    person.last_visit_time = now

    if last is None:
        st.session_state.showed_return_greeting = True
        return None

    gap = now - last
    gap_hours = gap.total_seconds() / 3600

    st.session_state.showed_return_greeting = True

    if gap_hours < 1:
        return None
    elif gap_hours < 6:
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


def handle_user_input(person, llm, memory_manager, debug_mode):
    """Handle user chat input and return result"""
    display_name = _get_user_display_name()
    user_input = st.chat_input("Talk to Jenbina...")

    if user_input:
        print("User input:", user_input)
        update_system_stage("Receiving message...")

        # Store the user message in person's communication history
        person.receive_message(display_name, user_input, "text")

        # Store in SQLite
        user_db, user_id = _get_user_db_and_id()
        if user_db and user_id:
            user_db.store_message(user_id, display_name, user_input, "user_message")

        # Get conversation history for context
        update_system_stage("Retrieving context...")
        conversation_history = person.get_conversation_history(display_name, count=1000)
        recent_context = "\n".join([
            f"{msg.sender}: {msg.content}"
            for msg in conversation_history
        ])

        # Extract recent actions from simulation history
        recent_actions = None
        sim_history = st.session_state.get("simulation_history", [])
        if sim_history:
            recent_actions = [
                r.get("chosen_action", "")
                for r in sim_history[-6:]
                if r.get("chosen_action")
            ]

        # Handle chat interaction
        update_system_stage("Generating response...")
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

            # Store Jenbina's reply in SQLite
            if user_db and user_id:
                user_db.store_message(user_id, "Jenbina", chat_result["assistant_response"], "jenbina_response")

            try:
                update_system_stage("Analyzing emotions...")
                chat_situation = f"User said: \"{user_input}\". Jenbina responded: \"{chat_result['assistant_response']}\""
                emotion_adjustments = analyze_emotion_impact(
                    llm=llm,
                    situation=chat_situation,
                    emotion_system=person.emotion_system,
                    maslow_needs=person.maslow_needs,
                )
                if emotion_adjustments:
                    person.emotion_system.apply_adjustments(emotion_adjustments)
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

        update_system_stage("Ready")

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


def display_communication_stats(person):
    """Display communication statistics"""
    with st.expander("Communication Statistics", expanded=False):
        comm_stats = person.get_communication_stats()
        st.write(f"**Total Conversations:** {comm_stats['total_conversations']}")
        st.write(f"**Total Messages:** {comm_stats['total_messages']}")
        
        if comm_stats['most_active_conversations']:
            st.write("**Most Active Conversations:**")
            for conv in comm_stats['most_active_conversations']:
                st.write(f"- {conv['outsider']}: {conv['message_count']} messages")


def display_conversation_history(person):
    """Display recent conversation history"""
    display_name = _get_user_display_name()
    with st.expander("Recent Conversation History", expanded=False):
        user_summary = person.get_conversation_summary(display_name)
        if user_summary['message_count'] > 0:
            st.write(f"**Messages with {display_name}:** {user_summary['message_count']}")
            st.write(f"**Last Interaction:** {user_summary['last_interaction'].strftime('%Y-%m-%d %H:%M')}")

            st.write("**Recent Messages:**")
            for msg in user_summary['recent_messages']:
                sender_icon = "👤" if msg['sender'] != "person" else "🤖"
                st.write(f"{sender_icon} **{msg['sender']}** ({msg['timestamp'].strftime('%H:%M')}): {msg['content']}")
        else:
            st.write("No conversation history yet.")


def display_memory_stats(memory_manager):
    """Display memory system statistics"""
    with st.expander("Memory System Statistics", expanded=False):
        memory_stats = memory_manager.get_memory_stats()
        st.write(f"**Total Conversations in Memory:** {memory_stats.get('total_conversations', 0)}")
        st.write(f"**Unique People:** {memory_stats.get('unique_people', 0)}")
        st.write(f"**Memory Size:** {memory_stats.get('memory_size_mb', 0)} MB")
        
        if memory_stats.get('people'):
            st.write("**People in Memory:**")
            for person_name in memory_stats['people']:
                st.write(f"- {person_name}")
        
        if memory_stats.get('message_types'):
            st.write("**Message Types:**")
            for msg_type, count in memory_stats['message_types'].items():
                st.write(f"- {msg_type}: {count}")


def display_memory_debug(memory_manager):
    """Display memory debug information"""
    with st.expander("🐛 Memory Debug Info", expanded=False):
        st.write("**Memory Manager Status:**")
        st.write(f"- Memory Manager Initialized: {memory_manager is not None}")
        st.write(f"- Chroma Client: {memory_manager.client is not None if memory_manager else False}")
        st.write(f"- Collection: {memory_manager.collection is not None if memory_manager else False}")
        
        # Test memory operations
        if st.button("🧪 Test Memory Operations"):
            try:
                # Test storing
                test_id = memory_manager.store_conversation(
                    "TestUser", "This is a test message", "test_message"
                )
                st.success(f"✅ Test message stored with ID: {test_id}")
                
                # Test retrieval
                test_context = memory_manager.retrieve_relevant_context(
                    "TestUser", "test message", top_k=1
                )
                st.success(f"✅ Test retrieval found {len(test_context)} documents")
                
                # Clean up test
                memory_manager.clear_memory("TestUser")
                st.success("✅ Test data cleaned up")
                
            except Exception as e:
                st.error(f"❌ Memory test failed: {str(e)}")


def display_social_model(person):
    """Display social model stats for current user conversation partner."""
    if getattr(person, "social_cognition", None) is None:
        return

    display_name = _get_user_display_name()
    model = person.social_cognition.get_or_create_model(display_name)
    rel = model.relationship
    interests = sorted(model.interests.items(), key=lambda kv: kv[1], reverse=True)[:5]

    with st.expander("Social Model (Theory of Mind)", expanded=False):
        st.write(f"**User:** {display_name}")
        st.write(f"**Inferred Emotion:** {model.inferred_emotional_state}")
        st.write(
            f"**Relationship:** trust={rel.trust:.1f}, closeness={rel.closeness:.1f}, conflict={rel.conflict:.1f}, interactions={rel.interactions}"
        )
        if interests:
            st.write("**Top Interests:**")
            for topic, score in interests:
                st.write(f"- {topic}: {score:.2f}")
        if model.beliefs:
            st.write("**Recent Beliefs:**")
            for belief in model.beliefs[-5:]:
                st.write(f"- {belief}")


def _init_stage_placeholder():
    """Create or reuse the st.empty() placeholder for system stage."""
    placeholder = st.empty()
    st.session_state["_stage_placeholder"] = placeholder
    stage = st.session_state.get("system_stage", "Idle")
    placeholder.markdown(f"`⚙️ {stage}`")
    return placeholder


def update_system_stage(stage: str):
    """Update the system stage one-liner in real time."""
    st.session_state["system_stage"] = stage
    placeholder = st.session_state.get("_stage_placeholder")
    if placeholder is not None:
        placeholder.markdown(f"`⚙️ {stage}`")


def render_chat_simple(person, llm, memory_manager, debug_mode):
    """Render a minimal chat: message history + input only."""
    display_name = _get_user_display_name()

    # Show live-updating system stage one-liner
    _init_stage_placeholder()

    # Check for return greeting
    greeting = check_return_greeting(person)
    if greeting:
        person.send_message(display_name, greeting, "text")

    # Check for proactive message (independent of simulation)
    if not st.session_state.get("proactive_checked"):
        st.session_state.proactive_checked = True
        proactive_msg = send_proactive_message(person, llm)
        if proactive_msg:
            save_person_state()

    conversation_history = person.get_conversation_history(display_name, count=50)

    for msg in conversation_history:
        is_user = msg.sender != "person" and msg.sender != person.name
        with st.chat_message("user" if is_user else "assistant"):
            st.write(msg.content)

    handle_user_input(person, llm, memory_manager, debug_mode)


def render_chat_interface(person, llm, memory_manager, debug_mode):
    """Render the complete chat interface with statistics"""
    st.write("**6. Interaction with User:**")
    st.write("### Chat with Jenbina")

    # Show live-updating system stage one-liner
    _init_stage_placeholder()

    # Check for return greeting
    display_name = _get_user_display_name()
    greeting = check_return_greeting(person)
    if greeting:
        person.send_message(display_name, greeting, "text")

    # Check for proactive message (independent of simulation)
    if not st.session_state.get("proactive_checked"):
        st.session_state.proactive_checked = True
        proactive_msg = send_proactive_message(person, llm)
        if proactive_msg:
            save_person_state()

    display_person_state_compact(person)
    handle_user_input(person, llm, memory_manager, debug_mode)
    display_communication_stats(person)
    display_conversation_history(person)
    display_social_model(person)
    display_memory_stats(memory_manager)

    if debug_mode:
        display_memory_debug(memory_manager)
