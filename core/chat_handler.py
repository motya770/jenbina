from langchain.schema import HumanMessage

def handle_chat_interaction(
    st,
    llm,
    needs_response,
    world_description,
    action_decision,
    state_response=None,
    user_input=None
):
    """Handle chat interactions with Jenbin."""
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Generate and display Jenbin's response
        response = llm.invoke([
            HumanMessage(content=f"""As Jenbin, respond to the following user message: "{user_input}"
            Consider your current state and context:
            - Current needs: {needs_response}
            - World state: {world_description}
            - Chosen action: {action_decision}
            - State analysis: {state_response}
            
            Keep the response natural and in-character.""")
        ])
        st.chat_message("assistant").write(response.content)
        
        return {
            "user_message": user_input,
            "assistant_response": response.content
        }
    
    return None 