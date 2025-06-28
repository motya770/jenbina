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

        # Action decision
        st.write("**3. Action Decision:**")
        st.session_state.action_decision = create_action_decision_chain(llm=llm_json_mode, person=person, world_description=st.session_state.world_description)
        st.write(st.session_state.action_decision)
        
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
        
        user_input = st.chat_input("Talk to Jenbina...")
        
        if user_input:
            print("User input:", user_input)
            
            # Handle chat interaction using stored session state values
            chat_result = handle_chat_interaction(
                st=st,
                llm=llm,
                needs_response=st.session_state.needs_response,
                world_description=st.session_state.world_description,
                action_decision=st.session_state.action_decision,
                state_response=st.session_state.state_response,
                user_input=user_input
            )
            
            print(chat_result)

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


