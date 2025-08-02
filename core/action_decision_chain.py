import json
from langchain.prompts import PromptTemplate
# Remove LLMChain import since we'll use invoke directly
from langchain.llms.base import BaseLLM
from typing import Dict, Any
from person import Person  # Import Person instead of BasicNeeds
from fix_llm_json import fix_llm_json


def create_action_decision_chain(llm: BaseLLM, person: Person, world_description) -> Dict[str, Any]:
    # Create prompt for action decision
    action_prompt = PromptTemplate(
        input_variables=["descriptions", "actions", "hunger_satisfaction", "sleep_satisfaction", "safety_satisfaction", "overall_satisfaction"],
        template="""Given the current situation and the person's needs, decide on the most appropriate action to take.

    Current Description:
    {descriptions}

    Available Actions:
    {actions}

    Person's Current Needs:
    - Hunger satisfaction: {hunger_satisfaction:.1f}%
    - Sleep satisfaction: {sleep_satisfaction:.1f}%
    - Safety satisfaction: {safety_satisfaction:.1f}%
    - Overall satisfaction: {overall_satisfaction:.1f}%

    Select one action from the available actions that best addresses the person's most pressing needs.
    Explain your reasoning for choosing this action.

    Respond in JSON format with:
    - chosen_action: the selected action
    - reasoning: brief explanation of why this action was chosen.
    """
    )

    # Remove LLMChain creation since we'll use invoke directly

    def process_action_decision(person: Person, world_description: str, llm: BaseLLM) -> Dict[str, Any]:
        """
        Process and decide the next action based on person's needs and world description.
        
        Args:
            person: Person object containing person's current needs
            world_description: JSON string containing world description and available actions
            llm: Language model instance
        
        Returns:
            Dict containing the chosen action and reasoning
        """
        
        # Parse the world description JSON to get lists
        description_data = json.loads(world_description)
        
        # Get individual need satisfaction levels from the Person's BasicNeeds
        basic_needs = person.needs[0]  # Person has a list of BasicNeeds objects
        hunger_satisfaction = basic_needs.needs.get('hunger', 50.0).satisfaction
        sleep_satisfaction = basic_needs.needs.get('sleep', 50.0).satisfaction
        safety_satisfaction = basic_needs.needs.get('safety', 50.0).satisfaction
        overall_satisfaction = basic_needs.get_overall_satisfaction()
        
        # Get decision using invoke directly
        response = llm.invoke(
            action_prompt.format(
                descriptions=description_data["list_of_descriptions"],
                actions=description_data["list_of_actions"],
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction
            )
        )
        
        # Extract content from the response
        action_decision = response.content if hasattr(response, 'content') else str(response)
        
        # Fix and parse the JSON response
        fixed_action_decision = fix_llm_json(broken_json=action_decision, llm_json_mode=llm)
        fixed_action_decision = json.dumps(fixed_action_decision, indent=2)
        
        return json.loads(fixed_action_decision)
    
    return process_action_decision(person=person, world_description=world_description, llm=llm)