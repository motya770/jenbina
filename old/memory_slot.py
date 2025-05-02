from enum import Enum


class MemorySlot: 
    def __init__(self, name, date, actions, persons, location):
        self.name = name
        self.date = date
        self.actions = actions
        self.persons = persons
        self.location = location

class ActionType(Enum):
    WORK = 1
    LEISURE = 2
    SLEEP = 3
    EAT = 4
    EXERCISE = 5
    SOCIALIZE = 6
    LEARN = 7
    ADAPT = 8 


class Person: 
    def __init__(self) -> None:
        self.age = None
        self.name = None

class Action: 
    def __init__(self) -> None:
        self.action = None
        self.action_type: ActionType = None
        self.time = None

