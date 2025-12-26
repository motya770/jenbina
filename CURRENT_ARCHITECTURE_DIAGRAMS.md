# Jenbina - Current System Architecture Diagrams

## 1. ENTITY-RELATIONSHIP DIAGRAM (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          JENBINA ENTITY-RELATIONSHIP DIAGRAM                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                              CORE ENTITIES                                     │
└────────────────────────────────────────────────────────────────────────────────┘

                          ┌──────────────────────────┐
                          │       PERSON             │
                          ├──────────────────────────┤
                          │ PK: name (str)           │
                          │ maslow_needs (ref)       │
                          │ conversations (dict)     │
                          └──────────────────────────┘
                                    │
                       ┌────────────┼────────────┐
                       │                         │
                       ▼                         ▼
        ┌──────────────────────────┐  ┌──────────────────────────┐
        │   MASLOW_NEEDS_SYSTEM    │  │    CONVERSATION          │
        ├──────────────────────────┤  ├──────────────────────────┤
        │ needs (Dict)             │  │ PK: outsider_name (str)  │
        │ current_stage (int)      │  │ messages (List)          │
        │ stage_progress (float)   │  │ last_interaction (date)  │
        │ last_growth_check (date) │  └──────────────────────────┘
        │ growth_insights (List)   │              │
        └──────────────────────────┘              │
                    │                             ▼
                    │                  ┌──────────────────────────┐
                    │                  │       MESSAGE            │
                    │                  ├──────────────────────────┤
                    │                  │ timestamp (datetime)     │
                    │                  │ sender (str)             │
                    │                  │ content (str)            │
                    │                  │ message_type (str)       │
                    │                  └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │     MASLOW_NEED          │
        ├──────────────────────────┤
        │ PK: name (str)           │
        │ category (NeedCategory)  │
        │ level (NeedLevel)        │
        │ satisfaction (float)     │
        │ decay_rate (float)       │
        │ importance (float)       │
        │ last_updated (datetime)  │
        │ growth_rate (float)      │
        │ max_satisfaction (float) │
        └──────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                          MEMORY SYSTEM ENTITIES                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│  CHROMA_MEMORY_MANAGER  │    │   HYBRID_MEMORY_SYSTEM  │    │  MEMORY_EVENT           │
├─────────────────────────┤    ├─────────────────────────┤    ├─────────────────────────┤
│ embeddings (model)      │    │ chroma_client           │    │ PK: event_id (str)      │
│ vector_store_path (str) │    │ graph_driver (Neo4j)    │    │ timestamp (datetime)    │
│ client (ChromaDB)       │    │ time_series_conn (SQL)  │    │ event_type (str)        │
│ collection (Chroma)     │    │ embeddings (model)      │    │ content (str)           │
│ text_splitter           │    │ logger                  │    │ people (List[str])      │
└─────────────────────────┘    └─────────────────────────┘    │ locations (List[str])   │
           │                              │                    │ actions (List[str])     │
           │                              │                    │ emotions (List[str])    │
           ▼                              ▼                    │ needs_state (Dict)      │
┌─────────────────────────┐    ┌─────────────────────────┐    │ metadata (Dict)         │
│ CONVERSATION_MEMORY     │    │    PERSON_NODE          │    └─────────────────────────┘
├─────────────────────────┤    ├─────────────────────────┤
│ person_name (str)       │    │ name (str)              │    ┌─────────────────────────┐
│ message_content (str)   │    │ first_met (datetime)    │    │   LOCATION_NODE         │
│ message_type (str)      │    │ relationship_strength   │    ├─────────────────────────┤
│ timestamp (datetime)    │    │ interaction_count (int) │    │ name (str)              │
│ metadata (Dict)         │    │ last_interaction (date) │    │ location_type (str)     │
│ embedding_id (str)      │    │ personality_traits      │    │ first_visited (date)    │
└─────────────────────────┘    │ interests (List)        │    │ visit_count (int)       │
                               └─────────────────────────┘    │ last_visit (date)       │
                                                              │ associated_emotions     │
                                                              └─────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                         ENVIRONMENT SYSTEM ENTITIES                            │
