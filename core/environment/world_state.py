from dataclasses import dataclass
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from typing import List, Callable
from ..needs.maslow_needs import BasicNeeds
from ..person.person import Person

@dataclass
class WorldState:
    location: str = "Small house in a Moldovan village"
    time_of_day: str = "morning"
    weather: str = "sunny"
    last_descriptions: List[str] = None
    
    def __post_init__(self):
        if self.last_descriptions is None:
            self.last_descriptions = []
    
    def add_description(self, description: str):
        self.last_descriptions.append(description)
        # Keep last 5 descriptions for context
        if len(self.last_descriptions) > 5:
            self.last_descriptions.pop(0)

def create_world_description_system(llm: BaseLLM) -> Callable:
    """
    Creates and returns a function that generates world descriptions.
    
    Args:
        llm: Language model instance
    
    Returns:
        Callable that generates world descriptions
    """
    world_prompt = PromptTemplate(
        input_variables=["location", "time_of_day", "weather", "last_descriptions", "hunger_satisfaction", "sleep_satisfaction", "safety_satisfaction", "overall_satisfaction"],
        template="""You are describing a world where a person lives in {location}. Ommit person feelings and thoughts.  
        it is only describtion of environment and surroundings.
    Current time: {time_of_day}
    Weather: {weather}
    Hunger satisfaction: {hunger_satisfaction:.1f}%
    Sleep satisfaction: {sleep_satisfaction:.1f}%
    Safety satisfaction: {safety_satisfaction:.1f}%
    Overall satisfaction: {overall_satisfaction:.1f}%

    Previous context:
    {last_descriptions}

    Describe the current situation and surroundings in two lists maintaining consistency with previous descriptions. :
    - list_of_descriptions: list of descriptions
    - list_of_actions: list of available actions
    The lists should be in JSON format.
    The list_of_descriptions can include following details:
    - The immediate environment (house, room, etc.)
    - Sensory details (smells, sounds, temperature)
    - Available resources or items nearby
    - Cultural context of the Moldovan village setting

    The list_of_actions should include available actions that can be taken by the person
    Keep the description coherent with previous ones and consider the person's current needs.

    Respond in JSON format with two fields:
    - list_of_descriptions: list of descriptions
    - list_of_actions: list of available actions
    - reasoning: brief explanation why
    """
    )

    def get_world_description(person: Person, world: WorldState) -> str:
        """
        Generate a coherent world description based on current state and person's needs.
        
        Args:
            person: Person object containing person's current needs
            world: WorldState object containing current world state
            
        Returns:
            String containing the world description
        """
        # Get individual need satisfaction levels from the Person's MaslowNeedsSystem
        maslow_needs = person.maslow_needs
        hunger_satisfaction = maslow_needs.get_need_satisfaction('hunger')
        sleep_satisfaction = maslow_needs.get_need_satisfaction('sleep')
        safety_satisfaction = maslow_needs.get_need_satisfaction('security')
        overall_satisfaction = maslow_needs.get_overall_satisfaction()
        
        # Use invoke directly instead of LLMChain.run
        response = llm.invoke(
            world_prompt.format(
                location=world.location,
                time_of_day=world.time_of_day,
                weather=world.weather,
                last_descriptions="\n".join(world.last_descriptions),
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction
            )
        )
        
        return response.content

    return get_world_description