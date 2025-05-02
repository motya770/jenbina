from actor import Actor
from openai import OpenAI
from threading import Thread
import instructor
from pydantic import BaseModel


class WorldInfo(instructor.OpenAISchema):
    location: str
    actions: list
    person: str
    date: str


class Engine: 
    def __init__(self):
        self.actor = Actor(name="Jennifer")
        self.client = instructor.from_openai(OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio"))

    def run(self):
        while True:
            print("Engine is running...")
            world = self.llm_world()    
            print(world)
            break
            # neocortex = self.llm_neocortex(self.actor, world)
            # print(neocortex)
            # Thread.sleep(1)


    def llm_neocortex(self, actor: Actor, world: str):
        completion = self.client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            
            messages=[
                {"role": "system", "content": """You are part of the brain known as neocortex 
                - you will translate desires and motivations of the agent into 
                actions that are going to be available for you from environment.
                You are going to communicate with environment - 
                the description of your surroundings are going to be provided.
                Also you will communicate with another human. Stop generating after 100 words. """},
                {"role": "user", "content": "Agent status:  Enviromement: "}
            ],
            temperature=0.7,
        )

        print(completion.choices[0].message)
        return completion.choices[0].message

    def llm_world(self):
        world_info = self.client.chat.completions.create(
            model="TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF",
            response_model = WorldInfo,
            
            messages=[
                {"role": "system", "content": """ 
                You are representation of the world for third party. You describe how enviroment looks around you and
                provide information about actions that are available
                Also you can generate description of roads, food, restaurants,
                city - everything that we see in everyday live.
                You return response to user in following json format: 
                {'location': current location, 'actions': [list of actions that this agent can do], 
                person: 'name of the person if it exists in the system', date: current date and time} 
                  """},
                {"role": "user", "content": "Where am I?"}
            ],
            temperature=0.7,
        )

        print(WorldInfo.from_response(world_info,  mode=instructor.Mode.JSON, strict=False))

        # print(completion.choices[0].message)
        # return completion.choices[0].message


if __name__ == "__main__":
    engine = Engine()   
    engine.run()