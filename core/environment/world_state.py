from dataclasses import dataclass
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from typing import List, Callable, Dict, Any, Optional
from ..needs.maslow_needs import BasicNeeds
from ..person.person import Person
from datetime import datetime
from .environment_simulator import EnvironmentSimulator, EnvironmentState, WeatherData, TimeData
from .location_system import PaloAltoLocationSystem, Location, Neighborhood
from .dynamic_events import DynamicEventsSystem, Event, Venue

@dataclass
class WorldState:
    last_descriptions: List[str] = None
    
    # Enhanced fields from integrated systems
    weather_data: Optional[WeatherData] = None
    time_data: Optional[TimeData] = None
    current_location_info: Optional[Location] = None
    nearby_locations: List[Location] = None
    open_locations: List[Location] = None
    current_events: List[Event] = None
    mood_factors: Dict[str, float] = None
    environment_description: str = ""
    
    def __post_init__(self):
        if self.last_descriptions is None:
            self.last_descriptions = []
        if self.nearby_locations is None:
            self.nearby_locations = []
        if self.open_locations is None:
            self.open_locations = []
        if self.current_events is None:
            self.current_events = []
        if self.mood_factors is None:
            self.mood_factors = {}
    
    def add_description(self, description: str):
        self.last_descriptions.append(description)
        # Keep last 5 descriptions for context
        if len(self.last_descriptions) > 5:
            self.last_descriptions.pop(0)

def create_comprehensive_world_state(
    person_location: str = "Jenbina's House",
    api_keys: Dict[str, str] = None
) -> WorldState:
    """
    Creates a comprehensive WorldState by integrating information from:
    - EnvironmentSimulator (weather, time, mood factors)
    - PaloAltoLocationSystem (locations, neighborhoods)
    - DynamicEventsSystem (events, venues)
    
    Args:
        person_location: The current location of the person
        api_keys: Optional API keys for real data fetching
        
    Returns:
        WorldState object with rich, integrated information
    """
    
    # Initialize all systems
    env_simulator = EnvironmentSimulator(location="Palo Alto, CA", api_keys=api_keys)
    location_system = PaloAltoLocationSystem()
    events_system = DynamicEventsSystem(api_keys=api_keys)
    
    # Get current time and environment data
    current_time = datetime.now()
    env_state = env_simulator.get_environment_state()
    
    # Get location information
    current_location = location_system.get_location(person_location)
    if current_location is None:
        # Fallback to a known location if the requested location is not found
        current_location = location_system.get_location("Jenbina's House")
    
    nearby_locations = location_system.get_nearby_locations(person_location, radius_km=5.0)
    open_locations = location_system.get_open_locations(current_time)
    
    # Get current events
    current_events = events_system.get_events(location="Palo Alto", date_range=1)
    
    # Create comprehensive world state
    world_state = WorldState(
        weather_data=env_state.weather,
        time_data=env_state.time,
        current_location_info=current_location,
        nearby_locations=nearby_locations,
        open_locations=open_locations,
        current_events=current_events,
        mood_factors=env_state.mood_factors,
        environment_description=env_simulator.get_environment_description()
    )
    
    return world_state

def get_world_state_summary(world_state: WorldState) -> Dict[str, Any]:
    """
    Get a comprehensive summary of the world state for display or processing.
    
    Args:
        world_state: The WorldState object
        
    Returns:
        Dictionary containing summary information
    """
    summary = {
        "location": {
            "name": world_state.current_location_info.name if world_state.current_location_info else "Unknown location",
            "description": world_state.current_location_info.description if world_state.current_location_info else "Unknown location",
            "type": world_state.current_location_info.type if world_state.current_location_info else "unknown",
            "features": world_state.current_location_info.features if world_state.current_location_info else []
        },
        "time": {
            "time_of_day": world_state.time_data.time_of_day,
            "day_of_week": world_state.time_data.day_of_week if world_state.time_data else "unknown",
            "is_daytime": world_state.time_data.is_daytime if world_state.time_data else True,
            "season": world_state.time_data.season if world_state.time_data else "unknown"
        },
        "weather": {
            "description": world_state.weather_data.description if world_state.weather_data else "Unknown",
            "temperature": world_state.weather_data.temperature if world_state.weather_data else 20.0,
            "humidity": world_state.weather_data.humidity if world_state.weather_data else 65.0,
            "wind_speed": world_state.weather_data.wind_speed if world_state.weather_data else 5.0
        },
        "environment": {
            "nearby_locations_count": len(world_state.nearby_locations),
            "open_locations_count": len(world_state.open_locations),
            "current_events_count": len(world_state.current_events),
            "mood_factors": world_state.mood_factors
        },
        "activities": {
            "nearby_locations": [
                {
                    "name": loc.name,
                    "type": loc.type,
                    "mood": loc.mood,
                    "popularity": loc.popularity
                } for loc in world_state.nearby_locations[:5]  # Top 5
            ],
            "open_locations": [
                {
                    "name": loc.name,
                    "type": loc.type,
                    "mood": loc.mood
                } for loc in world_state.open_locations[:5]  # Top 5
            ],
            "current_events": [
                {
                    "name": event.name,
                    "type": event.type,
                    "location": event.location,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "price": event.price
                } for event in world_state.current_events[:3]  # Top 3
            ]
        }
    }
    
    return summary

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
                location=world.current_location_info.name if world.current_location_info else "Unknown location",
                time_of_day=world.time_data.time_of_day if world.time_data else "unknown",
                weather=world.weather_data.description if world.weather_data else "unknown",
                last_descriptions="\n".join(world.last_descriptions),
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction
            )
        )
        
        return response.content

    return get_world_description