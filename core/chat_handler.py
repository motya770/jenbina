from langchain.schema import HumanMessage

def handle_chat_interaction(
    st,
    llm,
    needs_response,
    world_description,
    action_decision,
    state_response=None,
    user_input=None,
    person_state=None,
    conversation_context=None
):
    """Handle chat interactions with Jenbin."""
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Build context-aware prompt
        context_parts = []
        
        if person_state:
            context_parts.append(f"Current State: {person_state}")
        
        if conversation_context:
            context_parts.append(f"Recent Conversation Context:\n{conversation_context}")
        
        context_parts.append(f"Current needs: {needs_response}")
        context_parts.append(f"World state: {world_description}")
        context_parts.append(f"Chosen action: {action_decision}")
        
        if state_response:
            context_parts.append(f"State analysis: {state_response}")
        
        full_context = "\n".join(context_parts)
        
        # Generate and display Jenbin's response
        response = llm.invoke([
            HumanMessage(content=f"""As Jenbin, respond to the following user message: "{user_input}"

Consider your current state and context:
{full_context}

Keep the response natural and in-character. Consider your current needs and how they might influence your response. If you have conversation history, reference it appropriately to maintain continuity.""")
        ])
        st.chat_message("assistant").write(response.content)
        
        return {
            "user_message": user_input,
            "assistant_response": response.content
        }
    
    return None 