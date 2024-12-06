import streamlit as st
from datetime import datetime
 # Import your other components
from action_decision_chain import create_action_decision_chain
from basic_needs import BasicNeeds, create_basic_needs_chain
from asimov_check_chain import create_asimov_check_system 
from state_analysis_chain import create_state_analysis_system
from world_state import WorldState, create_world_description_system

# Initialize LLM
import os

### LLM
from langchain_ollama import ChatOllama
local_llm = 'llama3.2:3b-instruct-fp16'
llm = ChatOllama(model=local_llm, temperature=0)
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')

# Example usage
person = BasicNeeds()
person.update_needs()  

# Initialize session state for person's state if not already done
if 'person' not in st.session_state:
    st.session_state.person = person
    st.session_state.action_history = []

st.title("Conversation with Jenbina")

# Create columns for the interface layout
col1, col2 = st.columns([2, 1])

with col1:
    # Display all stages and responses
    st.subheader("System Stages and Responses")
    user_input = st.text_input("Your message to Jenbina:", key="user_input")
    if st.button("Send"):
        if user_input:
            # Add user input to history
            st.session_state.action_history.append({"role": "user", "content": user_input})
            
            # Display all stages
            st.write("### Processing Stages:")

            # Simulate time passing
            
            # Basic needs analysis
            st.write("**1. Basic Needs Analysis:**")
            needs_response = create_basic_needs_chain(llm_json_mode=llm_json_mode, person=person)
            st.write(needs_response)


            # World state
            st.write("**2. World State:**")
            world = WorldState()

            # World description
            st.write("**2. World Description:**")
            world_description = create_world_description_system(llm=llm_json_mode, person=person, world=world)
            st.write(world_description)


            # Action decision
            st.write("**3. Action Decision:**")
            action_decision = create_action_decision_chain(llm=llm_json_mode, person=person, world_description=world_description)
            st.write(action_decision)

            
            # Asimov compliance check
            st.write("**5. Asimov Compliance Check:**")
            asimov_response = create_asimov_check_system(llm=llm_json_mode, action=action_decision)
            st.write(asimov_response)

            # State analysis
            st.write("**4. State Analysis:**") 
            state_response = create_state_analysis_system(llm=llm_json_mode, action=action_decision, asimov=asimov_response)
            st.write(state_response)
            
            
            # Add system response to history
            st.session_state.action_history.append({"role": "assistant", "content": action_decision})

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


