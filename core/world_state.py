# World state and description management
@dataclass
class WorldState:
    location: str = "Small house in a Moldovan village"
    time_of_day: str = "morning"
    weather: str = "sunny"
    last_descriptions: list = None
    
    def __post_init__(self):
        if self.last_descriptions is None:
            self.last_descriptions = []
    
    def add_description(self, description: str):
        self.last_descriptions.append(description)
        # Keep last 5 descriptions for context
        if len(self.last_descriptions) > 5:
            self.last_descriptions.pop(0)

# Prompt template for world description
world_prompt = PromptTemplate(
    input_variables=["location", "time_of_day", "weather", "last_descriptions", "hunger_level"],
    template="""You are describing a world where a person lives in {location}. Ommit person feelings and thoughts.  
    it is only describtion of environment and surroundings.
Current time: {time_of_day}
Weather: {weather}
Hunger Level: {hunger_level}/100

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

# Create the chain for world description
world_description_chain = LLMChain(
    llm=llm,
    prompt=world_prompt,
    verbose=True
)

# Initialize world state
world = WorldState()

# Example of generating coherent world description
def get_world_description(person: BasicNeeds, world: WorldState) -> str:
    description = world_description_chain.run(
        location=world.location,
        time_of_day=world.time_of_day,
        weather=world.weather,
        last_descriptions="\n".join(world.last_descriptions),
        hunger_level=person.hunger
    )
    world.add_description(description)
    return description

description = get_world_description(person, world)
print(description)