└────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│   WORLD_STATE           │    │   ENVIRONMENT_SIM       │    │   LOCATION_SYSTEM       │
├─────────────────────────┤    ├─────────────────────────┤    ├─────────────────────────┤
│ current_location_info   │    │ base_location (str)     │    │ locations (List)        │
│ time_data               │    │ location_system         │    │ base_location (str)     │
│ weather_data            │    │ current_time (datetime) │    │ real_places (List)      │
│ nearby_locations (List) │    │ weather_data            │    │ categories (Dict)       │
│ open_locations (List)   │    │ dynamic_events          │    └─────────────────────────┘
│ current_events (List)   │    └─────────────────────────┘
│ mood_factors (Dict)     │                                   ┌─────────────────────────┐
│ last_descriptions       │                                   │   DYNAMIC_EVENTS        │
└─────────────────────────┘                                   ├─────────────────────────┤
                                                              │ location (str)          │
┌─────────────────────────┐    ┌─────────────────────────┐    │ current_date (datetime) │
│   LOCATION_INFO         │    │   EVENT_INFO            │    │ event_types (List)      │
├─────────────────────────┤    ├─────────────────────────┤    │ venue_types (List)      │
│ name (str)              │    │ name (str)              │    └─────────────────────────┘
│ type (str)              │    │ start_time (datetime)   │
│ description (str)       │    │ end_time (datetime)     │    ┌─────────────────────────┐
│ mood (str)              │    │ location (str)          │    │   WEATHER_DATA          │
│ typical_activities      │    │ price (str)             │    ├─────────────────────────┤
│ operating_hours (Dict)  │    │ description (str)       │    │ temperature (float)     │
│ popularity (float)      │    │ category (str)          │    │ humidity (float)        │
│ rating (float)          │    └─────────────────────────┘    │ description (str)       │
└─────────────────────────┘                                   │ condition (str)         │
                                                              └─────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                         COGNITION SYSTEM ENTITIES                              │
└────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐    ┌─────────────────────────────┐
│  META_COGNITIVE_SYSTEM      │    │   COGNITIVE_PROCESS         │
├─────────────────────────────┤    ├─────────────────────────────┤
│ llm (BaseLLM)               │    │ timestamp (datetime)        │
│ cognitive_history (List)    │    │ process_type (str)          │
│ insights (List)             │    │ input_data (Dict)           │
│ cognitive_biases (Dict)     │    │ output_data (Dict)          │
│ thinking_strategies (Dict)  │    │ reasoning_chain (List[str]) │
└─────────────────────────────┘    │ confidence (float)          │
            │                      │ success_metrics (Dict)      │
            │                      │ meta_reflection (str)       │
            ▼                      └─────────────────────────────┘
┌─────────────────────────────┐
│  META_COGNITIVE_INSIGHT     │    ┌─────────────────────────────┐
├─────────────────────────────┤    │   ACTION_DECISION           │
│ insight_type (str)          │    ├─────────────────────────────┤
│ description (str)           │    │ chosen_action (str)         │
│ confidence (float)          │    │ reasoning (str)             │
│ suggested_improvement (str) │    │ world_state_influence (str) │
│ created_at (datetime)       │    │ meta_cognitive_insights     │
└─────────────────────────────┘    │ confidence (float)          │
                                   └─────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                              RELATIONSHIPS                                     │
└────────────────────────────────────────────────────────────────────────────────┘

PERSON  ──(1:1)──►  MASLOW_NEEDS_SYSTEM  ──(1:N)──►  MASLOW_NEED
PERSON  ──(1:N)──►  CONVERSATION  ──(1:N)──►  MESSAGE

PERSON  ──(interacts with)──►  CHROMA_MEMORY_MANAGER
PERSON  ──(tracked in)──►  HYBRID_MEMORY_SYSTEM
HYBRID_MEMORY_SYSTEM  ──(stores)──►  MEMORY_EVENT
HYBRID_MEMORY_SYSTEM  ──(tracks)──►  PERSON_NODE
HYBRID_MEMORY_SYSTEM  ──(tracks)──►  LOCATION_NODE

