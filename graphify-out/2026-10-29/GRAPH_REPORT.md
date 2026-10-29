# Graph Report - quizzical-mirzakhani  (2026-10-29)

## Corpus Check
- 153 files · ~457,897 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2934 nodes · 6177 edges · 132 communities (115 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 374 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8962c0cf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_person
- world_state.py
- CLAUDE.md Project Instructions
- generate_first_greeting
- MetaCognitiveSystem
- test_pixel_ui.py
- Person
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- MaslowNeedsSystem
- sidebar.py
- InsightSystem
- CuriositySystem
- Person
- TestPerson
- LearningSystem
- Deep Emotional Mirror Implementation Plan
- TestChains
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- memory/__init__.py
- Test Suite README
- .create_plan
- TestEnvironmentSimulator
- StreamCapture
- timedelta
- get_llm
- PaloAltoLocationSystem
- chat_handler.py
- GoalSystem
- PlanningSystem
- _FakeSessionState
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- core/__init__.py
- Experience
- WorkingMemorySystem
- run_single_iteration
- UserDatabase
- MemoryIntegration
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- guardrails.py
- handle_chat_interaction
- Need
- Plan
- TestLesson
- EmotionSystem
- .get_needs_summary
- simulation_runner.py
- MemoryEvent
- Lesson
- TestUserCRUD
- WorkingMemoryItem
- fix_llm_json
- timeline.py
- make_mock_llm
- TestBasicNeedsBackwardCompatibility
- test_sprites.py
- _run_one_iteration
- make_plan
- TestCheckInjectionBlock
- FirebaseAuth
- Conversation
- run_chain_tests.py
- Design
- TestConversation
- SocialInteractionTracker
- _invoke_and_parse
- test_simulation.py
- File Structure
- TestLearningSystemSerialization
- infer_emotional_tone
- Design
- Conversation
- test_working_memory.py
- NullRail
- EventLog
- TestCheckInjectionWarn
- Message
- TestTitles
- Emotion
- display_jenbina_image
- .record_social_action
- streamlit_server
- Any
- SocialInteraction
- HybridMemorySystem
- .from_dict
- Review Focus
- TestLearningSystemDecay
- .get_current_step
- _format_current_events
- event_html
- make_needs
- .get_planning_stats
- stage_pill_html
- .from_dict
- TestEvents
- TestPromptTemplates
- .from_dict
- TestGrowthStageLadder
- TestGoalSystemStats
- _format_nearby_locations
- TestChainRealWorldScenarios
- simulation.py
- Jenbina Blob Character
- clear_chromadb.py
- .test_full_plan_lifecycle
- TestFocusNoise
- shared_init.py
- TestContextSwitch
- .add_conversation
- ._get_capacity
- .from_dict
- maslow_needs.py
- TestFormatting
- TestUiExports
- .init_planning_system

## God Nodes (most connected - your core abstractions)
1. `Person` - 87 edges
2. `GoalSystem` - 82 edges
3. `WorkingMemorySystem` - 72 edges
4. `PlanningSystem` - 66 edges
5. `InnerMonologueSystem` - 64 edges
6. `MaslowNeedsSystem` - 55 edges
7. `run_single_iteration()` - 51 edges
8. `UserDatabase` - 48 edges
9. `Person` - 48 edges
10. `CLAUDE.md Project Instructions` - 47 edges

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
- **Deep Emotional Mirror feature flow (research -> dossier -> insights -> greetings -> chat)** — core_research_user_research_research_user, core_research_user_research_generate_user_dossier, core_social_social_cognition_personmodel, core_insights_insight_system_insightsystem, core_interaction_chat_handler_handle_chat_interaction, core_interaction_chat_handler_generate_first_greeting, core_interaction_chat_handler_generate_return_greeting, core_ui_chat_check_return_greeting, core_ui_shared_init_init_session_state, core_ui_shared_init_init_llm, core_interaction_guardrails_jenbina_system_prompt [EXTRACTED 1.00]
- **Jenbina Visual Identity (pink blob mascot, happy expression, Tamagotchi styling)** — assets_favicon, assets_favicon_jenbina_blob_character, assets_favicon_content_happy_expression, assets_favicon_tamagotchi_mascot_design [INFERRED 0.85]
- **Motivation-to-action stack injected into the action decision prompt (working memory, plan step, goals, lessons)** — core_working_memory_working_memory_system_workingmemorysystem, core_planning_planning_system_planningsystem, core_goals_goal_system_goalsystem, core_learning_learning_system_learningsystem, core_needs_maslow_needs_maslowneedssystem, core_cognition_action_decision_chain_create_action_decision_chain [INFERRED 0.85]
- **Simulation iteration LLM chain pipeline (needs -> world -> description -> action -> Asimov -> state)** — core_needs_maslow_needs_create_basic_needs_chain, core_environment_world_state_create_comprehensive_world_state, core_environment_world_state_create_world_description_system, core_cognition_enhanced_action_decision_chain_create_meta_cognitive_action_chain, core_cognition_action_decision_chain_create_action_decision_chain, core_cognition_asimov_check_chain_create_asimov_check_system, core_cognition_state_analysis_chain_create_state_analysis_system, core_ui_simulation_run_single_iteration [INFERRED 0.85]

## Communities (132 total, 17 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (39): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+31 more)

### Community 1 - "_make_mock_person"
Cohesion: 0.09
Nodes (24): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+16 more)

