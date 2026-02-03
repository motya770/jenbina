"""Chat UI components for Jenbina app"""
import streamlit as st
from core.interaction.chat_handler import handle_chat_interaction


def display_person_state_compact(person):
    """Display current person state in compact form"""
    st.write("**Current State:**")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")


def handle_user_input(person, llm, memory_manager, debug_mode):
    """Handle user chat input and return result"""
    user_input = st.chat_input("Talk to Jenbina...")
    
    if user_input:
        print("User input:", user_input)
        
        # Store the user message in person's communication history
        person.receive_message("User", user_input, "text")
        
        # Get conversation history for context
        conversation_history = person.get_conversation_history("User", count=1000)
        recent_context = "\n".join([
            f"{msg.sender}: {msg.content}" 
            for msg in conversation_history
        ])
        
        # Handle chat interaction
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
            debug_mode=debug_mode
        )
        
        print(chat_result)
        
        # Store the person's response
        if "assistant_response" in chat_result:
            person.send_message("User", chat_result["assistant_response"], "text")
        
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
    with st.expander("Recent Conversation History", expanded=False):
        user_summary = person.get_conversation_summary("User")
        if user_summary['message_count'] > 0:
            st.write(f"**Messages with User:** {user_summary['message_count']}")
            st.write(f"**Last Interaction:** {user_summary['last_interaction'].strftime('%Y-%m-%d %H:%M')}")
            
            st.write("**Recent Messages:**")
            for msg in user_summary['recent_messages']:
                sender_icon = "👤" if msg['sender'] == "User" else "🤖"
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


def render_chat_interface(person, llm, memory_manager, debug_mode):
    """Render the complete chat interface"""
    st.write("**6. Interaction with User:**")
    st.write("### Chat with Jenbina")
    
    display_person_state_compact(person)
    handle_user_input(person, llm, memory_manager, debug_mode)
    display_communication_stats(person)
    display_conversation_history(person)
    display_memory_stats(memory_manager)
    
    if debug_mode:
        display_memory_debug(memory_manager)
