import json
from langchain.schema import HumanMessage
from conversation_memory import ChromaMemoryManager

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
        # Store BasicNeeds as JSON
        if "needs" in person_state and person_state["needs"]:
            needs = person_state["needs"][0] if isinstance(person_state["needs"], list) else person_state["needs"]
            metadata["basic_needs_json"] = basic_needs_to_json(needs)
        
        # Add other person state info
        metadata["person_name"] = person_state.get("name", "Unknown")
        metadata["conversations"] = person_state.get("conversations", 0)
        metadata["messages"] = person_state.get("messages", 0)
    
    if world_description:
        metadata["world_description"] = str(world_description)[:500]  # Truncate if too long
    
    if action_decision:
        metadata["action_taken"] = str(action_decision)[:500]  # Truncate if too long
    
    return metadata

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
    memory_manager=None,
    debug_mode=False
):
    """Handle chat interactions with Jenbina using Chroma memory."""
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Store user message in Chroma
        if memory_manager:
            print(f"🔵 Storing user message in memory: {user_input[:50]}...")
            
            # Create metadata with JSON-serialized BasicNeeds
            metadata = create_metadata_from_person_state(person_state, world_description)
            
            embedding_id = memory_manager.store_conversation(
                person_name="User",
                message_content=user_input,
                message_type="user_message",
                metadata=metadata
            )
            print(f"✅ Stored with embedding ID: {embedding_id}")
        else:
            print("❌ No memory manager available for storing user message")
        
        # Get relevant context from Chroma
        relevant_context = ""
        if memory_manager:
            print(f"Retrieving relevant context for message: {user_input[:50]}...")
            relevant_context_docs = memory_manager.retrieve_relevant_context(
                person_name="User",
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
        
        context_parts.append(f"Current needs: {needs_response}")
        context_parts.append(f"World state: {world_description}")
        context_parts.append(f"Chosen action: {action_decision}")
        
        if state_response:
            context_parts.append(f"State analysis: {state_response}")
        
        full_context = "\n".join(context_parts)
        
        # Generate and display Jenbina's response
        response = llm.invoke([
            HumanMessage(content=f"""As Jenbina, respond to the following user message: "{user_input}"

Consider your current state and context:
{full_context}

Keep the response natural and in-character. Consider your current needs and how they might influence your response. If you have conversation history, reference it appropriately to maintain continuity.""")
        ])
        
        st.chat_message("assistant").write(response.content)
        
        # Store Jenbina's response in Chroma
        if memory_manager:
            print(f"🔵 Storing Jenbina response in memory: {response.content[:50]}...")
            
            # Create metadata with JSON-serialized BasicNeeds
            metadata = create_metadata_from_person_state(person_state, world_description, action_decision)
            
            embedding_id = memory_manager.store_conversation(
                person_name="User",
                message_content=response.content,
                message_type="jenbina_response",
                metadata=metadata
            )
            print(f"✅ Stored Jenbina response with embedding ID: {embedding_id}")
        else:
            print("❌ No memory manager available for storing Jenbina response")
        
        return {
            "user_message": user_input,
            "assistant_response": response.content
        }
    
    return None 