### Community 2 - "world_state.py"
Cohesion: 0.10
Nodes (22): DynamicEventsSystem, Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API (+14 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.10
Nodes (48): .coveragerc coverage config, GitHub Actions Workflows README, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action) (+40 more)

### Community 4 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.08
Nodes (23): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+15 more)

### Community 6 - "test_pixel_ui.py"
Cohesion: 0.07
Nodes (31): _data_uri(), dialog_html(), icon_html(), Base64 data URI of a committed asset, cached for the process lifetime. Assets…, An inline 16x16 pixel icon, or an empty span when the icon does not exist. Only…, An RPG dialog box around escaped ``body`` text (newlines become ``<br>``)., Redraw mood, place, doing/goal lines, needs bars and emotion chips., _css_token() (+23 more)

### Community 7 - "Person"
Cohesion: 0.07
Nodes (17): Person Management Submodule This submodule handles the AI's person…, Person, Any, Update all needs, decay emotions, and decay lessons, Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Start a new conversation with an outsider, Receive a message from an outsider (+9 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.11
Nodes (14): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Calculate how environment affects mood, Get local events based on Palo Alto location system (+6 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., Choose when to be nice, polite, or assertive. (+7 more)

### Community 10 - "rail.py"
Cohesion: 0.09
Nodes (24): _about_you_lines(), _card_title(), env_line_html(), _goal_lines(), _lesson_lines(), _plan_lines(), The status rail beside the timeline: the Now card (stage pill, portrait,…, Draw the Now card and return the handles the runner updates. (+16 more)

### Community 11 - "MaslowNeedsSystem"
Cohesion: 0.07
Nodes (28): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+20 more)

### Community 12 - "sidebar.py"
Cohesion: 0.20
Nodes (13): Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar, render_debug_controls() (+5 more)

### Community 13 - "InsightSystem"
Cohesion: 0.11
Nodes (12): InsightSystem, Any, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Check if conditions are met to generate a subtle insight. Always returns True…, Generate a subtle perceptive observation about the user. Returns the insight…, Reset the per-session counter (call on new session start)., Generates deep perceptive observations about users mid-conversation., Check if we should fire the bold first-impression insight. (+4 more)

### Community 14 - "CuriositySystem"
Cohesion: 0.10
Nodes (9): CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., Initialize curiosity / exploration system., TestCuriositySystem (+1 more)

### Community 15 - "Person"
Cohesion: 0.11
Nodes (8): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Get a summary of conversation with a specific outsider, Tests for the legacy Person class in core/person.py., TestLegacyPerson

### Community 16 - "TestPerson"
Cohesion: 0.05
Nodes (19): Test Person functionality, Test person initialization, Test person with default name, Test updating all needs, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider (+11 more)

### Community 17 - "LearningSystem"
Cohesion: 0.08
Nodes (21): LearningSystem, Any, Records experiences, extracts lessons via LLM, and formats them for prompts., Decay all lessons and prune dead ones., Initialize the learning system with an LLM instance. Called separately because…, make_mock_llm(), Test LLM-based lesson extraction, Test that valid LLM JSON response creates lessons (+13 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.10
Nodes (34): .env.example template, Environment Variables (.env / .env.example), Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, build_search_query(), generate_user_dossier(), parse_research_results(), Any (+26 more)

### Community 19 - "TestChains"
Cohesion: 0.05
Nodes (22): BasicNeeds, Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Add a new need to the system, Remove a need from the system (+14 more)

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (21): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+13 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.15
Nodes (8): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateProactiveMessage, TestGenerateReturnGreeting

### Community 23 - "memory/__init__.py"
Cohesion: 0.15
Nodes (12): LocationNode, PersonNode, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, create_memory_integration(), Memory Integration Module Shows how to integrate the hybrid memory system with…, Create a memory integration instance with default settings Returns:… (+4 more)

### Community 24 - "Test Suite README"
Cohesion: 0.25
Nodes (8): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), Run a specific test module, run_specific_test(), Run all tests and provide comprehensive reporting, run_comprehensive_tests()

### Community 25 - ".create_plan"
Cohesion: 0.20
Nodes (5): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id.

### Community 26 - "TestEnvironmentSimulator"
Cohesion: 0.12
Nodes (9): TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator, TestTimeData (+1 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "timedelta"
Cohesion: 0.17
Nodes (8): build_timeline(), Render the rows in order; an empty list shows the empty-state marker., Merge chat messages and life events by time, apply the filter, keep the newest…, render_timeline(), TestBuildTimeline, TestCorruptRows, TestRenderTimeline, timedelta

### Community 29 - "get_llm"
Cohesion: 0.10
Nodes (21): get_json_llm(), get_llm(), get_recommended_llm(), Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service…, Get LLM with recommended configuration for specific use case. Args: use_case:…, run_simulation(), LLMProvider (+13 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.09
Nodes (19): Location, PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type (+11 more)

### Community 31 - "chat_handler.py"
Cohesion: 0.08
Nodes (19): basic_needs_to_json(), _build_subsystem_context(), _chat_avatar(), create_metadata_from_person_state(), history_context(), ``section[key]`` for the nested world-summary shape, the value itself for a…, ``(recent_actions, world_context)`` read from the records the runners append to…, Convert BasicNeeds object to JSON-serializable format (+11 more)

### Community 32 - "GoalSystem"
Cohesion: 0.10
Nodes (8): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., Initialize the goal system with an LLM instance. Called separately because LLM…, TestGoalSystemFormatting, TestGoalSystemGeneration

### Community 33 - "PlanningSystem"
Cohesion: 0.16
Nodes (7): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation, TestPlanningSystemReplan, TestPlanningSystemStats

### Community 34 - "_FakeSessionState"
Cohesion: 0.12
Nodes (15): dict, _FakeSessionState, patch, Dict subclass that also supports attribute-style access, like Streamlit's…, Tests for check_return_greeting in chat.py with llm parameter., Without LLM, first visit (last_visit_time=None) returns None., Without LLM, static greetings are returned (backward compat)., Calling without llm argument uses default None (backward compat). (+7 more)

### Community 35 - "TestEmotion"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "TestMemoryIntegration"
Cohesion: 0.06
Nodes (17): Test storing action memory, Test storing action memory with people and location, Test storing need change memory, Test storing need change memory with current needs state, Test MemoryIntegration functionality, Test getting relevant context for a query, Test getting context for a specific person, Test getting recent memories (+9 more)

### Community 37 - "TestMaslowNeedsSystem"
Cohesion: 0.07
Nodes (15): Test the complete Maslow needs system, Test system initialization with all needs, Test updating all needs over time, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs (+7 more)

### Community 38 - "core/__init__.py"
Cohesion: 0.12
Nodes (18): callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_meta_cognitive_action_chain(), Enhanced action decision with meta-cognitive monitoring, Cognition and Decision Making Submodule This submodule handles all aspects of…, create_world_description_system(), BaseLLM (+10 more)

### Community 39 - "Experience"
Cohesion: 0.09
Nodes (14): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set (+6 more)

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.14
Nodes (7): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestSalienceScoring

### Community 41 - "run_single_iteration"
Cohesion: 0.12
Nodes (34): make_action(), make_goal(), make_mood(), make_move(), make_plan(), make_thought(), The vocabulary of Jenbina's life events, their one-line titles, and the…, One entry of Jenbina's day. ``title`` is the line the timeline shows. (+26 more)

### Community 42 - "UserDatabase"
Cohesion: 0.04
Nodes (27): Connection, datetime, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first. (+19 more)

### Community 43 - "MemoryIntegration"
Cohesion: 0.12
Nodes (15): example_usage(), MemoryIntegration, Any, Person, Integrates the hybrid memory system with Jenbina's existing components, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person… (+7 more)

### Community 45 - "TestEmotionSystem"
Cohesion: 0.08
Nodes (13): Test EmotionSystem functionality, Should initialize with 8 Plutchik emotions, Check Jenbina's character baselines, Initially, intensity should equal base_intensity, Should spike the named emotion, Triggering unknown emotion should be a no-op, Should apply multiple adjustments at once, Should return top-k emotions by intensity (+5 more)

### Community 46 - "make_goal"
Cohesion: 0.15
Nodes (3): make_goal(), TestGoal, TestGoalSystemDecay

### Community 47 - "Goal"
Cohesion: 0.10
Nodes (11): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals) (+3 more)

### Community 48 - "ChromaMemoryManager"
Cohesion: 0.06
Nodes (28): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+20 more)

### Community 49 - "guardrails.py"
Cohesion: 0.11
Nodes (17): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+9 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "Need"
Cohesion: 0.09
Nodes (13): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Legacy needs property that maps to Maslow needs, Test the legacy Need class (+5 more)

### Community 52 - "Plan"
Cohesion: 0.13
Nodes (11): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., An ordered sequence of steps to achieve a goal., Planning System Design, Multi-step Chain-of-Thought Planning, Plan Step Completion Detection & Replan Trigger (+3 more)

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.12
Nodes (11): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Decay all emotions toward their baselines based on elapsed time., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}. (+3 more)

