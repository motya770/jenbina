# Graph Report - jenbina  (2026-10-27)

## Corpus Check
- 143 files · ~1,536,853 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2675 nodes · 5544 edges · 125 communities (111 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 344 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `84af532e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_person
- DynamicEventsSystem
- CLAUDE.md Project Instructions
- generate_first_greeting
- MetaCognitiveSystem
- simulation.py
- Person
- create_basic_needs_chain
- SocialCognitionSystem
- simulation_runner.py
- timedelta
- shared_init.py
- InsightSystem
- CuriositySystem
- Person
- TestPerson
- LearningSystem
- Deep Emotional Mirror Implementation Plan
- BasicNeeds
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- MemoryEvent
- EnvironmentSimulator
- .get_needs_summary
- TestEnvironmentSimulator
- StreamCapture
- generate_proactive_message
- get_llm
- PaloAltoLocationSystem
- create_metadata_from_person_state
- GoalSystem
- PlanningSystem
- _FakeSessionState
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- Conversation
- Experience
- WorkingMemorySystem
- sidebar.py
- UserDatabase
- MemoryIntegration
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- TestCheckInjectionBlock
- handle_chat_interaction
- maslow_needs.py
- Plan
- TestLesson
- .get_dominant_emotions
- core/__init__.py
- create_action_decision_chain
- TestHybridMemorySystem
- Lesson
- TestUserCRUD
- WorkingMemoryItem
- _invoke_and_parse
- TestChainEdgeCases
- fix_llm_json
- NoveltyEvent
- test_sprites.py
- _run_one_iteration
- make_plan
- TestLearningSystemStats
- FirebaseAuth
- Conversation
- make_mock_llm
- .add_conversation
- TestConversation
- SocialInteractionTracker
- MaslowNeedsSystem
- test_simulation.py
- File Structure
- TestLearningSystemSerialization
- infer_emotional_tone
- Design
- Message
- test_working_memory.py
- Run Unit Tests Workflow (PR gate)
- TestLearningSystemDecay
- test_pixel_ui.py
- test_person.py
- .get_communication_stats
- EmotionSystem
- .add_conversation
- .apply_adjustments
- streamlit_server
- test_goal_system.py
- SocialInteraction
- HybridMemorySystem
- _build_subsystem_context
- make_experience
- create_memory_integration
- .get_current_step
- TestGoalSystemFormatting
- TestPersonSerializeConversations
- make_needs
- .get_planning_stats
- .create_plan
- Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)
- TestPersonCuriositySerialization
- .from_dict
- .from_dict
- .from_dict
- chat.py
- Jenbina Blob Character
- clear_chromadb.py
- .test_full_plan_lifecycle
- TestFocusNoise
- TestContextSwitch
- ._get_capacity
- .from_dict
- MaslowNeed
- TestFormatting

## God Nodes (most connected - your core abstractions)
1. `GoalSystem` - 82 edges
2. `Person` - 80 edges
3. `WorkingMemorySystem` - 72 edges
4. `PlanningSystem` - 66 edges
5. `InnerMonologueSystem` - 64 edges
6. `MaslowNeedsSystem` - 53 edges
7. `CLAUDE.md Project Instructions` - 47 edges
8. `run_single_iteration()` - 45 edges
9. `generate_return_greeting()` - 44 edges
10. `Person` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Goal System Design` --semantically_similar_to--> `create_maslow_goal_setter()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-07-goal-system-design.md → core/needs/maslow_decision_chain.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration_headless()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/simulation_runner.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/ui/simulation.py
- `query_llm_knowledge() (planned function)` --semantically_similar_to--> `search_web()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md → core/research/user_research.py
- `APScheduler (background scheduling)` --conceptually_related_to--> `run_simulation_loop()`  [AMBIGUOUS]
  requirements.txt → core/ui/simulation.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Deep Emotional Mirror feature flow (research -> dossier -> insights -> greetings -> chat)** — core_research_user_research_research_user, core_research_user_research_generate_user_dossier, core_social_social_cognition_personmodel, core_insights_insight_system_insightsystem, core_interaction_chat_handler_handle_chat_interaction, core_interaction_chat_handler_generate_first_greeting, core_interaction_chat_handler_generate_return_greeting, core_ui_chat_check_return_greeting, core_ui_shared_init_init_session_state, core_ui_shared_init_init_llm, core_interaction_guardrails_jenbina_system_prompt [EXTRACTED 1.00]
- **Jenbina Visual Identity (pink blob mascot, happy expression, Tamagotchi styling)** — assets_favicon, assets_favicon_jenbina_blob_character, assets_favicon_content_happy_expression, assets_favicon_tamagotchi_mascot_design [INFERRED 0.85]
- **Motivation-to-action stack injected into the action decision prompt (working memory, plan step, goals, lessons)** — core_working_memory_working_memory_system_workingmemorysystem, core_planning_planning_system_planningsystem, core_goals_goal_system_goalsystem, core_learning_learning_system_learningsystem, core_needs_maslow_needs_maslowneedssystem, core_cognition_action_decision_chain_create_action_decision_chain [INFERRED 0.85]
- **Simulation iteration LLM chain pipeline (needs -> world -> description -> action -> Asimov -> state)** — core_needs_maslow_needs_create_basic_needs_chain, core_environment_world_state_create_comprehensive_world_state, core_environment_world_state_create_world_description_system, core_cognition_enhanced_action_decision_chain_create_meta_cognitive_action_chain, core_cognition_action_decision_chain_create_action_decision_chain, core_cognition_asimov_check_chain_create_asimov_check_system, core_cognition_state_analysis_chain_create_state_analysis_system, core_ui_simulation_run_single_iteration [INFERRED 0.85]

## Communities (125 total, 14 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "_make_mock_person"
Cohesion: 0.09
Nodes (24): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+16 more)