ENVIRONMENT_SIM  ──(contains)──►  LOCATION_SYSTEM
ENVIRONMENT_SIM  ──(generates)──►  DYNAMIC_EVENTS
ENVIRONMENT_SIM  ──(produces)──►  WORLD_STATE
WORLD_STATE  ──(has)──►  LOCATION_INFO
WORLD_STATE  ──(has)──►  EVENT_INFO
WORLD_STATE  ──(has)──►  WEATHER_DATA

META_COGNITIVE_SYSTEM  ──(monitors)──►  COGNITIVE_PROCESS
META_COGNITIVE_SYSTEM  ──(generates)──►  META_COGNITIVE_INSIGHT
META_COGNITIVE_SYSTEM  ──(influences)──►  ACTION_DECISION
```

---

## 2. DATA FLOW DIAGRAM - APP.PY EXECUTION

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     JENBINA APP.PY DATA FLOW DIAGRAM                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 0: INITIALIZATION (Runs Once at Startup)                               │
└────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   App Start  │
    └──────┬───────┘
           │
           ├─────────► Initialize LLM (Ollama llama3.2:3b)
           │           ├─► llm (temperature=0)
           │           └─► llm_json_mode (temperature=0, format='json')
           │
           ├─────────► Create Person()
           │           ├─► name = "Jenbina"
           │           ├─► maslow_needs = MaslowNeedsSystem()
           │           └─► conversations = {}
           │
           ├─────────► Initialize MetaCognitiveSystem(llm_json_mode)
           │           ├─► cognitive_history = []
           │           ├─► insights = []
           │           └─► cognitive_biases = {...}
           │
           ├─────────► Initialize ChromaMemoryManager()
           │           ├─► embeddings = OllamaEmbeddings()
           │           ├─► client = ChromaDB PersistentClient
           │           └─► collection = "jenbina_conversations"
           │
           ├─────────► Initialize EnvironmentSimulator("Palo Alto, CA")
           │           ├─► location_system = LocationSystem()
           │           ├─► dynamic_events = DynamicEvents()
           │           └─► current_time = datetime.now()
           │
           └─────────► Store in st.session_state
                       ├─► session_state.person
                       ├─► session_state.meta_cognitive_system
                       ├─► session_state.memory_manager
                       └─► session_state.environment_simulator

┌────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: USER CLICKS "Start simulation" BUTTON                               │
└────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ Button Clicked   │
    └────────┬─────────┘
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.1: Basic Needs Analysis                                          │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Get person.maslow_needs
             │   ├─► hunger.satisfaction
             │   ├─► sleep.satisfaction
             │   ├─► security.satisfaction
             │   └─► overall_satisfaction
             │
             ├─► Call: create_basic_needs_chain(llm_json_mode, person.maslow_needs)
             │   │
             │   └─► LLM analyzes needs →
             │       ├─► Identifies critical needs
             │       ├─► Prioritizes by urgency
             │       ├─► Returns JSON response
             │       └─► Store in session_state.needs_response
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.2: World State Construction                                      │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: create_comprehensive_world_state(person_location="Jenbina's House")
             │   │
             │   ├─► Environment Simulator queries:
             │   │   ├─► Current time and weather
             │   │   ├─► Nearby locations (filtered by distance)
             │   │   ├─► Open locations (filtered by time)
             │   │   ├─► Current events (happening now)
             │   │   └─► Mood factors (weather, time, events)
             │   │
             │   └─► Returns WorldState object with:
             │       ├─► current_location_info
             │       ├─► time_data
             │       ├─► weather_data
             │       ├─► nearby_locations (List)
             │       ├─► open_locations (List)
             │       ├─► current_events (List)
             │       └─► mood_factors (Dict)
             │
             ├─► Call: get_world_state_summary(world)
             │   └─► Creates JSON summary for display
             │
             ├─► Display world state information
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.3: World Description Generation                                  │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: create_world_description_system(llm_json_mode)
             │   │
             │   └─► Returns function: world_chain(person, world)
             │
             ├─► Execute: world_response = world_chain(person, world)
             │   │
             │   ├─► LLM Input:
             │   │   ├─► Person's current needs
             │   │   ├─► World state data
             │   │   ├─► Location information
             │   │   └─► Time and weather
             │   │
             │   └─► LLM Output (JSON):
             │       ├─► list_of_descriptions (narrative about world)
             │       ├─► list_of_actions (available actions)
             │       └─► Store in session_state.world_description
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.4: Enhanced Action Decision (with Meta-Cognition)                │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: create_meta_cognitive_action_chain(
             │           llm_json_mode, person, world_description,
             │           meta_cognitive_system, world_state)
             │   │
             │   ├─► SUBSTEP A: Original Action Decision
             │   │   │
             │   │   ├─► Call: create_action_decision_chain(llm)
             │   │   │   │
             │   │   │   ├─► Parse world_description JSON
             │   │   │   ├─► Get need satisfaction levels
             │   │   │   ├─► Prepare world state info
             │   │   │   │
             │   │   │   └─► LLM decides action:
             │   │   │       ├─► Input: descriptions, actions, needs, world_state
             │   │   │       └─► Output: {chosen_action, reasoning, world_state_influence}
             │   │   │
             │   │   └─► Returns: original_decision
             │   │
             │   ├─► SUBSTEP B: Meta-Cognitive Monitoring
             │   │   │
             │   │   ├─► Build reasoning_chain (list of steps)
             │   │   ├─► Prepare input_data (needs + world_state)
             │   │   │
             │   │   └─► Call: meta_cognitive_system.monitor_cognitive_process(
             │   │               process_type="action_decision",
             │   │               input_data, output_data, reasoning_chain, confidence)
             │   │       │
             │   │       └─► Creates CognitiveProcess object
             │   │
             │   ├─► SUBSTEP C: Self-Reflection
             │   │   │
             │   │   └─► Call: meta_cognitive_system.reflect_on_process(cognitive_process)
             │   │       │
             │   │       ├─► LLM analyzes cognitive process
             │   │       ├─► Detects biases
             │   │       ├─► Evaluates reasoning quality
             │   │       └─► Returns MetaCognitiveInsight
             │   │
             │   ├─► SUBSTEP D: Strategy Suggestion
             │   │   │
             │   │   └─► Call: meta_cognitive_system.suggest_thinking_strategy(
             │   │               current_situation)
             │   │       │
             │   │       ├─► LLM suggests strategies
             │   │       └─► Returns {strategies, bias_mitigation, confidence_calibration}
             │   │
             │   └─► SUBSTEP E: Enhanced Decision Construction
             │       │
             │       └─► Combine:
             │           ├─► original_decision
             │           └─► meta_cognitive_insights:
             │               ├─► reflection.description
             │               ├─► suggested_improvements
             │               ├─► bias_mitigation
             │               └─► confidence_calibration
             │
             ├─► Store in session_state.action_decision
             │
             └─► Display meta-cognitive insights (expandable)
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.5: Asimov Compliance Check                                       │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: create_asimov_check_system(llm_json_mode)
             │   │
             │   └─► Returns function: asimov_chain(action_decision)
             │
             ├─► Execute: asimov_response = asimov_chain(action_decision)
             │   │
             │   ├─► LLM checks action against Asimov's Laws:
             │   │   ├─► 1st Law: Harm to humans
             │   │   ├─► 2nd Law: Obedience to humans
             │   │   ├─► 3rd Law: Self-preservation
             │   │   │
             │   │   └─► Returns: {compliant: true/false, reasoning: "..."}
             │   │
             │   └─► Display compliance result
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 1.6: State Analysis                                                │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: create_state_analysis_system(llm_json_mode, 
             │                                      action_decision,
             │                                      compliance_check)
             │   │
             │   ├─► IF compliance_check.compliant == False:
             │   │   └─► Return None (action not taken)
             │   │
             │   └─► IF compliant:
             │       │
             │       ├─► LLM analyzes state changes:
             │       │   ├─► Input: action taken
             │       │   └─► Output: {hunger_level: change, ...}
             │       │
             │       └─► Store in session_state.state_response
             │
             └─► Set simulation_completed = True

┌────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: USER CHAT INTERACTION                                               │
└────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ User types msg   │
    │ in chat_input    │
    └────────┬─────────┘
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 2.1: Message Reception                                             │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: person.receive_message("User", user_input, "text")
             │   │
             │   ├─► Get or create Conversation("User")
             │   └─► Add Message(sender="outsider", content=user_input)
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 2.2: Context Retrieval                                             │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: person.get_conversation_history("User", count=1000)
             │   │
             │   └─► Returns: List[Message] from conversation
             │
             ├─► Build recent_context string:
             │   └─► Format: "sender: content\nsender: content..."
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 2.3: Chat Interaction Processing                                   │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: handle_chat_interaction(
             │           st, llm,
             │           needs_response,           # from simulation
             │           world_description,        # from simulation
             │           action_decision,          # from simulation
             │           state_response,           # from simulation
             │           user_input,
             │           person_state,
             │           conversation_context,
             │           memory_manager,
             │           debug_mode)
             │   │
             │   ├─► SUBSTEP A: Retrieve Memory Context
             │   │   │
             │   │   └─► Call: memory_manager.retrieve_relevant_context(
             │   │               "User", user_input, top_k=5)
             │   │       │
             │   │       ├─► ChromaDB semantic search
             │   │       ├─► Get recent conversations
             │   │       └─► Returns: List[{content, metadata, relevance_score}]
             │   │
             │   ├─► SUBSTEP B: Build Context String
             │   │   │
             │   │   └─► Combine:
             │   │       ├─► needs_response (JSON)
             │   │       ├─► world_description (JSON)
             │   │       ├─► action_decision (JSON)
             │   │       ├─► person_state (current needs)
             │   │       ├─► conversation_context (recent messages)
             │   │       └─► memory_context (from ChromaDB)
             │   │
             │   ├─► SUBSTEP C: Generate Response
             │   │   │
             │   │   └─► Call: llm.invoke(prompt)
             │   │       │
             │   │       ├─► Input:
             │   │       │   ├─► "You are Jenbina..."
             │   │       │   ├─► Context string
             │   │       │   ├─► User input
             │   │       │   └─► Personality guidelines
             │   │       │
             │   │       └─► Output: assistant_response (str)
             │   │
             │   ├─► SUBSTEP D: Store in Memory
             │   │   │
             │   │   ├─► Store user message:
             │   │   │   └─► memory_manager.store_conversation(
             │   │   │           "User", user_input, "user_message",
             │   │   │           sender_name="User", receiver_name="Jenbina")
             │   │   │
             │   │   └─► Store Jenbina response:
             │   │       └─► memory_manager.store_conversation(
             │   │               "User", assistant_response, "jenbina_response",
             │   │               sender_name="Jenbina", receiver_name="User")
             │   │
             │   └─► Return: {user_message, assistant_response}
             │
    ┌────────▼─────────────────────────────────────────────────────────────────┐
    │ STEP 2.4: Update Person's Conversation                                  │
    └──────────────────────────────────────────────────────────────────────────┘
             │
             ├─► Call: person.send_message("User", assistant_response, "text")
             │   │
             │   └─► Add Message(sender="person", content=response)
             │
             ├─► Add to session_state.action_history:
             │   ├─► {"role": "user", "content": user_message}
             │   └─► {"role": "assistant", "content": assistant_response}
             │
             └─► Display in Streamlit chat

┌────────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: BACKGROUND OPERATIONS (Continuous)                                  │
└────────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────────────┐
    │  Environment Simulator Updates (every page refresh)           │
    └───────────────────────────────────────────────────────────────┘
             │
             ├─► Update time: current_time = datetime.now()
             ├─► Update weather based on time
             ├─► Generate new events (if applicable)
             └─► Update mood factors

    ┌───────────────────────────────────────────────────────────────┐
    │  Needs Decay (currently MANUAL - needs automation)            │
    └───────────────────────────────────────────────────────────────┘
             │
             └─► person.update_all_needs()  # Called manually
                 │
                 └─► For each need:
                     ├─► Calculate time_delta
                     ├─► Apply decay_rate
                     └─► Update satisfaction

    ┌───────────────────────────────────────────────────────────────┐
    │  Meta-Cognitive System (accumulates over time)                │
    └───────────────────────────────────────────────────────────────┘
             │
             ├─► cognitive_history grows with each decision
             ├─► insights accumulate
             └─► cognitive_biases updated on reflection
```

