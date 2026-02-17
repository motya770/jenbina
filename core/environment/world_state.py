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
    current_neighborhood: Optional[Neighborhood] = None
    activity_suggestion: Optional[Dict] = None

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
    
    # Get neighborhood and activity suggestion
    neighborhood = location_system.get_neighborhood("Downtown Palo Alto")
    activity_suggestion = location_system.get_daily_activity_suggestion(current_time)

    # Get venue data from events system for richer environment description
    venues = events_system.get_venues()
    venue_descriptions = []
    for venue in venues[:3]:
        venue_descriptions.append(f"{venue.name} ({venue.type}) at {venue.address} — {venue.description}")

    # Build enriched environment description
    base_env_desc = env_simulator.get_environment_description()
    if venue_descriptions:
        base_env_desc += "\nNearby venues: " + "; ".join(venue_descriptions)
    if activity_suggestion:
        base_env_desc += f"\nSuggested activity: {activity_suggestion.get('activity', '')} — {activity_suggestion.get('reason', '')}"

    # Create comprehensive world state
    world_state = WorldState(
        weather_data=env_state.weather,
        time_data=env_state.time,
        current_location_info=current_location,
        nearby_locations=nearby_locations,
        open_locations=open_locations,
        current_events=current_events,
        mood_factors=env_state.mood_factors,
        environment_description=base_env_desc,
        current_neighborhood=neighborhood,
        activity_suggestion=activity_suggestion,
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
            "features": world_state.current_location_info.features if world_state.current_location_info else [],
            "address": world_state.current_location_info.address if world_state.current_location_info else "unknown",
            "mood": world_state.current_location_info.mood if world_state.current_location_info else "unknown",
        },
        "time": {
            "time_of_day": world_state.time_data.time_of_day,
            "day_of_week": world_state.time_data.day_of_week if world_state.time_data else "unknown",
            "is_daytime": world_state.time_data.is_daytime if world_state.time_data else True,
            "season": world_state.time_data.season if world_state.time_data else "unknown",
            "moon_phase": world_state.time_data.moon_phase if world_state.time_data else "unknown",
        },
        "weather": {
            "description": world_state.weather_data.description if world_state.weather_data else "Unknown",
            "temperature": world_state.weather_data.temperature if world_state.weather_data else 20.0,
            "humidity": world_state.weather_data.humidity if world_state.weather_data else 65.0,
            "wind_speed": world_state.weather_data.wind_speed if world_state.weather_data else 5.0,
            "visibility": world_state.weather_data.visibility if world_state.weather_data else 10.0,
            "sunrise": world_state.weather_data.sunrise if world_state.weather_data else "06:30",
            "sunset": world_state.weather_data.sunset if world_state.weather_data else "19:30",
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
                    "popularity": loc.popularity,
                    "description": loc.description,
                    "address": loc.address,
                    "features": loc.features,
                    "price_range": loc.price_range,
                } for loc in world_state.nearby_locations[:8]
            ],
            "open_locations": [
                {
                    "name": loc.name,
                    "type": loc.type,
                    "mood": loc.mood,
                    "description": loc.description,
                    "features": loc.features,
                } for loc in world_state.open_locations[:8]
            ],
            "current_events": [
                {
                    "name": event.name,
                    "type": event.type,
                    "description": event.description,
                    "location": event.location,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "end_time": event.end_time.isoformat() if event.end_time else None,
                    "price": event.price,
                    "popularity": event.popularity,
                } for event in world_state.current_events[:5]
            ]
        }
    }

    return summary

def _format_nearby_locations(world: 'WorldState') -> str:
    """Format nearby locations into a readable string for the prompt."""
    if not world.nearby_locations:
        return "No notable locations nearby."
    lines = []
    for loc in world.nearby_locations[:8]:
        features_str = ", ".join(loc.features[:4]) if loc.features else "no special features"
        lines.append(
            f"- {loc.name} ({loc.type}) — {loc.description[:80]}. "
            f"Mood: {loc.mood}, Features: {features_str}, Price: {loc.price_range}"
        )
    return "\n".join(lines)


def _format_open_locations(world: 'WorldState') -> str:
    """Format currently open locations into a readable string."""
    if not world.open_locations:
        return "Most places are closed right now."
    names = [f"{loc.name} ({loc.type}, {loc.mood})" for loc in world.open_locations[:8]]
    return ", ".join(names)


def _format_current_events(world: 'WorldState') -> str:
    """Format current events into a readable string."""
    if not world.current_events:
        return "No special events happening right now."
    lines = []
    for event in world.current_events[:5]:
        time_str = event.start_time.strftime("%H:%M") if event.start_time else "TBD"
        end_str = f" - {event.end_time.strftime('%H:%M')}" if event.end_time else ""
        lines.append(
            f"- {event.name} ({event.type}) at {event.location}, "
            f"{time_str}{end_str}, Price: {event.price or 'Free'} — {event.description[:80]}"
        )
    return "\n".join(lines)


def _format_location_details(world: 'WorldState') -> str:
    """Format current location details."""
    loc = world.current_location_info
    if not loc:
        return "Unknown location."
    features_str = ", ".join(loc.features) if loc.features else "none"
    return (
        f"Name: {loc.name}\n"
        f"Type: {loc.type}\n"
        f"Address: {loc.address}\n"
        f"Description: {loc.description}\n"
        f"Mood/Atmosphere: {loc.mood}\n"
        f"Features: {features_str}\n"
        f"Price range: {loc.price_range}"
    )


