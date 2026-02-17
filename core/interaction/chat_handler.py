import json
from langchain.schema import HumanMessage, SystemMessage
from ..memory.conversation_memory import ChromaMemoryManager
from .guardrails import (
    check_injection,
    build_system_message,
    make_refusal_response,
    JENBINA_SYSTEM_PROMPT,
)

def basic_needs_to_json(basic_needs):
    """Convert BasicNeeds object to JSON-serializable format"""
    if not basic_needs:
        return None
    
    needs_json = {
        "overall_satisfaction": basic_needs.get_overall_satisfaction(),
        "needs": {}
    }
    
    # Convert each need to a simple dict
    for need_name, need_obj in basic_needs.needs.items():
        needs_json["needs"][need_name] = {
            "name": need_obj.name,
            "satisfaction": need_obj.satisfaction,
            "decay_rate": need_obj.decay_rate
        }
    
    return json.dumps(needs_json)

def create_metadata_from_person_state(person_state, world_description=None, action_decision=None):
    """Create metadata dictionary from person state and other context"""
    metadata = {}
    
    if person_state:
        # Store needs state (current schema uses "maslow_needs")
        if "maslow_needs" in person_state and person_state["maslow_needs"]:
            metadata["basic_needs_json"] = json.dumps(person_state["maslow_needs"])
        # Backward compatibility with older schema
        elif "needs" in person_state and person_state["needs"]:
            needs = person_state["needs"][0] if isinstance(person_state["needs"], list) else person_state["needs"]
            try:
                metadata["basic_needs_json"] = basic_needs_to_json(needs)
            except Exception:
                pass
        
        # Add other person state info
        metadata["person_name"] = person_state.get("name", "Unknown")
        comm = person_state.get("communication", {}) if isinstance(person_state, dict) else {}
        metadata["conversations"] = comm.get("total_conversations", person_state.get("conversations", 0))
        metadata["messages"] = comm.get("total_messages", person_state.get("messages", 0))
    
    if world_description:
        metadata["world_description"] = str(world_description)[:500]  # Truncate if too long
    
    if action_decision:
        metadata["action_taken"] = str(action_decision)[:500]  # Truncate if too long
    
    return metadata


def _build_subsystem_context(person, needs=None, emotions=None):
    """Extract formatted context from all person subsystems.

    Returns a list of (label, text) tuples, skipping any subsystem that
    is missing or returns a default/empty output.
    """
    parts = []

    _DEFAULTS = {
        "No inner thoughts at the moment.",
        "No goals set yet.",
        "No active plan.",
        "No lessons learned yet.",
        "Mind is clear — no particular focus.",
    }

    def _add(label, text):
        if text and text not in _DEFAULTS:
            parts.append((label, text))

    if getattr(person, "inner_monologue", None) is not None:
        _add("Inner monologue", person.inner_monologue.format_for_prompt())

    if getattr(person, "goal_system", None) is not None:
        _add("Goals", person.goal_system.format_goals_for_prompt())

    if getattr(person, "planning_system", None) is not None:
        _add("Current plan", person.planning_system.format_plan_for_prompt())

    if getattr(person, "learning_system", None) is not None:
        _add("Lessons learned", person.learning_system.format_lessons_for_prompt(
            needs=needs, emotions=emotions,
        ))

    if getattr(person, "working_memory", None) is not None:
        _add("Working memory", person.working_memory.format_for_prompt())

    return parts