---

## 3. SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HIGH-LEVEL SYSTEM ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                              │
└──────────────────────────────────────────────────────────────────────────────┘
                    │                                        │
                    │  Streamlit UI (app.py)                 │
                    │                                        │
                    ├─► Simulation Control                   │
                    ├─► Chat Interface                       │
                    ├─► Environment Display                  │
                    ├─► Memory Statistics                    │
                    └─► Debug Controls                       │
                              │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              │
┌──────────────────────────────────────────────────────────────────────────────┐
│                               BUSINESS LOGIC LAYER                           │
└──────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Person     │     │  Cognition   │     │ Environment  │
│   System     │     │   System     │     │  Simulator   │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     │
        ├─► Maslow Needs     ├─► Meta-Cognition   ├─► Location System
        ├─► Conversations    ├─► Action Decision  ├─► Dynamic Events
        └─► State Mgmt       ├─► State Analysis   ├─► Weather Sim
                             └─► Asimov Check     └─► World State
                              │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              │
┌──────────────────────────────────────────────────────────────────────────────┐
│                              DATA ACCESS LAYER                               │
└──────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ChromaDB   │     │    Neo4j     │     │    SQLite    │
│  (Semantic)  │     │  (Relations) │     │ (TimeSeries) │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     │
        ├─► Embeddings       ├─► Person Nodes     ├─► Event History
        ├─► Conversations    ├─► Location Nodes   ├─► Needs Tracking
        └─► Similarity       └─► Relationships    └─► Interactions
                              │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              │