def _format_weather_details(world: 'WorldState') -> str:
    """Format detailed weather information."""
    w = world.weather_data
    if not w:
        return "Weather unknown."
    return (
        f"Conditions: {w.description}\n"
        f"Temperature: {w.temperature:.1f}°C\n"
        f"Humidity: {w.humidity:.0f}%\n"
        f"Wind: {w.wind_speed:.1f} km/h\n"
        f"Visibility: {w.visibility:.1f} km\n"
        f"Sunrise: {w.sunrise}, Sunset: {w.sunset}"
    )


def _format_time_details(world: 'WorldState') -> str:
    """Format detailed time information."""
    t = world.time_data
    if not t:
        return "Time unknown."
    return (
        f"Time of day: {t.time_of_day}\n"
        f"Day: {t.day_of_week}\n"
        f"Season: {t.season}\n"
        f"Daytime: {'yes' if t.is_daytime else 'no'}\n"
        f"Moon phase: {t.moon_phase}"
    )


def _format_mood_factors(world: 'WorldState') -> str:
    """Format environmental mood factors."""
    if not world.mood_factors:
        return "No mood data."
    return ", ".join(f"{k}: {v:.1f}" for k, v in world.mood_factors.items())


def create_world_description_system(llm: BaseLLM) -> Callable:
    """
    Creates and returns a function that generates world descriptions.

    Args:
        llm: Language model instance

    Returns:
        Callable that generates world descriptions
    """
    world_prompt = PromptTemplate(
        input_variables=[
            "location_details", "time_details", "weather_details",
            "nearby_locations", "open_locations", "current_events",
            "mood_factors", "environment_description",
            "last_descriptions", "recent_actions",
            "hunger_satisfaction", "sleep_satisfaction",
            "safety_satisfaction", "overall_satisfaction",
        ],
        template="""You are a vivid world narrator describing the environment around a person living in Palo Alto, California.
Describe ONLY the environment, surroundings, streets, and atmosphere. Omit the person's feelings and inner thoughts.

=== CURRENT LOCATION ===
{location_details}

=== TIME & DATE ===
{time_details}

=== WEATHER ===
{weather_details}

=== ENVIRONMENTAL MOOD ===
{mood_factors}

=== NEARBY PLACES (within walking/driving distance) ===
{nearby_locations}

=== CURRENTLY OPEN LOCATIONS ===
{open_locations}

=== EVENTS & ACTIVITIES HAPPENING NOW ===
{current_events}

=== ENVIRONMENT OVERVIEW ===
{environment_description}

=== PERSON'S NEEDS (for context — do NOT describe feelings, only reflect in available actions) ===
Hunger: {hunger_satisfaction:.1f}%  |  Sleep: {sleep_satisfaction:.1f}%  |  Safety: {safety_satisfaction:.1f}%  |  Overall: {overall_satisfaction:.1f}%

=== RECENT ACTIONS (most recent last) ===
{recent_actions}

=== PREVIOUS DESCRIPTIONS (maintain continuity) ===
{last_descriptions}

---

Generate a rich, immersive description of the world. Respond in JSON with these fields:

"list_of_descriptions": A list of 5-8 vivid description strings covering:
  - The immediate surroundings at the current location (what's visible, the space, objects)
  - Street life and neighborhood activity (people walking, traffic, shops, cafes)
  - Sensory details tied to weather and time (light quality, temperature feel, sounds, smells)
  - What's happening at nearby venues and streets (bustle at cafes, quiet parks, etc.)
  - Any notable events unfolding in the area
  - Seasonal and time-of-day atmosphere (morning fog, evening glow, winter chill)
  - Natural environment (sky, trees, birds, wind)

"list_of_actions": A list of 6-10 specific, concrete actions the person can take right now, based on:
  - What's currently open and accessible nearby
  - Events they could attend or activities they could join
  - Actions appropriate for the time of day, weather, and season
  - Walking to specific streets or neighborhoods
  - Visiting specific named locations with brief reason why
  - Indoor vs outdoor options based on weather
  - Actions that address their current need levels (e.g. if hungry, suggest specific nearby restaurants)

"reasoning": Brief explanation of why these descriptions and actions fit the current moment.

Keep descriptions coherent with previous ones. Reflect consequences of recent actions in the environment.
Each action should mention a SPECIFIC location or activity, not generic suggestions.
"""
    )

    def get_world_description(person: Person, world: WorldState, recent_actions: str = "None yet.") -> str:
        """
        Generate a coherent world description based on current state and person's needs.
        """
        maslow_needs = person.maslow_needs
        hunger_satisfaction = maslow_needs.get_need_satisfaction('hunger')
        sleep_satisfaction = maslow_needs.get_need_satisfaction('sleep')
        safety_satisfaction = maslow_needs.get_need_satisfaction('security')
        overall_satisfaction = maslow_needs.get_overall_satisfaction()

        response = llm.invoke(
            world_prompt.format(
                location_details=_format_location_details(world),
                time_details=_format_time_details(world),
                weather_details=_format_weather_details(world),
                nearby_locations=_format_nearby_locations(world),
                open_locations=_format_open_locations(world),
                current_events=_format_current_events(world),
                mood_factors=_format_mood_factors(world),
                environment_description=world.environment_description or "No additional context.",
                last_descriptions="\n".join(world.last_descriptions) if world.last_descriptions else "No previous descriptions.",
                recent_actions=recent_actions,
                hunger_satisfaction=hunger_satisfaction,
                sleep_satisfaction=sleep_satisfaction,
                safety_satisfaction=safety_satisfaction,
                overall_satisfaction=overall_satisfaction,
            )
        )

        return response.content

    return get_world_description