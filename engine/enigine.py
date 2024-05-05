from model.actor import Actor


class Engine: 
    def __init__(self, actor, memory):
        self.actor = Actor(name="Scarlett")
    
    def run(self):

        # simulate a single day
        self.actor.eat("20cookies")
        self.actor.discover("a hidden treasure")
        print(self.actor)
        print(self.memory)

    def llm_neocortext():
        pass

    def llm_world():
        pass