### Community 2 - "DynamicEventsSystem"
Cohesion: 0.11
Nodes (14): DynamicEventsSystem, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API, Flexible system to fetch real-time events and venue information (+6 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.12
Nodes (39): .env.example template, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, CLAUDE.md Project Instructions, Environment Variables (.env / .env.example), Layered Architecture (UI -> Interaction -> Cognition -> Core -> DB -> LLM), Current Architecture Diagrams (+31 more)

### Community 4 - "generate_first_greeting"
Cohesion: 0.10
Nodes (14): generate_first_greeting(), Generate a personalized first greeting for a new user., Tests for core/interaction/chat_handler.py — chat orchestration., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier. (+6 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.06
Nodes (25): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+17 more)

### Community 6 - "simulation.py"
Cohesion: 0.06
Nodes (69): main(), Jenbina - AGI Simulation Streamlit App Main entry point — Simulation page., get_world_state_summary(), Any, Get a comprehensive summary of the world state for display or processing. Args:…, UI components for Jenbina Streamlit app, _css_token(), _detect_location_from_action() (+61 more)

### Community 7 - "Person"
Cohesion: 0.07
Nodes (16): Person, Any, Update all needs, decay emotions, and decay lessons, Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Get a summary of conversation with a specific outsider, Get overall communication statistics, Return a first-person narrative of Jenbina's social day. (+8 more)

### Community 8 - "create_basic_needs_chain"
Cohesion: 0.05
Nodes (22): create_basic_needs_chain(), Legacy function for backward compatibility - now uses Maslow decision system, Test error recovery and graceful degradation in chains, Test chain performance with multiple rapid calls, Test chains with different person states, Test that chains produce consistent results with same inputs, Test memory usage of chains, Test the Asimov compliance check system (+14 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., Choose when to be nice, polite, or assertive. (+7 more)

### Community 10 - "simulation_runner.py"
Cohesion: 0.12
Nodes (22): Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, create_world_description_system(), BaseLLM, Creates and returns a function that generates world descriptions. Args: llm:…, _check_proactive_triggers(), _detect_location_from_action() (+14 more)

### Community 11 - "timedelta"
Cohesion: 0.09
Nodes (12): Update need satisfaction over time, After spiking an emotion, update_all should decay it, Test temporal memory retrieval, Test temporal memory retrieval with event type filter, Test needs history retrieval, Test getting history for all needs, Test need satisfaction decay over time, Test storing action memory with people and location (+4 more)

### Community 12 - "shared_init.py"
Cohesion: 0.08
Nodes (34): Streamlit session_state Persistence, SQLite user database for authentication and conversation persistence., Jenbina — Environment & Debug page., Jenbina — Console Log page., Jenbina — Debug Info page., _is_admin(), _is_local_request(), Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /… (+26 more)

### Community 13 - "InsightSystem"
Cohesion: 0.11
Nodes (12): InsightSystem, Any, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Check if conditions are met to generate a subtle insight. Always returns True…, Generate a subtle perceptive observation about the user. Returns the insight…, Reset the per-session counter (call on new session start)., Generates deep perceptive observations about users mid-conversation., Check if we should fire the bold first-impression insight. (+4 more)

### Community 14 - "CuriositySystem"
Cohesion: 0.14
Nodes (6): CuriositySystem, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., Initialize curiosity / exploration system., TestCuriositySystem

### Community 15 - "Person"
Cohesion: 0.17
Nodes (4): Person, Update all needs for this person, Tests for the legacy Person class in core/person.py., TestLegacyPerson

### Community 16 - "TestPerson"
Cohesion: 0.06
Nodes (18): Test Person functionality, Test person initialization, Test person with default name, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider, Test getting conversation history (+10 more)

### Community 17 - "LearningSystem"
Cohesion: 0.09
Nodes (19): LearningSystem, Any, Records experiences, extracts lessons via LLM, and formats them for prompts., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Decay all lessons and prune dead ones., make_mock_llm(), Test LLM-based lesson extraction (+11 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.10
Nodes (31): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, build_search_query(), generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,… (+23 more)

### Community 19 - "BasicNeeds"
Cohesion: 0.06
Nodes (17): BasicNeeds, Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Legacy needs property that maps to Maslow needs, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Add a new need to the system (+9 more)

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.25
Nodes (5): generate_return_greeting(), Generate a dynamic return greeting based on Jenbina's state and relationship., _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateReturnGreeting

### Community 23 - "MemoryEvent"
Cohesion: 0.16
Nodes (12): LocationNode, MemoryEvent, PersonNode, Represents a memory event with all its components, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, Memory Integration Module Shows how to integrate the hybrid memory system with… (+4 more)

### Community 24 - "EnvironmentSimulator"
Cohesion: 0.12
Nodes (13): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Get local events based on Palo Alto location system, Get a natural language description of the current environment (+5 more)

### Community 25 - ".get_needs_summary"
Cohesion: 0.10
Nodes (12): Any, Get average satisfaction for a specific level, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+4 more)

### Community 26 - "TestEnvironmentSimulator"
Cohesion: 0.11
Nodes (10): Calculate how environment affects mood, TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator (+2 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "generate_proactive_message"
Cohesion: 0.27
Nodes (3): generate_proactive_message(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, TestGenerateProactiveMessage

### Community 29 - "get_llm"
Cohesion: 0.10
Nodes (22): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_local_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service… (+14 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.08
Nodes (16): PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type, Get locations within a certain radius of current location (+8 more)

### Community 31 - "create_metadata_from_person_state"
Cohesion: 0.16
Nodes (7): basic_needs_to_json(), create_metadata_from_person_state(), Convert BasicNeeds object to JSON-serializable format, Create metadata dictionary from person state and other context, Interaction and Communication Submodule This submodule handles all aspects of…, TestBasicNeedsToJson, TestCreateMetadataFromPersonState

### Community 32 - "GoalSystem"
Cohesion: 0.11
Nodes (7): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., TestGoalSystem, TestGoalSystemGeneration

### Community 33 - "PlanningSystem"
Cohesion: 0.17
Nodes (9): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., Planning System Design, Multi-step Chain-of-Thought Planning, Plan Step Completion Detection & Replan Trigger, make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation (+1 more)

### Community 34 - "_FakeSessionState"
Cohesion: 0.12
Nodes (15): dict, _FakeSessionState, patch, Dict subclass that also supports attribute-style access, like Streamlit's…, Tests for check_return_greeting in chat.py with llm parameter., Without LLM, first visit (last_visit_time=None) returns None., Without LLM, static greetings are returned (backward compat)., Calling without llm argument uses default None (backward compat). (+7 more)

### Community 35 - "TestEmotion"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "TestMemoryIntegration"
Cohesion: 0.07
Nodes (14): Test storing action memory, Test storing need change memory, Test MemoryIntegration functionality, Test getting relevant context for a query, Test getting context for a specific person, Test getting recent memories, Test getting recent memories with event type filter, Test getting needs trends (+6 more)

### Community 37 - "TestMaslowNeedsSystem"
Cohesion: 0.07
Nodes (14): Test the complete Maslow needs system, Test system initialization with all needs, Test updating all needs over time, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs (+6 more)

### Community 38 - "Conversation"
Cohesion: 0.20
Nodes (6): Conversation, Get all conversations, Represents a conversation with a specific outsider, Tests for core/person.py — legacy Person, Message, and Conversation classes., Tests for the Conversation dataclass., TestConversation

### Community 39 - "Experience"
Cohesion: 0.11
Nodes (12): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set, Test that world_context defaults to empty dict, Test Experience dataclass (+4 more)

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.14
Nodes (7): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestSalienceScoring

### Community 41 - "sidebar.py"
Cohesion: 0.20
Nodes (13): Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar, render_debug_controls() (+5 more)

### Community 42 - "UserDatabase"
Cohesion: 0.04
Nodes (24): Connection, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first., Return all users with their total and per-sender message counts. (+16 more)

### Community 43 - "MemoryIntegration"
Cohesion: 0.12
Nodes (15): example_usage(), MemoryIntegration, Any, Person, Integrates the hybrid memory system with Jenbina's existing components, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person… (+7 more)

### Community 45 - "TestEmotionSystem"
Cohesion: 0.09
Nodes (12): Test EmotionSystem functionality, Should initialize with 8 Plutchik emotions, Check Jenbina's character baselines, Initially, intensity should equal base_intensity, Should spike the named emotion, Triggering unknown emotion should be a no-op, Should apply multiple adjustments at once, Should return top-k emotions by intensity (+4 more)

### Community 46 - "make_goal"
Cohesion: 0.15
Nodes (3): make_goal(), TestGoal, TestGoalSystemDecay

### Community 47 - "Goal"
Cohesion: 0.10
Nodes (11): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals) (+3 more)

### Community 48 - "ChromaMemoryManager"
Cohesion: 0.06
Nodes (29): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+21 more)

### Community 49 - "TestCheckInjectionBlock"
Cohesion: 0.05
Nodes (21): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+13 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "maslow_needs.py"
Cohesion: 0.08
Nodes (19): Needs Management Submodule This submodule handles all aspects of the AI's needs…, Need, NeedCategory, NeedLevel, Enum, Maslow's hierarchy levels, Categories within each need level, Add a new need to the system (+11 more)

### Community 52 - "Plan"
Cohesion: 0.15
Nodes (8): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., An ordered sequence of steps to achieve a goal., make_step(), Tests for the planning system., TestPlanStep

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - ".get_dominant_emotions"
Cohesion: 0.29
Nodes (4): Any, Serialize to dictionary., Get the top-k emotions by intensity., Get a summary dict suitable for LLM prompts.

### Community 55 - "core/__init__.py"
Cohesion: 0.12
Nodes (24): Event, Venue, EnvironmentState, Environment and World Simulation Submodule This submodule handles all aspects…, Location, Neighborhood, create_comprehensive_world_state(), _format_current_events() (+16 more)

### Community 56 - "create_action_decision_chain"
Cohesion: 0.10
Nodes (28): GitHub Actions Workflows README, Test Suite Workflow (push/manual), callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's… (+20 more)

### Community 57 - "TestHybridMemorySystem"
Cohesion: 0.10
Nodes (11): Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test memory statistics, Test person relationships when Neo4j is not available, Test error handling in memory operations, Test that memories persist across system restarts, Test HybridMemorySystem functionality (+3 more)

### Community 58 - "Lesson"
Cohesion: 0.12
Nodes (9): Lesson, A learned pattern extracted from experiences., Test format_lessons_for_prompt, No lessons should return default message, Active lessons should appear in formatted text, Lessons should be sorted by confidence descending, Inactive lessons should not appear, Should show at most 10 lessons (+1 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.17
Nodes (6): Any, Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., Recalculate working memory from current state. Called once per cycle., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "_invoke_and_parse"
Cohesion: 0.13
Nodes (13): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for core/cognition/action_decision_chain.py., Tests for the prompt template definitions. (+5 more)

### Community 62 - "TestChainEdgeCases"
Cohesion: 0.40
Nodes (3): Test edge cases and boundary conditions for chains, Test chains with very large world descriptions, TestChainEdgeCases

### Community 63 - "fix_llm_json"
Cohesion: 0.18
Nodes (8): fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function., TestFixLlmJson

### Community 65 - "test_sprites.py"
Cohesion: 0.05
Nodes (41): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, check(), compose(), _file_matches(), frame_layers(), main() (+33 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "make_plan"
Cohesion: 0.22
Nodes (3): make_plan(), TestPlan, TestPlanningSystemReplan

### Community 68 - "TestLearningSystemStats"
Cohesion: 0.22
Nodes (5): Test get_learning_stats, Empty system should return zero counts, Stats should reflect recorded data, recent_experiences should show at most 5, TestLearningSystemStats

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "make_mock_llm"
Cohesion: 0.30
Nodes (4): make_experience(), make_mock_llm(), TestGoalSystemMilestone, TestGoalSystemProgress

### Community 72 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 73 - "TestConversation"
Cohesion: 0.13
Nodes (8): Test that last_interaction updates when adding messages, Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, TestConversation

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.13
Nodes (12): Initialize social interaction tracker., Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts. (+4 more)

### Community 75 - "MaslowNeedsSystem"
Cohesion: 0.09
Nodes (24): analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:…, Create a decision-making chain based on Maslow's hierarchy of needs Args:… (+16 more)

### Community 76 - "test_simulation.py"
Cohesion: 0.18
Nodes (10): fixture, Page, Playwright E2E test — run a single simulation iteration and verify each stage…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the simulation page loads and shows controls., Click 'Run Single Iteration' and verify key Tamagotchi UI elements appear…, After running, the simulation summary section should appear. (+2 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - "TestLearningSystemSerialization"
Cohesion: 0.18
Nodes (6): Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 79 - "infer_emotional_tone"
Cohesion: 0.31
Nodes (4): infer_emotional_tone(), Return a simple emotional-tone label from message text. This is a *stateless*…, Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Message"
Cohesion: 0.12
Nodes (10): Person Management Submodule This submodule handles the AI's person…, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Add a new message to the conversation, Reconstruct a Person from a JSON string. Args: json_str: JSON produced by…, Get the most recent messages from the conversation, Get all messages of a specific type (+2 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "Run Unit Tests Workflow (PR gate)"
Cohesion: 0.17
Nodes (13): .coveragerc coverage config, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action), Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), pytest / pytest-cov / pytest-playwright / pytest-timeout, Test Suite README, Mock LLM invoke Pattern (+5 more)

### Community 84 - "TestLearningSystemDecay"
Cohesion: 0.18
Nodes (6): Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, TestLearningSystemDecay

### Community 85 - "test_pixel_ui.py"
Cohesion: 0.06
Nodes (28): _data_uri(), dialog_html(), icon_html(), The animated sprite for ``state`` with an optional caption. ``scale`` 4 is the…, An inline 16x16 pixel icon, or an empty span when the icon does not exist. Only…, An RPG dialog box around escaped ``body`` text (newlines become ``<br>``)., sprite_html(), display_jenbina_image() (+20 more)

### Community 86 - "test_person.py"
Cohesion: 0.25
Nodes (4): Test Message functionality, Test message initialization, Test message with default values, TestMessage

### Community 87 - ".get_communication_stats"
Cohesion: 0.25
Nodes (4): Any, Get overall communication statistics, Get a summary of the person's current state, Get a summary of conversation with a specific outsider

### Community 88 - "EmotionSystem"
Cohesion: 0.14
Nodes (8): Emotion, EmotionSystem, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 91 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 92 - "test_goal_system.py"
Cohesion: 0.22
Nodes (4): Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemIntegration, TestGoalSystemStats

### Community 93 - "SocialInteraction"
Cohesion: 0.21
Nodes (6): Any, Social interaction tracker for Jenbina. Records each social interaction (chat,…, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, Tests for the SocialInteractionTracker system., TestSocialInteraction

### Community 94 - "HybridMemorySystem"
Cohesion: 0.08
Nodes (18): HybridMemorySystem, Any, datetime, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID (+10 more)

### Community 95 - "_build_subsystem_context"
Cohesion: 0.43
Nodes (3): _build_subsystem_context(), Extract formatted context from all person subsystems. Returns a list of (label,…, TestBuildSubsystemContext

### Community 97 - "create_memory_integration"
Cohesion: 0.28
Nodes (6): create_memory_integration(), Create a memory integration instance with default settings Returns:…, Test memory integration factory functions, Test creating memory integration with default settings, Test creating memory integration with custom paths, TestMemoryIntegrationFactory

### Community 98 - ".get_current_step"
Cohesion: 0.25
Nodes (3): Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Mark current step completed and move to next.

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 103 - ".create_plan"
Cohesion: 0.20
Nodes (5): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id.

### Community 104 - "Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)"
Cohesion: 0.67
Nodes (3): ConversationMemory, Represents a conversation memory entry, Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 114 - "chat.py"
Cohesion: 0.08
Nodes (42): _chat_avatar(), Pixel avatar path for a chat row. Imported lazily: ``core.ui`` imports this…, check_proactive_message(), check_return_greeting(), display_communication_stats(), display_conversation_history(), display_memory_debug(), display_memory_stats() (+34 more)

### Community 115 - "Jenbina Blob Character"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "clear_chromadb.py"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 118 - ".test_full_plan_lifecycle"
Cohesion: 0.40
Nodes (3): Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete., TestPlanningSystemIntegration

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 136 - "MaslowNeed"
Cohesion: 0.08
Nodes (16): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy, Increase satisfaction by given amount, Test low status detection (+8 more)

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls
- `run_simulation_loop()` → `APScheduler (background scheduling)`  [AMBIGUOUS]
  requirements.txt · relation: conceptually_related_to

## Knowledge Gaps
- **25 isolated node(s):** `Global Constraints`, `Review Focus`, `Task 1: Palette and compositor`, `Task 2: Body, hair, faces and the emotion states`, `Task 3: Props, effects and the action states` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `run_simulation_loop()` and `APScheduler (background scheduling)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Person` connect `Person` to `CLAUDE.md Project Instructions`, `MetaCognitiveSystem`, `create_basic_needs_chain`, `SocialCognitionSystem`, `simulation_runner.py`, `shared_init.py`, `InsightSystem`, `CuriositySystem`, `TestPerson`, `Deep Emotional Mirror Implementation Plan`, `SelfNarrativeSystem`, `MemoryEvent`, `get_llm`, `GoalSystem`, `PlanningSystem`, `TestMemoryIntegration`, `Conversation`, `Experience`, `WorkingMemorySystem`, `MemoryIntegration`, `Goal`, `core/__init__.py`, `create_action_decision_chain`, `TestChainEdgeCases`, `SocialInteractionTracker`, `MaslowNeedsSystem`, `Message`, `test_person.py`, `EmotionSystem`, `.add_conversation`, `SocialInteraction`, `create_memory_integration`, `TestPersonSerializeConversations`, `Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)`, `TestPersonCuriositySerialization`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `GoalSystem` connect `GoalSystem` to `PlanningSystem`, `CLAUDE.md Project Instructions`, `TestGoalSystemFormatting`, `simulation.py`, `Experience`, `Person`, `make_mock_llm`, `MaslowNeedsSystem`, `.from_dict`, `make_goal`, `Goal`, `Deep Emotional Mirror Implementation Plan`, `Plan`, `generate_return_greeting`, `EmotionSystem`, `test_goal_system.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `CLAUDE.md Project Instructions` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `simulation.py`, `simulation_runner.py`, `MaslowNeedsSystem`, `shared_init.py`, `ChromaMemoryManager`, `TestCheckInjectionBlock`, `Deep Emotional Mirror Implementation Plan`, `Run Unit Tests Workflow (PR gate)`, `clear_chromadb.py`, `maslow_needs.py`, `create_action_decision_chain`, `StreamCapture`, `get_llm`, `HybridMemorySystem`, `fix_llm_json`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `WorkingMemorySystem` (e.g. with `EmotionSystem` and `Goal`) actually correct?**
  _`WorkingMemorySystem` has 15 INFERRED edges - model-reasoned connections that need verification._