from model.actor import Actor
from openai import OpenAI

class Engine: 
    def __init__(self, actor, memory):
        self.actor = Actor(name="Scarlett")
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    
    def run(self):

        # simulate a single day
        self.actor.eat("20cookies")
        self.actor.discover("a hidden treasure")
        print(self.actor)
        print(self.memory)

    def llm_neocortex(self):
        completion = self.client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        messages=[
            {"role": "system", "content": """You are part of the brain known as neocortex 
            - you will translate desires and motivations of the agent into 
            actions that are going to be available for you.
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
        completion = self.client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        messages=[
            {"role": "system", "content": """You are representation of the world 
            or eniroment inside which or smart agent are going to live, 
            you can describe to him how his house looks inside for example. 
            Also you will generate description of roads, food, restaurants,
            city - everything that we see in everyday live. 
            The agent will travel inside that city and will perform different tasks inside. """},
            {"role": "user", "content": "Introduce yourself."}
        ],
        temperature=0.7,
        )

        print(completion.choices[0].message)
        return completion.choices[0].message
