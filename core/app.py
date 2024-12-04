import streamlit as st
from datetime import datetime
 # Import your other components
from action_decision_chain import create_action_decision_chain
from basic_needs import BasicNeeds
from asimov_check_chain import create_asimov_check_system 
from state_analysis_chain import create_state_analysis_system

# Initialize LLM
import os
from langchain_ollama import Ollama

### LLM
from langchain_ollama import ChatOllama
local_llm = 'llama3.2:3b-instruct-fp16'
llm = ChatOllama(model=local_llm, temperature=0)
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')


# Initialize session state for person's state if not already done
if 'person' not in st.session_state:
    st.session_state.person = person
    st.session_state.action_history = []

st.title("Conversation with Jenbina")

# Create columns for the interface layout
col1, col2 = st.columns([2, 1])

with col1:
    # Dialog interface
    st.subheader("Conversation")
    user_input = st.text_input("Your message to Jenbina:", key="user_input")
    if st.button("Send"):
        if user_input:
            st.session_state.action_history.append({"role": "user", "content": user_input})
            # Display the conversation history
            for message in st.session_state.action_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

with col2:
    # Internal state visualization
    st.subheader("Jenbina's Internal State")
    st.write("Current Emotional State:", st.session_state.person.emotional_state)
    st.write("Decision Making Process:")
    
    # Display the reasoning chain
    if st.session_state.action_history:
        with st.expander("Latest Decision Chain", expanded=True):
            chain = state_analysis_chain(st.session_state.person)
            st.write(chain)
            
    # Display Asimov compliance status
    compliance_status = check_asimov_compliance(st.session_state.person)
    st.metric("Asimov Compliance", value=f"{compliance_status}%")


