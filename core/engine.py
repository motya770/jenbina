from .needs.maslow_needs import BasicNeeds
from .environment.world_state import WorldState, create_world_description_system
from .cognition.action_decision_chain import process_action_decision
from .cognition.asimov_check_chain import create_asimov_check_system
from .cognition.state_analysis_chain import create_state_analysis_system
from .person.person import Person
from .connect import get_llm, get_json_llm


def run_simulation():

    ### LLM - Using ChatGPT as default (switch to "ollama" for local)
    # Options: "openai" (default), "openai-advanced", "ollama", "sambanova"
    llm = get_llm(provider="openai", temperature=0)
    llm_json_mode = get_json_llm(provider="openai", temperature=0)

    # Initialize person and world state
    person = Person()
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
            person.update_all_needs()

        # TODO remove 
        break
