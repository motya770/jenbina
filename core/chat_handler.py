from langchain.schema import HumanMessage

def handle_chat_interaction(
    st,
    llm,
    needs_response,
    world_description,
    action_decision,
    state_response=None
):
    """Handle chat interactions with Jenbin."""
    # Generate initial response
    jenbin_response = llm.invoke([
        HumanMessage(content=f"""Based on the following context, generate a natural response from Jenbin to the user:
        - Current needs: {needs_response}
        - World state: {world_description}
        - Chosen action: {action_decision}
        - State analysis: {state_response}
        
        Respond in first person as Jenbin, keeping the response conversational and natural.
        """)
    ])
    
    # Display Jenbin's response
    st.chat_message("assistant").write(jenbin_response.content)
    
    # Handle user input
    user_input = st.chat_input("Talk to Jenbin...")
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Generate and display Jenbin's response
        response = llm.invoke([
            HumanMessage(content=f"""As Jenbin, respond to the following user message: "{user_input}"
            Consider your current state and context:
            - Current needs: {needs_response}
            - World state: {world_description}
            Keep the response natural and in-character.""")
        ])
        st.chat_message("assistant").write(response.content)
        
        return {
            "user_message": user_input,
            "assistant_response": response.content
        }
    
    return {
        "assistant_response": jenbin_response.content
    } 