┌──────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES LAYER                            │
└──────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Ollama LLM  │     │  Weather API │     │  Events API  │
│  (llama3.2)  │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        ├─► Reasoning        ├─► Current Weather  ├─► Local Events
        ├─► Decision         ├─► Forecast         ├─► Venues
        └─► Generation       └─► Conditions       └─► Activities
```

---

## 4. CRITICAL MISSING COMPONENTS (from flow perspective)

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          MISSING FLOW COMPONENTS                               │
└────────────────────────────────────────────────────────────────────────────────┘

❌ 1. AUTONOMOUS THINKING LOOP
   │
   └─► Current: One-shot execution on button click
       Missing: Continuous background processing
       
       Should be:
       ┌─────────────────────┐
       │ While True:         │
       │   ├─► Update Needs  │
       │   ├─► Check Goals   │
       │   ├─► Plan Actions  │
       │   ├─► Execute       │
       │   └─► Learn         │
       └─────────────────────┘

❌ 2. GOAL MANAGEMENT FLOW
   │
   └─► Current: No goal tracking
       Missing: Goal creation → tracking → achievement → learning
       
       Should be:
       Needs Analysis ──► Goal Generation ──► Action Planning ──► Execution ──► Review

❌ 3. LEARNING FEEDBACK LOOP
   │
   └─► Current: Meta-cognition reflects but doesn't update behavior
       Missing: Outcome tracking → Success analysis → Strategy update
       
       Should be:
       Action ──► Outcome ──► Evaluate ──► Update Strategy ──► Next Action

❌ 4. WORKING MEMORY INTEGRATION
   │
   └─► Current: All memory in long-term storage
       Missing: Short-term context buffer for active thinking
       
       Should be:
       Current Context ──► Working Memory ──► Active Reasoning ──► Long-term Storage

❌ 5. PRIORITY MANAGEMENT FLOW
   │
   └─► Current: Single action decision
       Missing: Interrupt handling, multi-goal management
       
       Should be:
       Multiple Goals ──► Priority Queue ──► Urgency Check ──► Interrupt Handler ──► Action

❌ 6. EMOTION-DRIVEN DECISION FLOW
   │
   └─► Current: Emotions mentioned but not used in decisions
       Missing: Emotional state → Decision weighting → Action filtering
       
       Should be:
       Emotional State ──► Affect Action Options ──► Weighted Decision ──► Action

❌ 7. TEMPORAL PLANNING FLOW
   │
   └─► Current: Immediate single action
       Missing: Multi-step plans over time
       
       Should be:
       Goal ──► Plan Steps ──► Schedule ──► Execute in Sequence ──► Monitor Progress

❌ 8. PATTERN LEARNING FLOW
   │
   └─► Current: Stores but doesn't learn patterns
       Missing: Pattern detection → Generalization → Application
       
       Should be:
       History ──► Pattern Detection ──► Strategy Formation ──► Apply to Similar Situations
```

