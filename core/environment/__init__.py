"""
Environment and World Simulation Submodule

This submodule handles all aspects of the AI's environment and world simulation, including:
- Environment simulation and state management
- World state representation
- Location systems and exploration
- Dynamic events and activities
"""

from .environment_simulator import (
    EnvironmentSimulator,
    EnvironmentState,
    WeatherData,
    TimeData
)

from .world_state import (
    WorldState,
    create_world_description_system
)

from .location_system import (
    PaloAltoLocationSystem,
    Location,
    Neighborhood
)

from .dynamic_events import (
    DynamicEventsSystem,
    Event,
    Venue
)

__all__ = [
    # Environment simulation
    'EnvironmentSimulator',
    'EnvironmentState',
    'WeatherData',
    'TimeData',
    
    # World state
    'WorldState',
    'create_world_description_system',
    
    # Location system
    'PaloAltoLocationSystem',
    'Location',
    'Neighborhood',
    
    # Dynamic events
    'DynamicEventsSystem',
    'Event',
    'Venue'
] 