from langchain.prompts import PromptTemplate
from dataclasses import dataclass
from typing import Dict
import random


@dataclass
class Need:
    """Represents a single need with its current satisfaction level"""
    name: str
    satisfaction: float = 100.0  # 100 is fully satisfied, 0 is critical
    decay_rate: float = 10.0  # How much satisfaction decreases per update
    
    def update(self):
        """Decrease satisfaction over time"""
        self.satisfaction = max(0, self.satisfaction - random.uniform(0.5 * self.decay_rate, 1.5 * self.decay_rate))
        
    def satisfy(self, amount: float):
        """Increase satisfaction by given amount"""
        self.satisfaction = min(100, self.satisfaction + amount)
        
    def is_critical(self) -> bool:
        """Check if need is critically low (below 20)"""
        return self.satisfaction < 20
        
    def is_low(self) -> bool:
        """Check if need is low (below 50)"""
        return self.satisfaction < 50


@dataclass
class BasicNeeds:
    """Container for all basic needs with overall satisfaction tracking"""
    needs: Dict[str, Need] = None
    
    def __post_init__(self):
        if self.needs is None:
            self.needs = {
                'hunger': Need('hunger', 100.0, 8.0),
                'sleep': Need('sleep', 100.0, 6.0),
                'safety': Need('safety', 100.0, 3.0)
            }
    
    def update_needs(self):
        """Update all needs (decrease satisfaction over time)"""
        for need in self.needs.values():
            need.update()
    
    def satisfy_need(self, need_name: str, amount: float):
        """Satisfy a specific need"""
        if need_name in self.needs:
            self.needs[need_name].satisfy(amount)
        else:
            raise ValueError(f"Unknown need: {need_name}")
    
    def get_need_satisfaction(self, need_name: str) -> float:
        """Get satisfaction level for a specific need"""
        return self.needs.get(need_name, Need(need_name, 0.0)).satisfaction
    
    def get_overall_satisfaction(self) -> float:
        """Calculate overall satisfaction percentage across all needs"""
        if not self.needs:
            return 0.0
        total_satisfaction = sum(need.satisfaction for need in self.needs.values())
        return total_satisfaction / len(self.needs)
    
    def get_critical_needs(self) -> list:
        """Get list of needs that are critically low"""
        return [need.name for need in self.needs.values() if need.is_critical()]
    
    def get_low_needs(self) -> list:
        """Get list of needs that are low"""
        return [need.name for need in self.needs.values() if need.is_low()]
    
    def add_need(self, name: str, initial_satisfaction: float = 100.0, decay_rate: float = 10.0):
        """Add a new need to the system"""
        self.needs[name] = Need(name, initial_satisfaction, decay_rate)
    
    def remove_need(self, name: str):
        """Remove a need from the system"""
        if name in self.needs:
            del self.needs[name]
    
    def __str__(self):
        needs_str = ", ".join([f"{name}: {need.satisfaction:.1f}" for name, need in self.needs.items()])
        return f"BasicNeeds(overall: {self.get_overall_satisfaction():.1f}%, {needs_str})"


def create_basic_needs_chain(llm_json_mode, person: BasicNeeds):
    # Prompt template for decision making based on needs
    needs_prompt = PromptTemplate(
        input_variables=["needs_status", "overall_satisfaction", "critical_needs", "low_needs"],
        template="""You are an AI making decisions based on basic needs.
    
Current needs status: {needs_status}
Overall satisfaction: {overall_satisfaction:.1f}%
Critical needs (below 20%): {critical_needs}
Low needs (below 50%): {low_needs}

Based on these needs, what action should be taken? 
Respond in JSON format with two fields:
- action: what to do (eat, sleep, find_safety, find_food, rest, or continue_activities)
- reasoning: brief explanation why

Consider:
- Critical needs (below 20%): Immediate action required
- Low needs (below 50%): Should address soon
- Above 50%: Can continue other activities
- Prioritize the most critical needs first"""
    )

    # Prepare the needs status string
    needs_status = ", ".join([f"{name}: {need.satisfaction:.1f}%" for name, need in person.needs.items()])
    
    # Use the newer invoke method instead of run
    response = llm_json_mode.invoke(
        needs_prompt.format(
            needs_status=needs_status,
            overall_satisfaction=person.get_overall_satisfaction(),
            critical_needs=person.get_critical_needs(),
            low_needs=person.get_low_needs()
        )
    )
    
    # Extract content from the response
    response_content = response.content if hasattr(response, 'content') else str(response)
    
    print(f"Current state: {person}")
    print(f"AI Decision: {response_content}")
    return response_content
    