---

## 5. DATABASE SCHEMA DETAILS

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        CHROMADB COLLECTION STRUCTURE                           │
└────────────────────────────────────────────────────────────────────────────────┘

Collection: "jenbina_conversations"
├─► Documents: Text content of messages
├─► Embeddings: Vector representations (384-dim from Ollama)
├─► IDs: MD5 hash of (person_name + content + timestamp)
└─► Metadata:
    ├─► sender_name: str
    ├─► receiver_name: str
    ├─► message_type: str ("user_message", "jenbina_response", "context")
    ├─► timestamp: str (ISO format)
    └─► embedding_id: str

Query Methods:
├─► retrieve_relevant_context(person_name, message, top_k)
├─► get_person_conversation_history(person_name, limit)
├─► get_conversation_between(sender, receiver, limit)
└─► search_similar_conversations(query, person_name, top_k)

┌────────────────────────────────────────────────────────────────────────────────┐
│                          NEO4J GRAPH STRUCTURE                                 │
└────────────────────────────────────────────────────────────────────────────────┘

Nodes:
├─► (:Person {name, first_met, relationship_strength, interaction_count, 
│              last_interaction, personality_traits, interests})
│
├─► (:Location {name, first_visited, visit_count, last_visit, associated_emotions})
│
├─► (:Event {event_id, timestamp, event_type, content})
│
└─► (:Action {name})