### Community 55 - ".get_needs_summary"
Cohesion: 0.12
Nodes (10): Any, Get average satisfaction for a specific level, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+2 more)

### Community 56 - "simulation_runner.py"
Cohesion: 0.06
Nodes (36): _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead., create_state_analysis_system(), Any, BaseLLM (+28 more)

### Community 57 - "MemoryEvent"
Cohesion: 0.07
Nodes (21): MemoryEvent, Represents a memory event with all its components, Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval (+13 more)

### Community 58 - "Lesson"
Cohesion: 0.12
Nodes (9): Lesson, A learned pattern extracted from experiences., Test format_lessons_for_prompt, No lessons should return default message, Active lessons should appear in formatted text, Lessons should be sorted by confidence descending, Inactive lessons should not appear, Should show at most 10 lessons (+1 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.17
Nodes (6): Any, Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., Recalculate working memory from current state. Called once per cycle., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "fix_llm_json"
Cohesion: 0.17
Nodes (9): LLM JSON Parsing via fix_llm_json, fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function. (+1 more)

### Community 62 - "timeline.py"
Cohesion: 0.12
Nodes (20): lessons_text(), Lessons as one line: lists joined with '; ', strings as they are., delta_badge_html(), The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests., avatar_path(), Path of the 48x48 chat avatar (frame 0 of ``base``)., action_details_text(), _event_row_html() (+12 more)

### Community 63 - "make_mock_llm"
Cohesion: 0.17
Nodes (8): make_experience(), make_mock_llm(), Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystem, TestGoalSystemIntegration, TestGoalSystemMilestone, TestGoalSystemProgress

### Community 64 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 65 - "test_sprites.py"
Cohesion: 0.05
Nodes (41): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, check(), compose(), _file_matches(), frame_layers(), main() (+33 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "make_plan"
Cohesion: 0.20
Nodes (4): make_experience(), make_plan(), TestPlan, TestPlanningSystemEvaluation

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "run_chain_tests.py"
Cohesion: 0.14
Nodes (11): main(), Main function to run tests, Run all chain tests and return results, Run a specific test by name, run_chain_tests(), run_specific_test(), Test edge cases and boundary conditions for chains, Test chains with empty or minimal needs (+3 more)

### Community 72 - "Design"
Cohesion: 0.11
Nodes (18): 10. Code changes, 1. Pages, 2. Shell, 3. Left column: the timeline, 4. The event log, 5. Right column: the status rail, 6. The runner, 7. Bug fixes in scope (+10 more)

### Community 73 - "TestConversation"
Cohesion: 0.13
Nodes (8): Test that last_interaction updates when adding messages, Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, TestConversation

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.20
Nodes (8): Initialize social interaction tracker., Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts., Tracks all of Jenbina's social interactions during the session. Only the…, SocialInteractionTracker

### Community 75 - "_invoke_and_parse"
Cohesion: 0.20
Nodes (10): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for the _invoke_and_parse helper., Tests for create_action_decision_chain. (+2 more)

### Community 76 - "test_simulation.py"
Cohesion: 0.20
Nodes (9): fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the home screen loads with the timeline and the controls., Click 'Step once' and verify the rail and the timeline fill in., sim_page() (+1 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - "TestLearningSystemSerialization"
Cohesion: 0.18
Nodes (6): Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 79 - "infer_emotional_tone"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Conversation"
Cohesion: 0.14
Nodes (8): Conversation, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Tests for core/person.py — legacy Person, Message, and Conversation classes., Tests for the Conversation dataclass., TestConversation

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "NullRail"
Cohesion: 0.11
Nodes (15): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, NullRail, A rail that draws nothing: headless runs and tests., build_env(), _plan_fixture(), Two plans: one finished earlier, one whose last step completes this iteration;…, A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a… (+7 more)

### Community 84 - "EventLog"
Cohesion: 0.16
Nodes (5): EventLog, Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., TestEventLog

### Community 86 - "Message"
Cohesion: 0.12
Nodes (11): Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Reconstruct a Person from a JSON string. Args: json_str: JSON produced by…, Get all messages of a specific type, Tests for the Message dataclass., TestMessage, Test Message functionality (+3 more)

### Community 87 - "TestTitles"
Cohesion: 0.19
Nodes (5): mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 88 - "Emotion"
Cohesion: 0.25
Nodes (4): Emotion, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "display_jenbina_image"
Cohesion: 0.09
Nodes (17): The animated sprite for ``state`` with an optional caption. ``scale`` 4 is the…, sprite_html(), display_jenbina_image(), _portrait_path(), Show the painterly portrait for the state named by ``image_path`` in a game…, The portrait file for ``state``, the ``base`` portrait if that is missing, else…, icon_path(), Pixel sprite assets for the Jenbina UI. Only paths and constants live here;… (+9 more)

### Community 90 - ".record_social_action"
Cohesion: 0.25
Nodes (4): Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Generate a simple automatic sentiment string., Try to extract a person/entity name from a simulated action string. The action…

### Community 91 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 92 - "Any"
Cohesion: 0.18
Nodes (7): Any, datetime, Retrieve memories based on semantic similarity, Get all relationships and interactions for a person, Get memories within a time range, Get needs satisfaction history over time, Get statistics about the memory system

### Community 93 - "SocialInteraction"
Cohesion: 0.29
Nodes (4): Any, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, TestSocialInteraction

### Community 94 - "HybridMemorySystem"
Cohesion: 0.10
Nodes (13): HybridMemorySystem, OpenAI embeddings client, built lazily so an API key is only needed once…, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID, Store event in ChromaDB for semantic search (+5 more)

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "TestLearningSystemDecay"
Cohesion: 0.18
Nodes (6): Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, TestLearningSystemDecay

### Community 98 - ".get_current_step"
Cohesion: 0.25
Nodes (3): Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Mark current step completed and move to next.

### Community 99 - "_format_current_events"
Cohesion: 0.11
Nodes (10): _format_current_events(), _format_location_details(), _format_open_locations(), _format_time_details(), _format_weather_details(), Format currently open locations into a readable string., Format current events into a readable string., Format current location details. (+2 more)

### Community 100 - "event_html"
Cohesion: 0.28
Nodes (5): action_icon(), event_html(), The icon name for an action's row, by keyword; the star when none fits., One timeline row for a life event. ``details`` is ``(summary, body)`` rendered…, TestEventHtml

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 103 - "stage_pill_html"
Cohesion: 0.25
Nodes (6): marker_html(), A centered time/place divider between timeline rows., The system stage pill in the status rail., stage_pill_html(), Show the system stage in the pill and remember it for reruns., TestMarkerAndPill

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 111 - "TestChainRealWorldScenarios"
Cohesion: 0.22
Nodes (5): Test chains with realistic scenarios, Test chains in a morning routine scenario, Test chains in a stressful situation, Test chains in a creative work scenario, TestChainRealWorldScenarios

### Community 114 - "simulation.py"
Cohesion: 0.08
Nodes (44): _latest_world(), main(), Jenbina - AGI Simulation Streamlit App Main entry point — the home screen: the…, ``(world_summary, chosen_action)`` of the last iteration this session, or…, _top_goal(), analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, check_proactive_message() (+36 more)

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

### Community 123 - "shared_init.py"
Cohesion: 0.08
Nodes (33): SQLite user database for authentication and conversation persistence., Jenbina — Environment & Debug page., Jenbina — Console Log page., Jenbina — Debug Info page., _is_admin(), _is_local_request(), Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, Check if the request originates from localhost. (+25 more)

### Community 125 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 136 - "maslow_needs.py"
Cohesion: 0.06
Nodes (24): MaslowNeed, NeedCategory, NeedLevel, Enum, Check if need is critically low, Maslow's hierarchy levels, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance (+16 more)

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls
- `run_simulation_loop()` → `APScheduler (background scheduling)`  [AMBIGUOUS]
  requirements.txt · relation: conceptually_related_to

## Knowledge Gaps
- **54 isolated node(s):** `Global Constraints`, `Review Focus`, `Task 1: Palette and compositor`, `Task 2: Body, hair, faces and the emotion states`, `Task 3: Props, effects and the action states` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `run_simulation_loop()` and `APScheduler (background scheduling)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Person` connect `Person` to `InnerMonologueSystem`, `world_state.py`, `CLAUDE.md Project Instructions`, `MetaCognitiveSystem`, `test_pixel_ui.py`, `SocialCognitionSystem`, `MaslowNeedsSystem`, `InsightSystem`, `CuriositySystem`, `.init_planning_system`, `TestPerson`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `TestChains`, `SelfNarrativeSystem`, `memory/__init__.py`, `get_llm`, `GoalSystem`, `PlanningSystem`, `TestMemoryIntegration`, `core/__init__.py`, `Experience`, `WorkingMemorySystem`, `MemoryIntegration`, `Goal`, `Plan`, `EmotionSystem`, `simulation_runner.py`, `run_chain_tests.py`, `SocialInteractionTracker`, `infer_emotional_tone`, `Conversation`, `NullRail`, `Message`, `TestChainRealWorldScenarios`, `shared_init.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `Jenbina README` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `GoalSystem`, `MetaCognitiveSystem`, `core/__init__.py`, `Person`, `EnvironmentSimulator`, `SocialCognitionSystem`, `InsightSystem`, `CuriositySystem`, `LearningSystem`, `simulation.py`, `Deep Emotional Mirror Implementation Plan`, `SelfNarrativeSystem`, `EmotionSystem`, `simulation_runner.py`, `Test Suite README`, `get_llm`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `CLAUDE.md Project Instructions` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `core/__init__.py`, `test_pixel_ui.py`, `maslow_needs.py`, `run_chain_tests.py`, `MaslowNeedsSystem`, `shared_init.py`, `ChromaMemoryManager`, `guardrails.py`, `Deep Emotional Mirror Implementation Plan`, `simulation.py`, `clear_chromadb.py`, `simulation_runner.py`, `Test Suite README`, `StreamCapture`, `get_llm`, `HybridMemorySystem`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `WorkingMemorySystem` (e.g. with `EmotionSystem` and `Goal`) actually correct?**
  _`WorkingMemorySystem` has 15 INFERRED edges - model-reasoned connections that need verification._