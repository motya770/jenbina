# Jenbina System Design Schema

## Overview
Jenbina is an open-source AGI simulation that creates a self-sustaining virtual persona with personality, motivation, memory, and the ability to interact with users and the environment. The system implements Maslow's Hierarchy of Needs and uses a hybrid memory system to simulate human-like cognition and behavior.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              JENBINA AGI SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   USER INTERFACE│    │  STREAMLIT APP  │    │  CHAT HANDLER   │            │
│  │                 │    │                 │    │                 │            │
│  │ • Chat Input    │◄──►│ • Web Interface │◄──►│ • Conversation  │            │
│  │ • Status Display│    │ • Debug Controls│    │ • Context Mgmt  │            │
│  │ • Environment   │    │ • Memory Stats  │    │ • Response Gen  │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           └───────────────────────┼───────────────────────┘                    │
│                                   │                                            │
│  ┌─────────────────────────────────┼─────────────────────────────────────────┐  │
│  │                        CORE SYSTEM LAYER                                 │  │
│  │                                                                           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │  │
│  │  │    PERSON       │  │   ENVIRONMENT   │  │    MEMORY       │          │  │
│  │  │                 │  │                 │  │                 │          │  │
│  │  │ • Maslow Needs  │  │ • Weather Sim   │  │ • ChromaDB      │          │  │
│  │  │ • Conversations │  │ • Location Sys  │  │ • Neo4j Graph   │          │  │
│  │  │ • State Mgmt    │  │ • Dynamic Events│  │ • SQLite Time   │          │  │
│  │  │ • Communication │  │ • Mood Factors  │  │ • Hybrid Search │          │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘          │  │
│  │           │                       │                       │              │  │
│  │           └───────────────────────┼───────────────────────┘              │  │
│  │                                   │                                      │  │
│  │  ┌─────────────────────────────────┼─────────────────────────────────────┐│  │
│  │  │                    COGNITION LAYER                                   ││  │
│  │  │                                                                       ││  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      ││  │
│  │  │  │  META-COGNITION │  │ ACTION DECISION │  │ STATE ANALYSIS  │      ││  │
│  │  │  │                 │  │                 │  │                 │      ││  │
│  │  │  │ • Self-Reflect  │  │ • Maslow Chain  │  │ • Current State │      ││  │
│  │  │  │ • Bias Detect   │  │ • Need Priority │  │ • Growth Stage  │      ││  │
│  │  │  │ • Strategy Opt  │  │ • Action Exec   │  │ • Satisfaction  │      ││  │
│  │  │  │ • Pattern Anal  │  │ • Goal Setting  │  │ • Recommendations│      ││  │
│  │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      ││  │
│  │  │           │                       │                       │          ││  │
│  │  │           └───────────────────────┼───────────────────────┘          ││  │
│  │  │                                   │                                  ││  │
│  │  │  ┌─────────────────────────────────┼─────────────────────────────────┐││  │
│  │  │  │                    NEEDS LAYER                                   │││  │
│  │  │  │                                                                   │││  │
│  │  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │││  │
│  │  │  │  │ PHYSIOLOGICAL   │  │     SAFETY      │  │     SOCIAL      │  │││  │
│  │  │  │  │                 │  │                 │  │                 │  │││  │
│  │  │  │  │ • Hunger        │  │ • Security      │  │ • Friendship    │  │││  │
│  │  │  │  │ • Thirst        │  │ • Stability     │  │ • Love          │  │││  │
│  │  │  │  │ • Sleep         │  │ • Protection    │  │ • Belonging     │  │││  │
│  │  │  │  │ • Health        │  │ • Order         │  │ • Connection    │  │││  │
│  │  │  │  │ • Shelter       │  │                 │  │                 │  │││  │
│  │  │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │││  │
│  │  │  │           │                       │                       │      │││  │
│  │  │  │           └───────────────────────┼───────────────────────┘      │││  │
│  │  │  │                                   │                              │││  │
│  │  │  │  ┌─────────────────────────────────┼─────────────────────────────┐│││  │
│  │  │  │  │                    GROWTH LAYER                               ││││  │
│  │  │  │  │                                                                 ││││  │
│  │  │  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐││││  │
│  │  │  │  │  │    ESTEEM       │  │SELF-ACTUALIZATION│  │   GROWTH TRACK  │││││  │
│  │  │  │  │  │                 │  │                 │  │                 │││││  │
│  │  │  │  │  │ • Self-Esteem   │  │ • Personal Growth│  │ • Stage Progression│││││  │
│  │  │  │  │  │ • Confidence    │  │ • Creativity     │  │ • Need Satisfaction│││││  │
│  │  │  │  │  │ • Achievement   │  │ • Purpose        │  │ • Growth Insights│││││  │
│  │  │  │  │  │ • Respect       │  │ • Meaning        │  │ • Opportunities │││││  │
│  │  │  │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘││││  │
│  │  │  │  └─────────────────────────────────────────────────────────────────┘│││  │
│  │  │  └─────────────────────────────────────────────────────────────────────┘││  │
│  │  └─────────────────────────────────────────────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                        EXTERNAL INTEGRATIONS                               │  │
│  │                                                                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   OLLAMA LLM    │  │   WEATHER API   │  │   EVENTS API    │            │  │
│  │  │                 │  │                 │  │                 │            │  │
│  │  │ • llama3.2:3b   │  │ • OpenWeatherMap│  │ • Event Discovery│            │  │
│  │  │ • JSON Mode     │  │ • Temperature   │  │ • Venue Data    │            │  │
│  │  │ • Reasoning     │  │ • Conditions    │  │ • Recommendations│            │  │
│  │  │ • Decision      │  │ • Forecast      │  │ • Dynamic Events│            │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   USER      │───►│  INTERFACE  │───►│   PERSON    │───►│   MEMORY    │
│  INPUT      │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   ▼                   ▼                   ▼
       │            ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │            │ ENVIRONMENT │    │  COGNITION  │    │  HYBRID DB  │
       │            │             │    │             │    │             │
       │            │ • Weather   │    │ • Decision  │    │ • ChromaDB  │
       │            │ • Location  │    │ • Reasoning │    │ • Neo4j     │
       │            │ • Events    │    │ • Analysis  │    │ • SQLite    │
       │            └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   ▼                   ▼                   ▼
       │            ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │            │   NEEDS     │    │  META-COG   │    │  RESPONSE   │
       │            │             │    │             │    │             │
       │            │ • Maslow    │    │ • Reflection│    │ • Context   │
       │            │ • Priority  │    │ • Bias Check│    │ • Memory    │
       │            │ • Growth    │    │ • Strategy  │    │ • Personal  │
       └───────────►└─────────────┘    └─────────────┘    └─────────────┘
