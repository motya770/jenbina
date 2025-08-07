import json
from langchain.prompts import PromptTemplate
# Remove LLMChain import since we'll use invoke directly
from langchain.llms.base import BaseLLM
from typing import Dict, Any, Optional
from ..person.person import Person  # Import Person instead of BasicNeeds
from ..fix_llm_json import fix_llm_json
from ..environment.world_state import WorldState


def create_action_decision_chain(llm: BaseLLM) -> callable:
    # Create prompt for action decision
    action_prompt = PromptTemplate(
        input_variables=["descriptions", "actions", "hunger_satisfaction", "sleep_satisfaction", "safety_satisfaction", "overall_satisfaction", "world_state_info"],
        template="""Given the current situation, the person's needs, and the world state, decide on the most appropriate action to take.

    Current Description:
    {descriptions}

    Available Actions:
    {actions}

    Person's Current Needs:
    - Hunger satisfaction: {hunger_satisfaction:.1f}%
    - Sleep satisfaction: {sleep_satisfaction:.1f}%
    - Safety satisfaction: {safety_satisfaction:.1f}%
    - Overall satisfaction: {overall_satisfaction:.1f}%

    World State Information:
    {world_state_info}

    Consider the world state information when making your decision. This includes:
    - Current weather and time conditions
    - Available nearby locations and events
    - Environmental mood factors
    - What locations are currently open

    Select one action from the available actions that best addresses the person's most pressing needs while considering the current world state.
    Explain your reasoning for choosing this action, including how the world state influenced your decision.

    Respond in JSON format with:
    - chosen_action: the selected action
    - reasoning: brief explanation of why this action was chosen, including world state considerations
    - world_state_influence: how the world state specifically influenced this decision
    """
    )

    def process_action_decision(person: Person, world_description: str, llm: BaseLLM, world_state: Optional[WorldState] = None) -> Dict[str, Any]:
        """
        Process and decide the next action based on person's needs, world description, and world state.
        
        Args:
            person: Person object containing person's current needs
            world_description: JSON string containing world description and available actions
            llm: Language model instance
            world_state: Optional WorldState object containing rich world information
        
        Returns:
            Dict containing the chosen action and reasoning
        """
        
        # Parse the world description JSON to get lists
        description_data = json.loads(world_description)
        
        # Get individual need satisfaction levels from the Person's MaslowNeedsSystem
        maslow_needs = person.maslow_needs
        hunger_satisfaction = maslow_needs.get_need_satisfaction('hunger')
        sleep_satisfaction = maslow_needs.get_need_satisfaction('sleep')
        safety_satisfaction = maslow_needs.get_need_satisfaction('security')
        overall_satisfaction = maslow_needs.get_overall_satisfaction()
        
        # Prepare world state information
        world_state_info = "No world state information available."
        if world_state:
            world_state_info = f"""
            Location: {world_state.current_location_info.name if world_state.current_location_info else 'Unknown location'}
            Time: {world_state.time_data.time_of_day if world_state.time_data else 'unknown'} ({world_state.time_data.day_of_week if world_state.time_data else 'unknown'})
            Weather: {world_state.weather_data.description if world_state.weather_data else 'unknown'} (Temperature: {world_state.weather_data.temperature if world_state.weather_data else 'unknown'}°C)
            
            Nearby Locations ({len(world_state.nearby_locations)}):
            {chr(10).join([f"- {loc.name} ({loc.type}, {loc.mood} mood)" for loc in world_state.nearby_locations[:5]])}
            
            Open Locations ({len(world_state.open_locations)}):
            {chr(10).join([f"- {loc.name} ({loc.type})" for loc in world_state.open_locations[:5]])}
            
            Current Events ({len(world_state.current_events)}):
            {chr(10).join([f"- {event.name} at {event.location} ({event.price})" for event in world_state.current_events[:3]])}
            
            Mood Factors:
            {chr(10).join([f"- {factor}: {value:.2f}" for factor, value in world_state.mood_factors.items()])}
            """
        
        # Get decision using invoke directly
        response = llm.invoke(
            action_prompt.format(
                descriptions=description_data["list_of_descriptions"],
                actions=description_data["list_of_actions"],
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction,
                world_state_info=world_state_info
            )
        )
        
        # Extract content from the response
        action_decision = response.content if hasattr(response, 'content') else str(response)
        
        # Fix and parse the JSON response
        fixed_action_decision = fix_llm_json(broken_json=action_decision, llm_json_mode=llm)
        fixed_action_decision = json.dumps(fixed_action_decision, indent=2)
        
        return json.loads(fixed_action_decision)
    
    return process_action_decision