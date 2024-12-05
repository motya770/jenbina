import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from typing import Dict, Any
from basic_needs import BasicNeeds  # Import instead of defining


def create_action_decision_chain(llm: BaseLLM, person: BasicNeeds, world_description: str) -> LLMChain:
    # Create prompt for action decision
    action_prompt = PromptTemplate(
        input_variables=["descriptions", "actions", "hunger_level", "energy_level", "comfort_level"],
        template="""Given the current situation and the person's needs, decide on the most appropriate action to take.

    Current Description:
    {descriptions}

    Available Actions:
    {actions}

    Person's Current Needs:
    - Hunger Level: {hunger_level}
    - Energy Level: {energy_level} 
    - Comfort Level: {comfort_level}

    Select one action from the available actions that best addresses the person's most pressing needs.
    Explain your reasoning for choosing this action.

    Respond in JSON format with:
    - chosen_action: the selected action
    - reasoning: brief explanation of why this action was chosen.
    """
    )

    action_decision_chain = LLMChain(
        llm=llm,
        prompt=action_prompt,
        verbose=True
    )

    def process_action_decision(person: BasicNeeds, world_description: str, llm: BaseLLM) -> Dict[str, Any]:
        """
        Process and decide the next action based on person's needs and world description.
        
        Args:
            person: BasicNeeds object containing person's current needs
            world_description: JSON string containing world description and available actions
            llm: Language model instance
        
        Returns:
            Dict containing the chosen action and reasoning
        """
        action_decision_chain = create_action_decision_chain(llm)
        
        # Parse the world description JSON to get lists
        description_data = json.loads(world_description)
        
        # Get decision from the chain
        action_decision = action_decision_chain.run(
            descriptions=description_data["list_of_descriptions"],
            actions=description_data["list_of_actions"],
            hunger_level=person.hunger,
            energy_level=person.energy,
            comfort_level=person.comfort
        )
        
        # Fix and parse the JSON response
        fixed_action_decision = fix_llm_json(action_decision)
        fixed_action_decision = json.dumps(fixed_action_decision, indent=2)
        
        return json.loads(fixed_action_decision)
    
    return process_action_decision(person=person, world_description=world_description, llm=action_decision_chain)