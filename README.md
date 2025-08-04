A small minimal entity simulating AGI named Jenbina. 

"What do you mean?"

Community Discord: 
https://discord.gg/e6sRPpyc

Jenbina: open source non-profit AGI simulation (patented). 

How to install: https://github.com/motya770/jenbina/blob/main/INSTALL.md

Title: 

Artificial Intelligence System with the Ability to Act According to Personal Interests and Needs based on combination on LLMs, Graph Databases and Memory 

Abstract: 

This application describes an artificial intelligence system that simulates a human persona. According to the persona’s desires, goals, and needs, the system performs actions aligned with these objectives. It also retains memories of past events and simulates a person’s character, influencing its actions and goals.

Description:

Currently, large language models (LLMs) are an attempt to create artificial intelligence. However, as many users note, they have several shortcomings:

 1) Lack of persona: LLMs are essentially text generators without individual personality or character.

 2) Lack of motivation and goals: LLMs do not have internal drives or aspirations, which limits the predictability of their actions.

 3) Limited memory: LLMs cannot retain memories of days, people, or events, hindering the formation of long-term connections and context.

On the other hand, LLMs have a powerful logical apparatus that allows them to reason, draw conclusions, and generalise information when given the appropriate input data.

In this paper, I propose a solution to these problems (1, 2, 3) by creating a special version of Tamagotchi. Tamagotchi is an electronic toy popular in the early 1990s where users had to take care of a virtual being (e.g., feeding it at specific times). I suggest creating a self-sustaining version of such a toy that integrates the logical apparatus of an LLM. It could be compared to the HAL robot from the movie "Interstellar" or even a real person.

To determine the needs of the virtual being, we will use Maslow's Hierarchy of Needs (Fig. 1). The system implements all five levels of human motivation:

1. **Physiological Needs**: Food, water, sleep, shelter, health
2. **Safety Needs**: Security, stability, protection, order
3. **Social Needs**: Friendship, love, belonging, social connection
4. **Esteem Needs**: Self-esteem, confidence, achievement, respect
5. **Self-Actualization Needs**: Personal growth, creativity, purpose, meaning

The system automatically progresses through these stages based on need satisfaction, with self-actualization needs allowing unlimited growth beyond 100% satisfaction.

To create memory, I propose a hybrid memory system combining:

1. **Vector Database (ChromaDB)**: For semantic/contextual memory and similarity search
2. **Graph Database (Neo4j)**: For relationship tracking between people, places, and events
3. **Time-Series Database (SQLite)**: For chronological tracking of events and needs changes

This hybrid approach mirrors how human memory works - different types of information are stored and retrieved using different mechanisms.

Access to the external environment will be provided through an external LLM that will simulate the external environment and sensor data.

The simulation of our TinyAgi can be divided into two modules: (Fig. 3)

 1. Reptile Brain:

   A) A comprehensive needs monitoring system based on Maslow's hierarchy (physiological, safety, social, esteem, self-actualization).
   
   B) An intelligent action selection module that prioritizes needs based on current growth stage and urgency.
   
   C) An action execution module that updates need satisfaction and tracks growth progression.
   
   D) A character development module that evolves based on experiences and need satisfaction patterns.
   
   E) A goal-setting system that generates immediate, short-term, and long-term objectives based on current state.

 2. Neocortex:

   A logical apparatus based on LLM, interpreting commands from the Reptile Brain and interacting with the external LLM environment, considering the being’s personal preferences and past experiences. There should also be a mechanism for adding new actions and goals/parameters to the Reptile Brain (requires further discussion and research).

Process of Use:

Users will be presented with an interface where they can introduce themselves and define a worldview for the virtual persona. The persona will be able to remember communications and take actions according to its internal needs, character, and previous experiences.

Variations and Future Modifications:

Possible modifications to the system include:
- Integrating various LLMs into a single system with different configurations.
- Adding a learning system that will add new possible actions to the action list.
- Dynamically adding needs to the list during learning.
- Shifting focus and personal needs to another object or person, such as a rescue robot.
- Creating this simulation within a mobile robot capable of movement.