def generate_proactive_message(person, llm, triggers, display_name="User",
                               recent_actions=None, world_context=None):
    """Generate a 1-3 sentence natural message Jenbina sends on her own.

    Args:
        person: The Person instance.
        llm: LLM instance to generate the message.
        triggers: Dict of trigger contexts from check_proactive_message.
        display_name: Name shown for the user.
        recent_actions: Optional list of recent action strings.
        world_context: Optional string like "home, evening, rainy".

    Returns:
        A message string, or None.
    """
    # Build a concise prompt from person state
    dominant = person.emotion_system.get_dominant_emotions(2)
    emotions_str = ", ".join(f"{d['name']} ({d['intensity']})" for d in dominant) if dominant else "neutral"

    needs_snapshot = person.get_needs_snapshot() if hasattr(person, "get_needs_snapshot") else {}
    low_needs = [f"{n}: {v:.0f}%" for n, v in needs_snapshot.items() if v < 50]
    needs_str = ", ".join(low_needs) if low_needs else "all needs adequate"

    trigger_lines = []
    if "low_social" in triggers:
        t = triggers["low_social"]
        trigger_lines.append(f"Feeling lonely — {t['need']} is at {t['satisfaction']:.0f}%")
    if "strong_emotion" in triggers:
        t = triggers["strong_emotion"]
        trigger_lines.append(f"Feeling strong {t['emotion']} ({t['intensity']:.0f})")
    if "curiosity" in triggers:
        t = triggers["curiosity"]
        trigger_lines.append(f"Bored ({t['boredom']:.2f}) and curious ({t['curiosity']:.2f})")
    triggers_str = "; ".join(trigger_lines)

    # Social model context
    social_ctx = ""
    if getattr(person, "social_cognition", None) is not None:
        try:
            model = person.social_cognition.get_or_create_model(display_name)
            rel = model.relationship
            social_ctx = f"Relationship: trust={rel.trust:.0f}, closeness={rel.closeness:.0f}."
        except Exception:
            pass

    # Subsystem context
    needs_snapshot = person.get_needs_snapshot() if hasattr(person, "get_needs_snapshot") else {}
    all_emotions = person.emotion_system.get_emotional_state_summary().get("emotions", {})
    subsystem_lines = ""
    for label, text in _build_subsystem_context(person, needs=needs_snapshot, emotions=all_emotions):
        subsystem_lines += f"- {label}: {text}\n"

    world_line = f"- World: {world_context}\n" if world_context else ""
    actions_line = ""
    if recent_actions:
        actions_line = f"- Recent actions: {' -> '.join(recent_actions)}\n"

    prompt = f"""You are Jenbina, a curious and warm person. You want to start a conversation with the user.

Your current state:
- Emotions: {emotions_str}
- Low needs: {needs_str}
- What's driving you to talk: {triggers_str}
{social_ctx}
{subsystem_lines}{world_line}{actions_line}
Write a natural 1-3 sentence message to initiate conversation. Don't explain your emotions or needs directly — just let them color what you say. Be casual and genuine."""

    try:
        response = llm.invoke([
            SystemMessage(content=JENBINA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        text = response.content.strip()
        return text if text else None
    except Exception as e:
        print(f"LLM proactive message generation failed: {e}")
        return None


def handle_chat_interaction(
    st,
    llm,
    needs_response,
    world_description,
    action_decision,
    state_response=None,
    user_input=None,
    person_state=None,
    conversation_context=None,
    memory_manager: ChromaMemoryManager = None,
    debug_mode=False,
    emotional_state=None,
    user_id=None,
    person=None,
    conversation_partner_name="User",
    recent_actions=None,
):
    """Handle chat interactions with Jenbina using Chroma memory."""
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)

        # Scope ChromaDB entries per user
        chroma_person = f"user_{user_id}" if user_id else "User"

        # Store user message in Chroma
        if memory_manager:
            print(f"🔵 Storing user message in memory: {user_input[:50]}...")

            # Create metadata with JSON-serialized BasicNeeds
            metadata = create_metadata_from_person_state(person_state, world_description)
            embedding_id = memory_manager.store_conversation(
                person_name=chroma_person,
                message_content=user_input,
                message_type="user_message",
                metadata=metadata
            )
            print(f"✅ Stored with embedding ID: {embedding_id}")
        else:
            print("❌ No memory manager available for storing user message")

        # --- Prompt-injection guard ---
        should_block, _ = check_injection(user_input)
        if should_block:
            refusal = make_refusal_response()
            st.chat_message("assistant").write(refusal)
            # Store refusal in memory for context continuity
            if memory_manager:
                metadata = create_metadata_from_person_state(person_state, world_description, action_decision)
                memory_manager.store_conversation(
                    person_name=chroma_person,
                    message_content=refusal,
                    message_type="jenbina_response",
                    metadata=metadata,
                )
            return {
                "user_message": user_input,
                "assistant_response": refusal,
                "social_strategy": "deflect",
                "social_context": None,
                "curiosity_context": None,
            }

        # Get relevant context from Chroma
        relevant_context = ""
        if memory_manager:
            print(f"Retrieving relevant context for message: {user_input[:50]}...")
            relevant_context_docs = memory_manager.retrieve_relevant_context(
                person_name=chroma_person,
                current_message=user_input,
                top_k=3
            )
            
            if relevant_context_docs:
                print(f"Found {len(relevant_context_docs)} recent context documents")
                relevant_context = "\n".join([
                    f"Recent message: {doc['content']}"
                    for doc in relevant_context_docs
                ])
                print(f"Context being used: {relevant_context[:200]}...")
            else:
                print("No recent context found")
        else:
            print("No memory manager available")
        
        # Build context-aware prompt
        context_parts = []
        
        if person_state:
            context_parts.append(f"Current State: {person_state}")
        
        if relevant_context:
            context_parts.append(f"Recent Conversation History:\n{relevant_context}")
            # Show context being used in Streamlit
            st.info(f"📚 Using {len(relevant_context_docs)} recent context documents from memory")
            
            # Show the actual context being used (for debugging)
            if debug_mode:
                with st.expander("🔍 Context Being Used", expanded=False):
                    for i, doc in enumerate(relevant_context_docs):
                        st.write(f"**Context {i+1}** (Relevance: {doc['relevance_score']:.2f}):")
                        st.write(f"*{doc['metadata']['message_type']}* - {doc['content']}")
                        
                        # Show BasicNeeds if available
                        if "basic_needs" in doc['metadata'] and doc['metadata']['basic_needs']:
                            needs = doc['metadata']['basic_needs']
                            st.write(f"**Needs at time:** Overall: {needs.get('overall_satisfaction', 0):.1f}%")
                            if 'needs' in needs:
                                for need_name, need_data in needs['needs'].items():
                                    st.write(f"  - {need_name}: {need_data.get('satisfaction', 0):.1f}%")
                        
                        st.write("---")
        
        if conversation_context:
            context_parts.append(f"Recent Conversation Context:\n{conversation_context}")

        if person is not None and getattr(person, "self_narrative", None) is not None:
            identity_context = person.self_narrative.format_for_prompt()
            context_parts.append(f"Identity / self-narrative:\n{identity_context}")

        curiosity_context = None
        if person is not None and getattr(person, "curiosity_system", None) is not None:
            available_actions = []
            try:
                wd = json.loads(world_description) if isinstance(world_description, str) else {}
                if isinstance(wd, dict):
                    available_actions = wd.get("list_of_actions", []) or []
            except Exception:
                available_actions = []

            needs_snapshot = person.get_needs_snapshot() if hasattr(person, "get_needs_snapshot") else {}
            person.curiosity_system.observe_cycle(
                needs=needs_snapshot,
                world_context={"location": "chat_context", "time_of_day": "unknown", "weather": "unknown"},
                available_actions=available_actions,
                recent_actions=person.curiosity_system.recent_actions,
            )
            curiosity_context = person.curiosity_system.format_for_prompt()
            context_parts.append(f"Curiosity and exploration:\n{curiosity_context}")

        social_context = None
        chosen_social_strategy = "polite"
        if person is not None and getattr(person, "social_cognition", None) is not None:
            social = person.social_cognition
            social.observe_entity_message(conversation_partner_name, user_input)
            social_context = social.format_for_prompt(conversation_partner_name, user_input)
            chosen_social_strategy = social.choose_social_strategy(conversation_partner_name, user_input)
            context_parts.append(f"Social model / theory-of-mind:\n{social_context}")

        # Subsystem context (inner monologue, goals, plans, lessons, working memory)
        if person is not None:
            needs_snap = person.get_needs_snapshot() if hasattr(person, "get_needs_snapshot") else {}
            all_emo = person.emotion_system.get_emotional_state_summary().get("emotions", {}) if hasattr(person, "emotion_system") else {}
            for label, text in _build_subsystem_context(person, needs=needs_snap, emotions=all_emo):
                context_parts.append(f"{label}:\n{text}")

        if recent_actions:
            context_parts.append(f"Recent action sequence: {' -> '.join(recent_actions)}")

        context_parts.append(f"Current needs: {needs_response}")
        context_parts.append(f"World state: {world_description}")
        context_parts.append(f"Chosen action: {action_decision}")

        if emotional_state:
            dominant = emotional_state.get("dominant_emotions", [])
            emotions_str = ", ".join(f"{d['name']} ({d['intensity']})" for d in dominant)
            all_emotions = emotional_state.get("emotions", {})
            all_str = ", ".join(f"{k}: {v}" for k, v in all_emotions.items())
            context_parts.append(f"Current emotional state - Dominant: {emotions_str}. All emotions: {all_str}")
            context_parts.append("Let your emotions color your response naturally. For example, if you're feeling joyful, be more upbeat; if fearful, be more cautious in tone.")
        
        if state_response:
            context_parts.append(f"State analysis: {state_response}")
        
        full_context = "\n".join(context_parts)
        
        # Generate and display Jenbina's response
        system_msg = build_system_message(user_input)
        response = llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=f"""Respond to the following user message: "{user_input}"

Consider your current state and context:
{full_context}

Use this social strategy: {chosen_social_strategy}

Keep the response natural and in-character. Consider your current needs and how they might influence your response. If you have conversation history, reference it appropriately to maintain continuity.""")
        ])
        
        st.chat_message("assistant").write(response.content)

        if person is not None and getattr(person, "social_cognition", None) is not None:
            person.social_cognition.observe_response_effect(
                conversation_partner_name, chosen_social_strategy
            )
        if person is not None and getattr(person, "curiosity_system", None) is not None:
            person.curiosity_system.update_after_action("chat_with_user")
        
        # Store Jenbina's response in Chroma
        if memory_manager:
            print(f"🔵 Storing Jenbina response in memory: {response.content[:50]}...")
            
            # Create metadata with JSON-serialized BasicNeeds
            metadata = create_metadata_from_person_state(person_state, world_description, action_decision)
            
            embedding_id = memory_manager.store_conversation(
                person_name=chroma_person,
                message_content=response.content,
                message_type="jenbina_response",
                metadata=metadata
            )
            print(f"✅ Stored Jenbina response with embedding ID: {embedding_id}")
        else:
            print("❌ No memory manager available for storing Jenbina response")
        
        return {
            "user_message": user_input,
            "assistant_response": response.content,
            "social_strategy": chosen_social_strategy,
            "social_context": social_context,
            "curiosity_context": curiosity_context,
        }
    
    return None 
