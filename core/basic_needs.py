
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dataclasses import dataclass
from typing import Dict
import random


@dataclass
class BasicNeeds:
    hunger: float = 100.0  # 100 is full, 0 is starving
    
    def update_needs(self):
        # Simulate hunger decreasing over time
        self.hunger = max(0, self.hunger - random.uniform(5, 15))
        
    def satisfy_hunger(self, amount: float):
        self.hunger = min(100, self.hunger + amount)

def create_basic_needs_chain(llm_json_mode, person: BasicNeeds):
    # Prompt template for decision making based on needs
    needs_prompt = PromptTemplate(
        input_variables=["hunger_level"],
        template="""You are an AI making decisions based on basic needs.
    Current hunger level: {hunger_level}/100 (100 is full, 0 is starving)

    Based on this hunger level, what action should be taken? 
    Respond in JSON format with two fields:
    - action: what to do (eat, find_food, or continue_activities)
    - reasoning: brief explanation why

    Consider:
    - Below 30: Critical need to find food
    - 30-60: Should consider eating soon
    - Above 60: Can continue other activities"""
    )

    # Create the chain for decision making
    needs_chain = LLMChain(
        llm=llm_json_mode,
        prompt=needs_prompt,
        verbose=True
    )

    response = needs_chain.run(hunger_level=person.hunger)
    print(f"Current state: {person.hunger}")
    print(f"AI Decision: {response}")
    return response
    
