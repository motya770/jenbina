import streamlit as st
from datetime import datetime
 # Import your other components
from action_decision_chain import create_action_decision_chain
from basic_needs import BasicNeeds, create_basic_needs_chain
from asimov_check_chain import create_asimov_check_system
from state_analysis_chain import create_state_analysis_system
from world_state import WorldState, create_world_description_system
from chat_handler import handle_chat_interaction
from person import Person
from meta_cognition import MetaCognitiveSystem
from enhanced_action_decision_chain import create_meta_cognitive_action_chain
from conversation_memory import ChromaMemoryManager

# Initialize LLM
import os

# os.environ['OLLAMA_HOST'] = 'http://129.153.140.217:11434'
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

os.environ['LANGSMITH_TRACING'] = 'true'
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY'] = "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"
os.environ['LANGSMITH_PROJECT'] = "jenbina"


### LLM
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage
local_llm = 'llama3.2:3b-instruct-fp16'

# os.environ['OLLAMA_HOST'] = 'https://api.sambanova.ai/v1'
llm = ChatOllama(model=local_llm, temperature=0)
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')

# Example usage
person = Person()
person.update_all_needs()
print(person)

# Initialize meta-cognitive system
meta_cognitive_system = MetaCognitiveSystem(llm_json_mode)

# Initialize memory manager
memory_manager = ChromaMemoryManager()

# Initialize session state for meta-cognition
if 'meta_cognitive_system' not in st.session_state:
    st.session_state.meta_cognitive_system = meta_cognitive_system

# Initialize session state for memory manager
if 'memory_manager' not in st.session_state:
    st.session_state.memory_manager = memory_manager

# Initialize session state for person's state if not already done
if 'person' not in st.session_state:
    st.session_state.person = person
    st.session_state.action_history = []

st.title("Jenbina:")

# Create columns for the interface layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("System Stages and Responses")
    
    # Initialize states if not already done
    if 'simulation_completed' not in st.session_state:
        st.session_state.simulation_completed = False
        st.session_state.needs_response = None
        st.session_state.world_description = None
        st.session_state.action_decision = None
        st.session_state.state_response = None

    if st.button("Start simulation"):
        # Display all stages
        st.write("### Processing Stages:")
        st.write("### Current Jenbina State:")
        st.write(f"- State: {str(person)}")
        
        # Basic needs analysis
        st.write("**1. Basic Needs Analysis:**")
        st.session_state.needs_response = create_basic_needs_chain(llm_json_mode=llm_json_mode, person=person.needs[0])
        st.write(st.session_state.needs_response)

        # World state and description
        st.write("**2. World State:**")
        world = WorldState()
        st.write(world)

        st.write("**2.1 World Description:**")
        st.session_state.world_description = create_world_description_system(llm=llm_json_mode, person=person, world=world)
        st.write(st.session_state.world_description)

        # Enhanced action decision with meta-cognition
        st.write("**3. Action Decision (with Meta-Cognition):**")
        st.session_state.action_decision = create_meta_cognitive_action_chain(
            llm=llm_json_mode, 
            person=person, 
            world_description=st.session_state.world_description,
            meta_cognitive_system=st.session_state.meta_cognitive_system
        )
        st.write(st.session_state.action_decision)
        
        # Display meta-cognitive insights
        with st.expander("Meta-Cognitive Insights", expanded=False):
            meta_stats = st.session_state.meta_cognitive_system.get_meta_cognitive_stats()
            st.write(f"**Total Cognitive Processes:** {meta_stats['total_processes']}")
            st.write(f"**Total Insights:** {meta_stats['total_insights']}")
            
            st.write("**Cognitive Biases Detected:**")
            for bias, level in meta_stats['cognitive_biases'].items():
                if level > 0:
                    st.write(f"- {bias}: {level:.2f}")
            
            if meta_stats['recent_insights']:
                st.write("**Recent Insights:**")
                for insight in meta_stats['recent_insights']:
                    st.write(f"- **{insight['type']}**: {insight['description']}")

        # Asimov compliance check
        st.write("**5. Asimov Compliance Check:**")
        asimov_response = create_asimov_check_system(llm=llm_json_mode, action=st.session_state.action_decision)
        st.write(asimov_response)

        # State analysis
        st.write("**4. State Analysis:**") 
        st.session_state.state_response = create_state_analysis_system(llm=llm_json_mode, action_decision=st.session_state.action_decision, compliance_check=asimov_response)
        st.write(st.session_state.state_response)

        # Mark simulation as completed
        st.session_state.simulation_completed = True

    # Only show chat interface after simulation is completed
    if st.session_state.simulation_completed:
        st.write("**6. Interaction with User:**")
        st.write("### Chat with Jenbina")
        
        # Display current person state
        st.write(f"**Current State:** {person}")
        
        user_input = st.chat_input("Talk to Jenbina...")
        
        if user_input:
            print("User input:", user_input)
            
            # Store the user message in person's communication history
            person.receive_message("User", user_input, "text")
            
            # Get conversation history for context
            conversation_history = person.get_conversation_history("User", count=5)
            recent_context = "\n".join([
                f"{msg.sender}: {msg.content}" 
                for msg in conversation_history[-3:]  # Last 3 messages for context
            ])
            
            # Handle chat interaction using stored session state values and person's state
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
                memory_manager=st.session_state.memory_manager
            )
            
            print(chat_result)

            # Store the person's response in communication history
            if "assistant_response" in chat_result:
                person.send_message("User", chat_result["assistant_response"], "text")

            # Add interactions to history
            if "user_message" in chat_result:
                st.session_state.action_history.append({
                    "role": "user",
                    "content": chat_result["user_message"]
                })
            st.session_state.action_history.append({
                "role": "assistant",
                "content": chat_result["assistant_response"]
            })
        
        # Display communication statistics
        with st.expander("Communication Statistics", expanded=False):
            comm_stats = person.get_communication_stats()
            st.write(f"**Total Conversations:** {comm_stats['total_conversations']}")
            st.write(f"**Total Messages:** {comm_stats['total_messages']}")
            
            if comm_stats['most_active_conversations']:
                st.write("**Most Active Conversations:**")
                for conv in comm_stats['most_active_conversations']:
                    st.write(f"- {conv['outsider']}: {conv['message_count']} messages")
        
        # Display recent conversation history
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
        
        # Display memory system statistics
        with st.expander("Memory System Statistics", expanded=False):
            memory_stats = st.session_state.memory_manager.get_memory_stats()
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

# with col2:
#     # Internal state visualization
#     st.subheader("Jenbina's Internal State")
#     st.write("Current Emotional State:", st.session_state.person.emotional_state)
#     st.write("Decision Making Process:")
    
#     # Display the reasoning chain
#     if st.session_state.action_history:
#         with st.expander("Latest Decision Chain", expanded=True):
#             chain = state_analysis_chain(st.session_state.person)
#             st.write(chain)
            
#     # Display Asimov compliance status
#     compliance_status = check_asimov_compliance(st.session_state.person)
#     st.metric("Asimov Compliance", value=f"{compliance_status}%")


