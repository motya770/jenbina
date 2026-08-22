# Graph Report - jenbina  (2026-08-22)

## Corpus Check
- Large corpus: 151 files · ~1,717,152 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 2598 nodes · 5350 edges · 136 communities (119 shown, 17 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 377 edges (avg confidence: 0.89)
- Token cost: 919,872 input · 0 output

## Community Hubs (Navigation)
- Inner Monologue System
- Greeting Generation Tests
- World State & Dynamic Events
- Cognition Chains & Simulation Runner
- ChromaDB Conversation Memory
- Meta-Cognition System
- Tamagotchi UI Simulation Page
- Person Class & Social Stats
- LLM Provider Connection
- Social Cognition Models
- Chain Integration Tests
- Maslow Needs System
- Chat UI & Emotion Analysis
- Insight System
- Curiosity System
- Legacy Person Tests
- Person Conversation Tests
- Learning System Extraction
- User Research Dossier
- Guardrail Injection Tests
- Learning Reinforcement Tests
- Self-Narrative Identity
- Greeting & Proactive Messages
- Hybrid Memory Storage
- README & Install Docs
- Conversation & Message Dataclasses
- Environment Simulator Tests
- Log Capture Utilities
- MaslowNeed Unit Tests
- Guardrails & System Messages
- Palo Alto Location System
- Chat Handler Metadata
- Goal System Generation
- Planning System Core
- Return Greeting Integration Tests
- Emotion Decay Tests
- Memory Integration Tests
- MaslowNeedsSystem Tests
- Environment Weather Simulator
- Experience Recording
- Working Memory Design
- Shared Session Init
- SQLite User Database
- Memory Integration Layer
- Social Interaction Tracker Tests
- EmotionSystem Tests
- Goal Decay Tests
- Goal System Design
- Temporal Memory Tests
- Action Decision Chain Tests
- Chat Interaction Handler Tests
- Legacy Need Class
- Plan & PlanStep Dataclasses
- Lesson Unit Tests
- Emotion System Core
- Chain Scenario Tests & ER Model
- Needs Summary & Growth
- Hybrid Memory Tests
- Lesson Formatting Tests
- Memory Event Models
- Working Memory Items & Salience
- LLM JSON Fixer
- BasicNeeds Container
- Sidebar & Environment Page
- Action Sprite Selection
- CI Workflows & Chain Test Runner
- Feedback Loop E2E Tests
- Plan Replan Tests
- Project Config & E2E Workflows
- Firebase Authentication
- Conversation Message Access
- Goal Progress & Milestone Tests
- BasicNeeds Compatibility Tests
- Conversation Unit Tests
- Social Interaction Tracker
- Emotion Sprite Selection
- Simulation E2E Tests
- App Entry & Simulation Loop
- Learning Serialization Tests
- Emotional Tone Inference
- Auth Page UI
- Message & Serialization Tests
- Working Memory Integration Tests
- Test Suite Runner & Guidelines
- Lesson Decay Tests
- Plan Creation & Replanning
- SocialInteraction Dataclass
- User CRUD Tests
- Emotion Dataclass & Decay
- Memory Integration Factory
- Social Interaction Recording
- Playwright E2E Fixtures
- Goal Lifecycle & Stats Tests
- Learning Stats Tests
- Plan Step Evaluation Tests
- User Message Storage Tests
- User DB Message Ordering
- First Greeting Generation
- Plan Step Execution
- Reading Sprite
- Talk Sprite
- Focus Calculation Tests
- Base Portrait Sprite
- Eating Sprite
- Smile Sprite
- Surprised Sprite
- Person State Persistence Tests
- Emotion Serialization
- Goal Serialization
- Admin Panel Page
- Deep Emotional Mirror Design
- Sad Sprite
- Sleep Sprite
- Thinking Sprite
- User Isolation Tests
- Favicon Mascot
- ChromaDB Clear Utility
- Goal Formatting Tests
- Plan Lifecycle Tests
- UserDatabase Init Tests
- Admin Message Count Tests
- Focus Noise Tests
- Context Switch Tests
- Needs Initialization
- Needs Update & Growth Stage
- Plan Serialization
- Working Memory Capacity
- Working Memory Serialization
- Working Memory Formatting
- Planning Stats

## God Nodes (most connected - your core abstractions)
1. `GoalSystem` - 82 edges
2. `Person` - 80 edges
3. `WorkingMemorySystem` - 72 edges
4. `PlanningSystem` - 66 edges
5. `InnerMonologueSystem` - 64 edges
6. `MaslowNeedsSystem` - 54 edges
7. `CLAUDE.md Project Instructions` - 47 edges
8. `generate_return_greeting()` - 44 edges
9. `Person` - 44 edges
10. `run_single_iteration()` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Goal System Design` --semantically_similar_to--> `create_maslow_goal_setter()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-07-goal-system-design.md → core/needs/maslow_decision_chain.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/ui/simulation.py
- `query_llm_knowledge() (planned function)` --semantically_similar_to--> `search_web()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md → core/research/user_research.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration_headless()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/simulation_runner.py
- `APScheduler (background scheduling)` --conceptually_related_to--> `run_simulation_loop()`  [AMBIGUOUS]
  requirements.txt → core/ui/simulation.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Simulation iteration LLM chain pipeline (needs -> world -> description -> action -> Asimov -> state)** — core_needs_maslow_needs_create_basic_needs_chain, core_environment_world_state_create_comprehensive_world_state, core_environment_world_state_create_world_description_system, core_cognition_enhanced_action_decision_chain_create_meta_cognitive_action_chain, core_cognition_action_decision_chain_create_action_decision_chain, core_cognition_asimov_check_chain_create_asimov_check_system, core_cognition_state_analysis_chain_create_state_analysis_system, core_ui_simulation_run_single_iteration [INFERRED 0.85]
- **Deep Emotional Mirror feature flow (research -> dossier -> insights -> greetings -> chat)** — core_research_user_research_research_user, core_research_user_research_generate_user_dossier, core_social_social_cognition_personmodel, core_insights_insight_system_insightsystem, core_interaction_chat_handler_handle_chat_interaction, core_interaction_chat_handler_generate_first_greeting, core_interaction_chat_handler_generate_return_greeting, core_ui_chat_check_return_greeting, core_ui_shared_init_init_session_state, core_ui_shared_init_init_llm, core_interaction_guardrails_jenbina_system_prompt [EXTRACTED 1.00]
- **Motivation-to-action stack injected into the action decision prompt (working memory, plan step, goals, lessons)** — core_working_memory_working_memory_system_workingmemorysystem, core_planning_planning_system_planningsystem, core_goals_goal_system_goalsystem, core_learning_learning_system_learningsystem, core_needs_maslow_needs_maslowneedssystem, core_cognition_action_decision_chain_create_action_decision_chain [INFERRED 0.85]
- **Jenbina Visual Identity (pink blob mascot, happy expression, Tamagotchi styling)** — assets_favicon, assets_favicon_jenbina_blob_character, assets_favicon_content_happy_expression, assets_favicon_tamagotchi_mascot_design [INFERRED 0.85]
- **Emotion-driven avatar selection in the Tamagotchi UI** — core_ui_simulation_get_jenbina_image_for_emotion, src_images_jenbina_angry_anger_emotional_state, src_images_jenbina_angry, src_images_jenbina_angry_emotion_avatar_sprite_set [EXTRACTED 1.00]
- **Jenbina Base Portrait Composition** — src_images_jenbina_base_jenbina_character, src_images_jenbina_base_space_helmet_and_suit, src_images_jenbina_base_all_seeing_eye_pendant, src_images_jenbina_base_cosmic_backdrop, src_images_jenbina_base_retro_space_age_style [EXTRACTED 1.00]
- **Thirst Need Visual Feedback Flow** — core_needs_maslow_needs_maslowneedssystem, core_ui_simulation_get_jenbina_image_for_action, src_images_jenbina_drink_drinking_action_state, src_images_jenbina_drink [INFERRED 0.85]
- **Jenbina eating sprite: persona + eating action + retro space styling form one Tamagotchi state image** — src_images_jenbina_eat, src_images_jenbina_eat_jenbina_character, src_images_jenbina_eat_eating_state, src_images_jenbina_eat_retro_space_aesthetic [INFERRED 0.85]
- **Visual elements composing the Jenbina 'reading' character state** — src_images_jenbina_read_retro_astronaut_persona, src_images_jenbina_read_content_absorbed_expression, src_images_jenbina_read_cosmic_book, src_images_jenbina_read_eye_in_triangle_pendant, src_images_jenbina_read_reading_state [INFERRED 0.85]
- **Jenbina Sad-Mood Avatar Composition** — src_images_jenbina_sad, src_images_jenbina_sad_jenbina_astronaut_persona, src_images_jenbina_sad_sad_emotional_state, src_images_jenbina_sad_retro_sci_fi_space_setting [INFERRED 0.85]
- **Fear emotion to frightened-portrait selection flow** — core_ui_simulation_get_jenbina_image_for_emotion, src_images_jenbina_scary_fear_state, src_images_jenbina_scary, src_images_jenbina_scary_emotion_sprite_set [INFERRED 0.85]
- **Jenbina Sleep-State Character Art Composition** — src_images_jenbina_sleep, src_images_jenbina_sleep_jenbina_astronaut_persona, src_images_jenbina_sleep_sleeping_state, src_images_jenbina_sleep_spaceship_cabin_setting, src_images_jenbina_sleep_vintage_scifi_art_style [INFERRED 0.85]
- **Jenbina smiling portrait as an emotion-keyed avatar state** — src_images_jenbina_smile, src_images_jenbina_smile_jenbina_character, src_images_jenbina_smile_happy_emotional_state, src_images_jenbina_smile_avatar_state_sprite [INFERRED 0.75]
- **Surprised-Reaction Scene: Character + Stimulus + Expression** — src_images_jenbina_surprised_jenbina_character, src_images_jenbina_surprised_ufo_tractor_beam, src_images_jenbina_surprised_surprised_expression, src_images_jenbina_surprised_retro_scifi_art_style [INFERRED 0.75]
- **Jenbina Conversation Scene (two figures, whisper gesture, joyful expressions)** — src_images_jenbina_talk_two_women_conversing, src_images_jenbina_talk_whisper_gesture, src_images_jenbina_talk_joyful_expression, src_images_jenbina_talk_chat_state [INFERRED 0.85]
- **Jenbina 'thinking' state illustration: persona + thinking pose + awareness pendant + retro space aesthetic** — src_images_jenbina_thinking_jenbina_persona, src_images_jenbina_thinking_thinking_pose, src_images_jenbina_thinking_all_seeing_eye_pendant, src_images_jenbina_thinking_retro_space_age_aesthetic [INFERRED 0.85]
- **Action-driven sprite display flow (walking)** — core_ui_simulation_get_jenbina_image_for_action, src_images_jenbina_walks_action_sprite_mapping, src_images_jenbina_walks_walking_exploration_state, src_images_jenbina_walks [INFERRED 0.85]

## Communities (136 total, 17 thin omitted)

### Community 0 - "Inner Monologue System"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "Greeting Generation Tests"
Cohesion: 0.06
Nodes (34): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+26 more)

### Community 2 - "World State & Dynamic Events"
Cohesion: 0.07
Nodes (36): DynamicEventsSystem, Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API (+28 more)

### Community 3 - "Cognition Chains & Simulation Runner"
Cohesion: 0.08
Nodes (39): callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, create_meta_cognitive_action_chain(), Enhanced action decision with meta-cognitive monitoring (+31 more)

### Community 4 - "ChromaDB Conversation Memory"
Cohesion: 0.06
Nodes (28): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+20 more)

### Community 5 - "Meta-Cognition System"
Cohesion: 0.08
Nodes (20): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+12 more)

### Community 6 - "Tamagotchi UI Simulation Page"
Cohesion: 0.09
Nodes (45): _detect_location_from_action(), display_curiosity_stats(), display_goal_stats(), display_identity_stats(), display_learning_stats(), display_meta_cognitive_insights(), display_person_state(), display_planning_stats() (+37 more)

### Community 7 - "Person Class & Social Stats"
Cohesion: 0.06
Nodes (20): Person, Any, Initialize social interaction tracker., Update all needs, decay emotions, and decay lessons, Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Start a new conversation with an outsider, Receive a message from an outsider (+12 more)

### Community 8 - "LLM Provider Connection"
Cohesion: 0.09
Nodes (25): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_local_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service… (+17 more)

### Community 9 - "Social Cognition Models"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., Choose when to be nice, polite, or assertive. (+7 more)

### Community 10 - "Chain Integration Tests"
Cohesion: 0.05
Nodes (22): create_basic_needs_chain(), Legacy function for backward compatibility - now uses Maslow decision system, Test error recovery and graceful degradation in chains, Test chain performance with multiple rapid calls, Test chains with different person states, Test that chains produce consistent results with same inputs, Test memory usage of chains, Test the Asimov compliance check system (+14 more)

### Community 11 - "Maslow Needs System"
Cohesion: 0.10
Nodes (27): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+19 more)

### Community 12 - "Chat UI & Emotion Analysis"
Cohesion: 0.10
Nodes (35): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, check_proactive_message(), check_return_greeting(), display_communication_stats(), display_conversation_history(), display_memory_debug(), display_memory_stats() (+27 more)

### Community 13 - "Insight System"
Cohesion: 0.11
Nodes (12): InsightSystem, Any, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Check if conditions are met to generate a subtle insight. Always returns True…, Generate a subtle perceptive observation about the user. Returns the insight…, Reset the per-session counter (call on new session start)., Generates deep perceptive observations about users mid-conversation., Check if we should fire the bold first-impression insight. (+4 more)

### Community 14 - "Curiosity System"
Cohesion: 0.10
Nodes (9): CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., Initialize curiosity / exploration system., TestCuriositySystem (+1 more)

### Community 15 - "Legacy Person Tests"
Cohesion: 0.09
Nodes (11): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+3 more)

### Community 16 - "Person Conversation Tests"
Cohesion: 0.06
Nodes (18): Test Person functionality, Test person initialization, Test person with default name, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider, Test getting conversation history (+10 more)

### Community 17 - "Learning System Extraction"
Cohesion: 0.09
Nodes (19): Learning system for Jenbina - extracts lessons from experiences, LearningSystem, Any, Learning system for Jenbina — records experiences, extracts lessons, and…, Records experiences, extracts lessons via LLM, and formats them for prompts., Decay all lessons and prune dead ones., make_mock_llm(), Test LLM-based lesson extraction (+11 more)

### Community 18 - "User Research Dossier"
Cohesion: 0.12
Nodes (22): build_search_query(), generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,…, Build a web search query from user info., Call the SerpAPI web search API (serpapi.com). Returns raw JSON response from… (+14 more)

### Community 19 - "Guardrail Injection Tests"
Cohesion: 0.11
Nodes (4): Tier 1 BLOCK patterns should return (True, *)., Tier 2 WARN patterns should return (False, True)., TestCheckInjectionBlock, TestCheckInjectionWarn

### Community 20 - "Learning Reinforcement Tests"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "Self-Narrative Identity"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "Greeting & Proactive Messages"
Cohesion: 0.15
Nodes (8): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateProactiveMessage, TestGenerateReturnGreeting

### Community 23 - "Hybrid Memory Storage"
Cohesion: 0.08
Nodes (18): HybridMemorySystem, Any, datetime, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID (+10 more)

### Community 24 - "README & Install Docs"
Cohesion: 0.14
Nodes (31): Layered Architecture (UI -> Interaction -> Cognition -> Core -> DB -> LLM), Current Architecture Diagrams, Database Schemas (Chroma collection, Neo4j graph, SQLite tables), Installation Guide, Environment API Keys (Eventbrite, Ticketmaster, Yelp, Google Places), LangSmith Tracing (optional env vars), Neo4j Docker Setup (optional, neo4j:5.17.0 with APOC), Ollama Local LLM Setup (llama3.2:3b-instruct-fp16) (+23 more)

### Community 25 - "Conversation & Message Dataclasses"
Cohesion: 0.09
Nodes (16): Person Management Submodule This submodule handles the AI's person…, Conversation, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation (+8 more)

### Community 26 - "Environment Simulator Tests"
Cohesion: 0.11
Nodes (10): Calculate how environment affects mood, TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator (+2 more)

### Community 27 - "Log Capture Utilities"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "MaslowNeed Unit Tests"
Cohesion: 0.08
Nodes (16): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy, Increase satisfaction by given amount, Test low status detection (+8 more)

### Community 29 - "Guardrails & System Messages"
Cohesion: 0.11
Nodes (17): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+9 more)

### Community 30 - "Palo Alto Location System"
Cohesion: 0.08
Nodes (16): PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type, Get locations within a certain radius of current location (+8 more)

### Community 31 - "Chat Handler Metadata"
Cohesion: 0.12
Nodes (11): basic_needs_to_json(), _build_subsystem_context(), create_metadata_from_person_state(), Convert BasicNeeds object to JSON-serializable format, Create metadata dictionary from person state and other context, Extract formatted context from all person subsystems. Returns a list of (label,…, Interaction and Communication Submodule This submodule handles all aspects of…, Tests for core/interaction/chat_handler.py — chat orchestration. (+3 more)

### Community 32 - "Goal System Generation"
Cohesion: 0.11
Nodes (7): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., TestGoalSystem, TestGoalSystemGeneration

### Community 33 - "Planning System Core"
Cohesion: 0.17
Nodes (9): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., Planning System Design, Multi-step Chain-of-Thought Planning, Plan Step Completion Detection & Replan Trigger, make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation (+1 more)

### Community 34 - "Return Greeting Integration Tests"
Cohesion: 0.12
Nodes (15): dict, _FakeSessionState, patch, Dict subclass that also supports attribute-style access, like Streamlit's…, Tests for check_return_greeting in chat.py with llm parameter., Without LLM, first visit (last_visit_time=None) returns None., Without LLM, static greetings are returned (backward compat)., Calling without llm argument uses default None (backward compat). (+7 more)

### Community 35 - "Emotion Decay Tests"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "Memory Integration Tests"
Cohesion: 0.07
Nodes (14): Test storing action memory, Test storing need change memory, Test MemoryIntegration functionality, Test getting relevant context for a query, Test getting context for a specific person, Test getting recent memories, Test getting recent memories with event type filter, Test getting needs trends (+6 more)

### Community 37 - "MaslowNeedsSystem Tests"
Cohesion: 0.08
Nodes (13): Test the complete Maslow needs system, Test system initialization with all needs, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs, Test getting priority needs (+5 more)

### Community 38 - "Environment Weather Simulator"
Cohesion: 0.11
Nodes (13): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Get local events based on Palo Alto location system, Get a natural language description of the current environment (+5 more)

### Community 39 - "Experience Recording"
Cohesion: 0.11
Nodes (12): Experience, Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set, Test that world_context defaults to empty dict, Test Experience dataclass (+4 more)

### Community 40 - "Working Memory Design"
Cohesion: 0.14
Nodes (7): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestSalienceScoring

### Community 41 - "Shared Session Init"
Cohesion: 0.15
Nodes (19): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Streamlit session_state Persistence, Superpowers executing-plans Workflow, Jenbina — Console Log page., Jenbina — Debug Info page., UI components for Jenbina Streamlit app, init_llm(), init_session_state() (+11 more)

### Community 42 - "SQLite User Database"
Cohesion: 0.12
Nodes (12): Connection, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first., Return all users with their total and per-sender message counts. (+4 more)

### Community 43 - "Memory Integration Layer"
Cohesion: 0.12
Nodes (15): example_usage(), MemoryIntegration, Any, Person, Integrates the hybrid memory system with Jenbina's existing components, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person… (+7 more)

### Community 45 - "EmotionSystem Tests"
Cohesion: 0.08
Nodes (13): Test EmotionSystem functionality, Should initialize with 8 Plutchik emotions, Check Jenbina's character baselines, Initially, intensity should equal base_intensity, Should spike the named emotion, Triggering unknown emotion should be a no-op, Should apply multiple adjustments at once, Should return top-k emotions by intensity (+5 more)

### Community 46 - "Goal Decay Tests"
Cohesion: 0.15
Nodes (3): make_goal(), TestGoal, TestGoalSystemDecay

### Community 47 - "Goal System Design"
Cohesion: 0.10
Nodes (11): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals) (+3 more)

### Community 48 - "Temporal Memory Tests"
Cohesion: 0.09
Nodes (12): Update need satisfaction over time, Test temporal memory retrieval, Test temporal memory retrieval with event type filter, Test needs history retrieval, Test getting history for all needs, Test updating all needs over time, Test need satisfaction decay over time, Test storing action memory with people and location (+4 more)

### Community 49 - "Action Decision Chain Tests"
Cohesion: 0.13
Nodes (13): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for core/cognition/action_decision_chain.py., Tests for the prompt template definitions. (+5 more)

### Community 50 - "Chat Interaction Handler Tests"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "Legacy Need Class"
Cohesion: 0.10
Nodes (12): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Test the legacy Need class, Test legacy Need initialization (+4 more)

### Community 52 - "Plan & PlanStep Dataclasses"
Cohesion: 0.15
Nodes (8): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., An ordered sequence of steps to achieve a goal., make_step(), Tests for the planning system., TestPlanStep

### Community 53 - "Lesson Unit Tests"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "Emotion System Core"
Cohesion: 0.12
Nodes (10): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Decay all emotions toward their baselines based on elapsed time., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}. (+2 more)

### Community 55 - "Chain Scenario Tests & ER Model"
Cohesion: 0.10
Nodes (12): WorldState, ConversationMemory, Represents a conversation memory entry, Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition), Test chains with realistic scenarios, Test chains in a morning routine scenario, Test chains in a stressful situation, Test chains in a creative work scenario (+4 more)

### Community 56 - "Needs Summary & Growth"
Cohesion: 0.11
Nodes (11): Any, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization, Create from dictionary (+3 more)

### Community 57 - "Hybrid Memory Tests"
Cohesion: 0.10
Nodes (11): Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test memory statistics, Test person relationships when Neo4j is not available, Test error handling in memory operations, Test that memories persist across system restarts, Test HybridMemorySystem functionality (+3 more)

### Community 58 - "Lesson Formatting Tests"
Cohesion: 0.12
Nodes (9): Lesson, A learned pattern extracted from experiences., Test format_lessons_for_prompt, No lessons should return default message, Active lessons should appear in formatted text, Lessons should be sorted by confidence descending, Inactive lessons should not appear, Should show at most 10 lessons (+1 more)

### Community 59 - "Memory Event Models"
Cohesion: 0.16
Nodes (12): LocationNode, MemoryEvent, PersonNode, Represents a memory event with all its components, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, Memory Integration Module Shows how to integrate the hybrid memory system with… (+4 more)

### Community 60 - "Working Memory Items & Salience"
Cohesion: 0.17
Nodes (6): Any, Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., Recalculate working memory from current state. Called once per cycle., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "LLM JSON Fixer"
Cohesion: 0.20
Nodes (8): fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function., TestFixLlmJson

### Community 62 - "BasicNeeds Container"
Cohesion: 0.12
Nodes (9): BasicNeeds, Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Legacy needs property that maps to Maslow needs, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Add a new need to the system (+1 more)

### Community 63 - "Sidebar & Environment Page"
Cohesion: 0.18
Nodes (16): Jenbina — Environment & Debug page., Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar (+8 more)

### Community 64 - "Action Sprite Selection"
Cohesion: 0.16
Nodes (18): _get_image_path(), get_jenbina_image_for_action(), Get absolute path to a Jenbina image., Determine which Jenbina image to show based on the chosen action., Jenbina Drink Illustration, Action-to-Sprite Mapping for Tamagotchi UI, All-Seeing Eye Pendant Motif, Calm Content Expression (Sideways Glance, Slight Smile) (+10 more)

### Community 65 - "CI Workflows & Chain Test Runner"
Cohesion: 0.18
Nodes (15): .coveragerc coverage config, GitHub Actions Workflows README, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action), Test Suite Workflow (push/manual), GitHub Actions CI/CD, pytest / pytest-cov / pytest-playwright / pytest-timeout (+7 more)

### Community 66 - "Feedback Loop E2E Tests"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "Plan Replan Tests"
Cohesion: 0.22
Nodes (3): make_plan(), TestPlan, TestPlanningSystemReplan

### Community 68 - "Project Config & E2E Workflows"
Cohesion: 0.23
Nodes (12): .env.example template, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, CLAUDE.md Project Instructions, Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), Environment Variables (.env / .env.example), Firebase Auth + Google OAuth (+4 more)

### Community 69 - "Firebase Authentication"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation Message Access"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "Goal Progress & Milestone Tests"
Cohesion: 0.30
Nodes (4): make_experience(), make_mock_llm(), TestGoalSystemMilestone, TestGoalSystemProgress

### Community 72 - "BasicNeeds Compatibility Tests"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 73 - "Conversation Unit Tests"
Cohesion: 0.13
Nodes (8): Test that last_interaction updates when adding messages, Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, TestConversation

### Community 74 - "Social Interaction Tracker"
Cohesion: 0.24
Nodes (7): Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts., Tracks all of Jenbina's social interactions during the session. Only the…, SocialInteractionTracker

### Community 75 - "Emotion Sprite Selection"
Cohesion: 0.21
Nodes (14): get_jenbina_image_for_emotion(), Determine which Jenbina image to show based on dominant emotion., jenbina_angry.png (Jenbina angry-state portrait), All-seeing eye medallion (eye-in-triangle pendant), Anger emotional state (shouting, furrowed brows, bared teeth), Jenbina emotion/action avatar sprite set (jenbina_*.png), Jenbina character (retro space-age woman in bubble helmet), Retro-futuristic pulp sci-fi art style (+6 more)

### Community 76 - "Simulation E2E Tests"
Cohesion: 0.18
Nodes (10): fixture, Page, Playwright E2E test — run a single simulation iteration and verify each stage…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the simulation page loads and shows controls., Click 'Run Single Iteration' and verify key Tamagotchi UI elements appear…, After running, the simulation summary section should appear. (+2 more)

### Community 77 - "App Entry & Simulation Loop"
Cohesion: 0.22
Nodes (11): main(), Jenbina - AGI Simulation Streamlit App Main entry point — Simulation page., display_jenbina_image(), display_simulation_summary(), Run the simulation loop for specified iterations, Display summary of simulation history, Render simulation control UI and return settings (designed for sidebar), Display a Jenbina image in the UI if the file exists. (+3 more)

### Community 78 - "Learning Serialization Tests"
Cohesion: 0.18
Nodes (6): Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 79 - "Emotional Tone Inference"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Auth Page UI"
Cohesion: 0.21
Nodes (11): _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only., Show logged-in user info and a logout button in the sidebar., Return path to Google credentials file. Locally, reads…, Return the OAuth redirect URI. Uses the ``REDIRECT_URI`` env var if set…, Return a shared UserDatabase instance via session state. (+3 more)

### Community 81 - "Message & Serialization Tests"
Cohesion: 0.17
Nodes (6): Test Message functionality, Conversations must survive serialize/deserialize (regression: used to be…, Test message initialization, Test message with default values, TestMessage, TestPersonSerializeConversations

### Community 82 - "Working Memory Integration Tests"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "Test Suite Runner & Guidelines"
Cohesion: 0.25
Nodes (8): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), Run a specific test module, run_specific_test(), Run all tests and provide comprehensive reporting, run_comprehensive_tests()

### Community 84 - "Lesson Decay Tests"
Cohesion: 0.18
Nodes (6): Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, TestLearningSystemDecay

### Community 85 - "Plan Creation & Replanning"
Cohesion: 0.20
Nodes (5): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id.

### Community 86 - "SocialInteraction Dataclass"
Cohesion: 0.29
Nodes (4): Any, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, TestSocialInteraction

### Community 87 - "User CRUD Tests"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 88 - "Emotion Dataclass & Decay"
Cohesion: 0.25
Nodes (4): Emotion, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "Memory Integration Factory"
Cohesion: 0.28
Nodes (6): create_memory_integration(), Create a memory integration instance with default settings Returns:…, Test memory integration factory functions, Test creating memory integration with default settings, Test creating memory integration with custom paths, TestMemoryIntegrationFactory

### Community 90 - "Social Interaction Recording"
Cohesion: 0.25
Nodes (4): Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Generate a simple automatic sentiment string., Try to extract a person/entity name from a simulated action string. The action…

### Community 91 - "Playwright E2E Fixtures"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 92 - "Goal Lifecycle & Stats Tests"
Cohesion: 0.22
Nodes (4): Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemIntegration, TestGoalSystemStats

### Community 93 - "Learning Stats Tests"
Cohesion: 0.22
Nodes (5): Test get_learning_stats, Empty system should return zero counts, Stats should reflect recorded data, recent_experiences should show at most 5, TestLearningSystemStats

### Community 96 - "User DB Message Ordering"
Cohesion: 0.25
Nodes (3): SQLite user database for authentication and conversation persistence., Same-second writes must be deterministic by id tiebreaker., TestMessageOrdering

### Community 97 - "First Greeting Generation"
Cohesion: 0.39
Nodes (3): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting

### Community 98 - "Plan Step Execution"
Cohesion: 0.25
Nodes (3): Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Mark current step completed and move to next.

### Community 99 - "Reading Sprite"
Cohesion: 0.43
Nodes (8): Jenbina Reading Illustration (jenbina_read.png), Calm, Content, Absorbed Expression (eyes lowered to book, gentle smile), Open Book Showing Planet and Comet (cosmic knowledge motif), Eye-in-Triangle Pendant (awareness / consciousness symbol), Jenbina Reading / Learning Activity State, Retro Sci-Fi Astronaut Persona (bubble helmet, 1960s hairstyle, pearl earrings), Spaceship Interior and Starry Space Backdrop (planet, rocket, control panel, alien terrain), Vintage Sepia/Gold Pulp Illustration Style

### Community 100 - "Talk Sprite"
Cohesion: 0.43
Nodes (8): Jenbina Talk Illustration, Jenbina Talking / Chat State, Eye-in-Triangle Pendant Symbol, Joyful Smiling Expressions, Retro Pulp Sci-Fi Art Style (Sepia/Gold), Spacecraft Interior with Porthole (Planet, Stars, Rocket), Two Women in Retro Spacesuits Conversing, Hand-Cupped Whisper / Confiding Gesture

### Community 101 - "Focus Calculation Tests"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "Base Portrait Sprite"
Cohesion: 0.43
Nodes (7): jenbina_base.png (Jenbina base portrait image), All-Seeing-Eye Pendant (eye-in-triangle medallion), Cosmic Backdrop (planet, rocket, spired city, stars), Jenbina Character (avatar persona), Neutral Baseline Expression (calm, confident gaze), Retro-Futuristic Space-Age Art Style, Glass Bubble Helmet and Silver Spacesuit

### Community 103 - "Eating Sprite"
Cohesion: 0.43
Nodes (7): Jenbina Eating Illustration (jenbina_eat.png), All-Seeing Eye Pendant (eye-in-triangle medallion on spacesuit collar), Eating State (Jenbina biting a cheeseburger, content half-smile, eyes glancing sideways), Hunger / Physiological Need Satisfaction, Jenbina Persona (retro space-age woman in glass-dome helmet and silver spacesuit), Retro Pulp Sci-Fi Aesthetic (1960s space-age: bouffant hair, rocket, starfield, planet, spired city), Tamagotchi State Sprite (per-activity character art for the persona UI)

### Community 104 - "Smile Sprite"
Cohesion: 0.48
Nodes (7): jenbina_smile.png (Jenbina smiling portrait), All-Seeing Eye Pendant (awareness / consciousness symbol), Emotion-Keyed Avatar Portrait (Tamagotchi UI state image), Happy / Smiling Emotional State, Jenbina Character (retro space-age woman in bubble helmet), Retro-Futurist 1960s Pulp Sci-Fi Aesthetic, Space Scene Backdrop (planet, stars, rocket, futuristic spires)

### Community 105 - "Surprised Sprite"
Cohesion: 0.52
Nodes (6): All-Seeing Eye Pendant, Emotion-Based Persona Avatar Set, Jenbina Character (Space-Suited Persona), Retro Pulp Sci-Fi Art Style, Surprised Emotional State, UFO with Tractor Beam (Surprise Stimulus)

### Community 107 - "Emotion Serialization"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 109 - "Admin Panel Page"
Cohesion: 0.40
Nodes (5): _is_admin(), _is_local_request(), Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, Check if the request originates from localhost., Return True if the current visitor is allowed to see the admin panel.

### Community 110 - "Deep Emotional Mirror Design"
Cohesion: 0.60
Nodes (6): Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals

### Community 111 - "Sad Sprite"
Cohesion: 0.53
Nodes (6): Jenbina Sad Avatar Image, All-Seeing Eye Pendant (eye-in-triangle medallion, awareness symbol), Jenbina Retro-Futurist Astronaut Persona, Retro Sci-Fi Space Setting (glass bubble helmet, rocket, moon, starfield, spire city), Sad / Worried Emotional State (furrowed brows, downcast expression), Tamagotchi Mood Sprite (avatar variant keyed to emotional state)

### Community 112 - "Sleep Sprite"
Cohesion: 0.53
Nodes (6): jenbina_sleep.png (Jenbina Sleeping Illustration), Jenbina as Retro-Futurist Astronaut Character, Peaceful Contentment Expression (eyes closed, slight smile), Jenbina Sleeping / Resting State, Spaceship Cabin Setting (porthole, planet, stars, rocket), Vintage Pulp Sci-Fi Illustration Style

### Community 113 - "Thinking Sprite"
Cohesion: 0.47
Nodes (6): Jenbina Thinking (character illustration), All-Seeing Eye Pendant (eye-in-triangle medallion, symbol of awareness/cognition), Jenbina Persona (retro space-age woman in glass helmet and silver spacesuit), Persona Thinking State (visual indicator that Jenbina is deliberating / processing), Retro Space-Age Aesthetic (1960s pulp sci-fi: stars, planet, rocket, futuristic spires, painterly texture), Thinking Pose (finger to cheek, upward gaze, contemplative smile)

### Community 115 - "Favicon Mascot"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "ChromaDB Clear Utility"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 118 - "Plan Lifecycle Tests"
Cohesion: 0.40
Nodes (3): Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete., TestPlanningSystemIntegration

### Community 121 - "Focus Noise Tests"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls
- `run_simulation_loop()` → `APScheduler (background scheduling)`  [AMBIGUOUS]
  requirements.txt · relation: conceptually_related_to
- `Jenbina character (retro space-age woman in bubble helmet)` → `All-seeing eye medallion (eye-in-triangle pendant)`  [AMBIGUOUS]
  src/images/jenbina_angry.png · relation: conceptually_related_to
- `Jenbina Character (avatar persona)` → `All-Seeing-Eye Pendant (eye-in-triangle medallion)`  [AMBIGUOUS]
  src/images/jenbina_base.png · relation: rationale_for
- `Jenbina Persona (retro space-age woman in glass-dome helmet and silver spacesuit)` → `All-Seeing Eye Pendant (eye-in-triangle medallion on spacesuit collar)`  [AMBIGUOUS]
  src/images/jenbina_eat.png · relation: conceptually_related_to
- `Retro Pulp Sci-Fi Illustration Style` → `All-Seeing Eye Pendant`  [AMBIGUOUS]
  src/images/jenbina_scary.png · relation: conceptually_related_to
- `Eye-in-Triangle Pendant Symbol` → `Jenbina Talking / Chat State`  [AMBIGUOUS]
  src/images/jenbina_talk.png · relation: conceptually_related_to

## Knowledge Gaps
- **10 isolated node(s):** `Matthew Kudelin (creator)`, `Pytest Coverage PR Comment (MishaKav action)`, `.coveragerc coverage config`, `Streamlit Page Icon / Browser Tab Favicon`, `Retro-futuristic pulp sci-fi art style` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `run_simulation_loop()` and `APScheduler (background scheduling)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Jenbina character (retro space-age woman in bubble helmet)` and `All-seeing eye medallion (eye-in-triangle pendant)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Jenbina Character (avatar persona)` and `All-Seeing-Eye Pendant (eye-in-triangle medallion)`?**
  _Edge tagged AMBIGUOUS (relation: rationale_for) - confidence is low._
- **What is the exact relationship between `Jenbina Persona (retro space-age woman in glass-dome helmet and silver spacesuit)` and `All-Seeing Eye Pendant (eye-in-triangle medallion on spacesuit collar)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Retro Pulp Sci-Fi Illustration Style` and `All-Seeing Eye Pendant`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Eye-in-Triangle Pendant Symbol` and `Jenbina Talking / Chat State`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._