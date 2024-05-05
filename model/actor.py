from memory import Memory

class Actor:
    def __init__(self, name):
        self.name = name
        self.energy = 100  # initialize energy to 100%
        self.curiousity = 100 # initialize curiousity to 100%
        self.memory = Memory()

    def eat(self, food):
        """Restore some of the actor's energy"""
        if isinstance(food, str):  # assume 'food' is a string representing a snack
            energy_restored = int(food[:-1])  # extract the numeric value from the string (e.g. "20cookies")
            self.energy += energy_restored
            if self.energy > 100:  # prevent energy from exceeding 100%
                self.energy = 100
        else:
            print(f"{self.name} can't eat {type(food)}")

    def discover(self, item):
        # reduce curiousity by 10% when discovering an item
        self.curiousity -= 10
        print(f"{self.name} discovered {item}")

    def __str__(self):
        return f"{self.name} has {self.energy}% energy remaining"    