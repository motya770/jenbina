from maslow_needs import BasicNeeds
from world_state import WorldState, create_world_description_system
from action_decision_chain import process_action_decision
from asimov_check_chain import create_asimov_check_system
from state_analysis_chain import create_state_analysis_system
from langchain_ollama import ChatOllama


def run_simulation():

    ### LLM
    local_llm = 'llama3.2:3b-instruct-fp16'
    llm = ChatOllama(model=local_llm, temperature=0)
    llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')

    # Initialize basic needs and world state
    person = BasicNeeds()
    world = WorldState()
    
    # Create system components
    world_description_system = create_world_description_system(llm)
    asimov_check_system = create_asimov_check_system(llm)
    state_analysis_system = create_state_analysis_system(llm)
    
    # Main simulation loop
    while True:
        # Get world description
        world_description = world_description_system(person, world)
        
        # Decide on action
        action_decision = process_action_decision(person, world_description, llm)
        
        # Check if action complies with Asimov's Laws
        compliance_check = asimov_check_system(action_decision["chosen_action"])
        
        # Analyze state changes if action is compliant
        state_changes = state_analysis_system(
            action_decision["chosen_action"], 
            compliance_check
        )
        
        # Update person's state if changes were analyzed
        if state_changes:
            person.update_needs(state_changes)

        # TODO remove 
        break