```

## Component Details

### 1. Person System (`core/person/`)
- **Purpose**: Central entity representing Jenbina's persona
- **Components**:
  - `Person`: Main persona class with needs and conversations
  - `Message`: Individual message representation
  - `Conversation`: Conversation tracking with outsiders
- **Key Features**:
  - Maslow needs integration
  - Communication history tracking
  - State management and statistics

### 2. Needs System (`core/needs/`)
- **Purpose**: Implements Maslow's Hierarchy of Needs
- **Components**:
  - `MaslowNeedsSystem`: Core needs management
  - `MaslowDecisionChain`: Decision-making based on needs
  - `BasicNeeds`: Physiological needs tracking
- **Need Levels**:
  1. **Physiological**: Hunger, thirst, sleep, health, shelter
  2. **Safety**: Security, stability, protection, order
  3. **Social**: Friendship, love, belonging, connection
  4. **Esteem**: Self-esteem, confidence, achievement, respect
  5. **Self-Actualization**: Personal growth, creativity, purpose, meaning

### 3. Memory System (`core/memory/`)
- **Purpose**: Hybrid memory system simulating human memory
- **Components**:
  - **ChromaDB**: Semantic/contextual memory and similarity search
  - **Neo4j**: Relationship tracking (people, places, events)
  - **SQLite**: Time-series data and chronological tracking
- **Features**:
  - Multi-modal memory storage
  - Semantic search capabilities
  - Relationship graph management
  - Temporal memory retrieval

### 4. Cognition System (`core/cognition/`)
- **Purpose**: Advanced reasoning and decision-making
- **Components**:
  - `MetaCognitiveSystem`: Self-reflection and bias detection
  - `ActionDecisionChain`: Need-based action selection
  - `StateAnalysisChain`: Current state assessment
  - `AsimovCheckChain`: Safety and ethical compliance
- **Features**:
  - Cognitive bias detection
  - Strategy optimization
  - Pattern analysis
  - Confidence calibration

### 5. Environment System (`core/environment/`)
- **Purpose**: Simulates realistic external environment
- **Components**:
  - `EnvironmentSimulator`: Main environment controller
  - `LocationSystem`: Palo Alto location data
  - `DynamicEvents`: Real-time event generation
  - `WorldState`: Environment state management
- **Features**:
  - Weather simulation/API integration
  - Location-based activities
  - Dynamic event generation
  - Mood factor calculation

### 6. Interaction System (`core/interaction/`)
- **Purpose**: Handles user communication and responses
- **Components**:
  - `ChatHandler`: Main conversation processor
  - Context management
  - Response generation
- **Features**:
  - Conversation history integration
  - Memory-based responses
  - Personality-driven interactions

## Data Storage Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HYBRID MEMORY SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   CHROMADB      │    │     NEO4J       │    │    SQLITE       │        │
│  │                 │    │                 │    │                 │        │
│  │ • Semantic      │    │ • Relationships │    │ • Time Series   │        │
│  │ • Contextual    │    │ • People Graph  │    │ • Chronological │        │
│  │ • Similarity    │    │ • Location Map  │    │ • Event History │        │
│  │ • Vector Search │    │ • Event Nodes   │    │ • Needs Tracking│        │
│  │ • Embeddings    │    │ • Path Finding  │    │ • Statistics    │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│           │                       │                       │                │
│           └───────────────────────┼───────────────────────┘                │
│                                   │                                        │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                    MEMORY INTEGRATION LAYER                           │  │
│  │                                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│  │  │  SEMANTIC       │  │  RELATIONSHIP   │  │  TEMPORAL       │      │  │
│  │  │  RETRIEVAL      │  │  QUERIES        │  │  QUERIES        │      │  │
│  │  │                 │  │                 │  │                 │      │  │
│  │  │ • Similar       │  │ • Person Links  │  │ • Time Range    │      │  │
│  │  │ • Contextual    │  │ • Location Visits│  │ • Event History │      │  │
│  │  │ • Meaningful    │  │ • Interaction   │  │ • Need Changes  │      │  │
│  │  │ • Relevant      │  │ • Patterns      │  │ • Trends        │      │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Decision-Making Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CURRENT    │───►│   NEEDS     │───►│  DECISION   │───►│   ACTION    │
│   STATE     │    │  ANALYSIS   │    │   CHAIN     │    │ EXECUTION   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ ENVIRONMENT │    │ PRIORITY    │    │ META-COG    │    │ NEEDS       │
│   STATE     │    │  NEEDS      │    │ REFLECTION  │    │ UPDATE      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ MOOD        │    │ GROWTH      │    │ BIAS        │    │ MEMORY      │
│ FACTORS     │    │ STAGE       │    │ DETECTION   │    │ STORAGE     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Key Features

### 1. Self-Sustaining Personality
- Continuous needs monitoring and satisfaction
- Personality evolution based on experiences
- Goal-driven behavior with long-term planning

### 2. Advanced Memory System
- Multi-modal memory storage (semantic, relational, temporal)
- Context-aware memory retrieval
- Relationship tracking and pattern recognition

### 3. Meta-Cognitive Capabilities
- Self-reflection and bias detection
- Strategy optimization and learning
- Confidence calibration and error correction

### 4. Realistic Environment Simulation
- Dynamic weather and location systems
- Event generation and activity suggestions
- Mood-influencing environmental factors

### 5. Ethical AI Framework
- Asimov's laws compliance checking
- Safety-first decision making
- Transparent reasoning processes

## Technology Stack

- **Language**: Python 3.x
- **LLM**: Ollama with llama3.2:3b-instruct-fp16
- **Web Framework**: Streamlit
- **Vector Database**: ChromaDB
- **Graph Database**: Neo4j
- **Time-Series**: SQLite
- **Embeddings**: Ollama Embeddings
- **APIs**: OpenWeatherMap, Event Discovery APIs

## Scalability Considerations

1. **Memory System**: Hybrid approach allows for distributed storage
2. **Cognition**: Modular design enables parallel processing
3. **Environment**: API-based integration for real-world data
4. **Personality**: Extensible needs and growth systems

This architecture creates a comprehensive AGI simulation that balances complexity with maintainability, providing a foundation for advanced AI personality development and human-like interaction capabilities. 