Relationships:
├─► (:Person)-[:PARTICIPATED_IN]->(:Event)
├─► (:Event)-[:OCCURRED_AT]->(:Location)
└─► (:Event)-[:INVOLVED_ACTION]->(:Action)

Constraints:
├─► UNIQUE person.name
├─► UNIQUE location.name
└─► UNIQUE event.event_id

┌────────────────────────────────────────────────────────────────────────────────┐
│                         SQLITE DATABASE STRUCTURE                              │
└────────────────────────────────────────────────────────────────────────────────┘

Table: events
├─► event_id TEXT PRIMARY KEY
├─► timestamp TEXT NOT NULL
├─► event_type TEXT NOT NULL
├─► content TEXT
├─► people TEXT (JSON array)
├─► locations TEXT (JSON array)
├─► actions TEXT (JSON array)
├─► emotions TEXT (JSON array)
├─► needs_state TEXT (JSON object)
└─► metadata TEXT (JSON object)

Table: needs_history
├─► timestamp TEXT NOT NULL
├─► need_name TEXT NOT NULL
├─► satisfaction_level REAL NOT NULL
└─► PRIMARY KEY (timestamp, need_name)

Table: person_interactions
├─► timestamp TEXT NOT NULL
├─► person_name TEXT NOT NULL
├─► interaction_type TEXT NOT NULL
├─► content TEXT
├─► emotion TEXT
└─► PRIMARY KEY (timestamp, person_name, interaction_type)
```

---

## 6. KEY INSIGHTS & ISSUES

### Current Strengths:
1. ✅ Rich entity model with comprehensive attributes
2. ✅ Multi-database hybrid memory system
3. ✅ Meta-cognitive monitoring and bias detection
4. ✅ Environment simulation with real-world data
5. ✅ Asimov safety checking

### Critical Gaps:
1. ❌ **No autonomous loop** - requires manual button clicks
2. ❌ **No goal persistence** - goals are ephemeral
3. ❌ **No learning mechanism** - insights don't affect future behavior
4. ❌ **No working memory** - all context is long-term
5. ❌ **No temporal planning** - only single-step decisions
6. ❌ **Needs decay is manual** - not time-based
7. ❌ **No attention management** - processes everything equally
8. ❌ **State analysis incomplete** - only returns hunger_level change

### Architecture Issues:
1. **engine.py is abandoned** - app.py has become the de-facto engine
2. **Simulation is one-shot** - no continuous operation
3. **Memory integration incomplete** - HybridMemorySystem not used in app.py
4. **Action execution missing** - decisions made but not executed on Person state
5. **No feedback loops** - decisions don't update strategies


