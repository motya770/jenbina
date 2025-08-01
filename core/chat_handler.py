from langchain.schema import HumanMessage
from conversation_memory import ChromaMemoryManager

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
    memory_manager=None
):
    """Handle chat interactions with Jenbina using Chroma memory."""
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Store user message in Chroma
        if memory_manager:
            memory_manager.store_conversation(
                person_name="User",
                message_content=user_input,
                message_type="user_message",
                metadata={
                    "needs_state": person_state.get("needs", []) if person_state else [],
                    "world_state": world_description
                }
            )
        
        # Get relevant context from Chroma
        relevant_context = ""
        if memory_manager:
            relevant_context_docs = memory_manager.retrieve_relevant_context(
                person_name="User",
                current_message=user_input,
                top_k=3
            )
            
            if relevant_context_docs:
                relevant_context = "\n".join([
                    f"Previous context: {doc['content']}"
                    for doc in relevant_context_docs
                ])
        
        # Build context-aware prompt
        context_parts = []
        
        if person_state:
            context_parts.append(f"Current State: {person_state}")
        
        if relevant_context:
            context_parts.append(f"Relevant Conversation History:\n{relevant_context}")
        
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
            memory_manager.store_conversation(
                person_name="User",
                message_content=response.content,
                message_type="jenbina_response",
                metadata={
                    "needs_state": person_state.get("needs", []) if person_state else [],
                    "world_state": world_description,
                    "action_taken": action_decision
                }
            )
        
        return {
            "user_message": user_input,
            "assistant_response": response.content
        }
    
    return None 