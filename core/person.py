from dataclasses import dataclass
from typing import List
from basic_needs import BasicNeeds


@dataclass
class Person:
    name: str = "Jenbina"
    needs: List[BasicNeeds] = None
    
    def __post_init__(self):
        if self.needs is None:
            self.needs = [BasicNeeds()]
    
    def update_all_needs(self):
        """Update all needs for this person"""
        for need in self.needs:
            need.update_needs()
    
    def get_current_state(self):
        """Get a summary of the person's current state"""
        state = {"name": self.name, "needs": []}
        for need in self.needs:
            state["needs"].append(str(need))
        return state
    
    def __str__(self):
        needs_str = ", ".join([str(need) for need in self.needs])
        return f"Person(name={self.name}, needs=[{needs_str}])"
