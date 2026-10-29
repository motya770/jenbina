# Graph Report - objective-shirley  (2026-10-29)

## Corpus Check
- 154 files · ~459,101 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2948 nodes · 6198 edges · 144 communities (133 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 374 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fefa7457`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_person
- world_state.py
- CLAUDE.md Project Instructions
- MaslowNeedsSystem
- MetaCognitiveSystem
- test_pixel_ui.py
- Person
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- maslow_needs.py
- requirements.txt Dependency Manifest
- InsightSystem
- CuriositySystem
- Person
- TestPerson
- LearningSystem
- Deep Emotional Mirror Implementation Plan
- create_basic_needs_chain
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)
- Test Suite README
- Inner Life Surfacing via Prompt Engineering
- TestEnvironmentSimulator
- StreamCapture
- simulation_runner.py
- get_llm
- PaloAltoLocationSystem
- chat_handler.py
- GoalSystem
- PlanningSystem
- _FakeSessionState
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- _invoke_and_parse
- Experience
- WorkingMemorySystem
- test_timeline.py
- UserDatabase
- MemoryIntegration
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- timedelta
- handle_chat_interaction
- Need
- Plan
- TestLesson
- EmotionSystem
- .get_needs_summary
- create_asimov_check_system
- TestHybridMemorySystem
- Lesson
- TestUserCRUD
- WorkingMemoryItem
- fix_llm_json
- build_timeline
- make_mock_llm
- check
- test_sprites.py
- _run_one_iteration
- make_plan
- TestCheckInjectionBlock
- FirebaseAuth
- Conversation
- TestChains
- Design
- TestConversation
- SocialInteractionTracker
- history_context
- test_simulation.py
- File Structure
- TestLearningSystemSerialization
- infer_emotional_tone
- Design
- Conversation
- test_working_memory.py
- EventLog
- _make_mock_llm
- 3_🌍_Environment.py
- Message
- TestTitles
- Emotion
- display_jenbina_image
- .record_social_action
- streamlit_server
- HybridMemorySystem
- SocialInteraction
- MemoryEvent
- compose
- Review Focus
- TestLearningSystemDecay
- .get_current_step
- _format_current_events
- run_single_iteration
- make_needs
- render_frame
- make_experience
- .from_dict
- build.py
- TestBasicNeedsBackwardCompatibility
- .from_dict
- render_sheet
- TestGoalSystemStats
- _format_nearby_locations
- generate_proactive_message
- 6_🔑_Admin.py
- art.py
- simulation.py
- Jenbina Blob Character
- clear_chromadb.py
- _make_mock_llm_failing
- SimpleEmbeddings
- TestEvents
- .create_plan
- TestFocusNoise
- auth_page.py
- shared_init.py
- TestContextSwitch
- .add_conversation
- ._get_capacity
- .from_dict
- generate_first_greeting
- match_action_key
- MaslowNeed
- Deploying Jenbina to Railway
- TestFormatting
- TestChainRealWorldScenarios
- TestChainEdgeCases
- render_icon
- TestUiExports
- .update_all_needs

## God Nodes (most connected - your core abstractions)
1. `Person` - 88 edges
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
- `create_maslow_goal_setter()` --semantically_similar_to--> `Goal System Design`  [INFERRED] [semantically similar]
  core/needs/maslow_decision_chain.py → docs/plans/2026-02-07-goal-system-design.md
- `run_single_iteration_headless()` --semantically_similar_to--> `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)`  [INFERRED] [semantically similar]
  core/simulation_runner.py → CURRENT_ARCHITECTURE_DIAGRAMS.md
- `run_single_iteration()` --semantically_similar_to--> `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)`  [INFERRED] [semantically similar]
  core/ui/simulation.py → CURRENT_ARCHITECTURE_DIAGRAMS.md
- `search_web()` --semantically_similar_to--> `query_llm_knowledge() (planned function)`  [INFERRED] [semantically similar]
  core/research/user_research.py → docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md
- `run_simulation_loop()` --conceptually_related_to--> `APScheduler (background scheduling)`  [AMBIGUOUS]
  core/ui/simulation.py → requirements.txt

## Import Cycles
- None detected.

## Communities (144 total, 11 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (39): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+31 more)

### Community 1 - "_make_mock_person"
Cohesion: 0.11
Nodes (15): _make_mock_person(), LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists., Self-narrative is included when available., Last conversation topics are included when there's history., Dossier hint is included when social cognition has user data. (+7 more)

### Community 2 - "world_state.py"
Cohesion: 0.10
Nodes (22): DynamicEventsSystem, Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API (+14 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.16
Nodes (27): CLAUDE.md Project Instructions, Layered Architecture (UI -> Interaction -> Cognition -> Core -> DB -> LLM), Current Architecture Diagrams, Database Schemas (Chroma collection, Neo4j graph, SQLite tables), Installation Guide, Environment API Keys (Eventbrite, Ticketmaster, Yelp, Google Places), LangSmith Tracing (optional env vars), Neo4j Docker Setup (optional, neo4j:5.17.0 with APOC) (+19 more)

### Community 4 - "MaslowNeedsSystem"
Cohesion: 0.10
Nodes (24): Jenbina AGI System - Core Module This is the main core module for the Jenbina…, Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:… (+16 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.08
Nodes (20): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+12 more)

### Community 6 - "test_pixel_ui.py"
Cohesion: 0.06
Nodes (32): Streamlit session_state Persistence, dialog_html(), icon_html(), An inline 16x16 pixel icon, or an empty span when the icon does not exist. Only…, An RPG dialog box around escaped ``body`` text (newlines become ``<br>``)., Redraw mood, place, doing/goal lines, needs bars and emotion chips., _css_token(), Render Maslow needs as ten-segment pixel bars with 8x8 icons. (+24 more)

### Community 7 - "Person"
Cohesion: 0.07
Nodes (16): Person, Any, Update all needs, decay emotions, and decay lessons, Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+8 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.11
Nodes (14): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Calculate how environment affects mood, Get local events based on Palo Alto location system (+6 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., Choose when to be nice, polite, or assertive. (+7 more)

### Community 10 - "rail.py"
Cohesion: 0.11
Nodes (16): _about_you_lines(), env_line_html(), _goal_lines(), _lesson_lines(), _plan_lines(), The status rail beside the timeline: the Now card (stage pill, portrait,…, Goals, plans, lessons and what she knows about the user, as four tabs., ``<icon> Jenbina's House · Night · Clear skies, 15°C``; the bare home name when… (+8 more)

### Community 11 - "maslow_needs.py"
Cohesion: 0.18
Nodes (9): NeedCategory, NeedLevel, Enum, Maslow's hierarchy levels, Categories within each need level, Add a new need to the system, Create from dictionary, The growth stage names the level Jenbina is working on, and it falls back when… (+1 more)

### Community 12 - "requirements.txt Dependency Manifest"
Cohesion: 0.17
Nodes (21): .coveragerc coverage config, .env.example template, GitHub Actions Workflows README, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload (+13 more)

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
Cohesion: 0.12
Nodes (25): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, build_search_query(), generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,… (+17 more)

### Community 19 - "create_basic_needs_chain"
Cohesion: 0.06
Nodes (21): BasicNeeds, create_basic_needs_chain(), Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Add a new need to the system (+13 more)

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (21): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+13 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.25
Nodes (5): generate_return_greeting(), Generate a dynamic return greeting based on Jenbina's state and relationship., _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateReturnGreeting

### Community 23 - "Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)"
Cohesion: 0.14
Nodes (15): ConversationMemory, Represents a conversation memory entry, LocationNode, PersonNode, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, create_memory_integration() (+7 more)

### Community 24 - "Test Suite README"
Cohesion: 0.25
Nodes (8): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), Run a specific test module, run_specific_test(), Run all tests and provide comprehensive reporting, run_comprehensive_tests()

### Community 25 - "Inner Life Surfacing via Prompt Engineering"
Cohesion: 0.60
Nodes (6): Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals

### Community 26 - "TestEnvironmentSimulator"
Cohesion: 0.12
Nodes (9): TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator, TestTimeData (+1 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "simulation_runner.py"
Cohesion: 0.11
Nodes (21): get_world_state_summary(), Any, Get a comprehensive summary of the world state for display or processing. Args:…, _check_proactive_triggers(), credit_completed_plan(), _detect_location_from_action(), get_person_dict(), _print_json() (+13 more)

### Community 29 - "get_llm"
Cohesion: 0.12
Nodes (16): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_recommended_llm(), Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service…, Get LLM with recommended configuration for specific use case. Args: use_case:…, LLMProvider (+8 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.09
Nodes (19): Location, PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type (+11 more)

### Community 31 - "chat_handler.py"
Cohesion: 0.10
Nodes (15): basic_needs_to_json(), _build_subsystem_context(), _chat_avatar(), create_metadata_from_person_state(), Convert BasicNeeds object to JSON-serializable format, Pixel avatar path for a chat row. Imported lazily: ``core.ui`` imports this…, Create metadata dictionary from person state and other context, Extract formatted context from all person subsystems. Returns a list of (label,… (+7 more)

### Community 32 - "GoalSystem"
Cohesion: 0.10
Nodes (8): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., Initialize the goal system with an LLM instance. Called separately because LLM…, TestGoalSystemFormatting, TestGoalSystemGeneration

### Community 33 - "PlanningSystem"
Cohesion: 0.14
Nodes (9): Initialize the planning system with an LLM instance. Called separately because…, PlanningSystem, Any, Decomposes goals into plans and tracks execution across cycles., make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation, TestPlanningSystemSerialization (+1 more)

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
Nodes (14): Test the complete Maslow needs system, Test system initialization with all needs, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs, Test getting priority needs (+6 more)

### Community 38 - "_invoke_and_parse"
Cohesion: 0.12
Nodes (14): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for core/cognition/action_decision_chain.py., Tests for the prompt template definitions. (+6 more)

### Community 39 - "Experience"
Cohesion: 0.09
Nodes (14): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set (+6 more)

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.14
Nodes (7): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestSalienceScoring

### Community 41 - "test_timeline.py"
Cohesion: 0.13
Nodes (29): make_action(), make_goal(), make_mood(), make_move(), make_plan(), make_thought(), The vocabulary of Jenbina's life events, their one-line titles, and the…, One entry of Jenbina's day. ``title`` is the line the timeline shows. (+21 more)

### Community 42 - "UserDatabase"
Cohesion: 0.04
Nodes (28): Connection, datetime, SQLite user database for authentication and conversation persistence., SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id. (+20 more)

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
Cohesion: 0.08
Nodes (23): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person…, Parse BasicNeeds from JSON string stored in metadata (+15 more)

### Community 49 - "timedelta"
Cohesion: 0.10
Nodes (11): Update need satisfaction over time, Test temporal memory retrieval, Test temporal memory retrieval with event type filter, Test needs history retrieval, Test getting history for all needs, Test updating all needs over time, Test need satisfaction decay over time, Test storing action memory with people and location (+3 more)

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
Nodes (10): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Decay all emotions toward their baselines based on elapsed time., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}. (+2 more)

### Community 55 - ".get_needs_summary"
Cohesion: 0.12
Nodes (10): Any, Get average satisfaction for a specific level, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+2 more)

### Community 56 - "create_asimov_check_system"
Cohesion: 0.09
Nodes (24): Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead., create_state_analysis_system(), Any (+16 more)

### Community 57 - "TestHybridMemorySystem"
Cohesion: 0.09
Nodes (12): Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test memory statistics, Test person relationships when Neo4j is not available, Test error handling in memory operations (+4 more)

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
Cohesion: 0.18
Nodes (8): fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function., TestFixLlmJson

### Community 62 - "build_timeline"
Cohesion: 0.15
Nodes (7): build_timeline(), Render the rows in order; an empty list shows the empty-state marker., Merge chat messages and life events by time, apply the filter, keep the newest…, render_timeline(), TestBuildTimeline, TestCorruptRows, TestRenderTimeline

### Community 63 - "make_mock_llm"
Cohesion: 0.17
Nodes (8): make_experience(), make_mock_llm(), Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystem, TestGoalSystemIntegration, TestGoalSystemMilestone, TestGoalSystemProgress

### Community 64 - "check"
Cohesion: 0.29
Nodes (9): check(), main(), Every output image, keyed by path relative to ``assets/sprites``., Write every sheet, the avatar and the icons under ``out_dir``. When ``favicon``…, Relative paths under ``out_dir`` (plus the favicon) that are missing, differ…, render_all(), write_all(), Path (+1 more)

### Community 65 - "test_sprites.py"
Cohesion: 0.18
Nodes (6): all_layers(), Tests for the pixel sprite pipeline (core.ui.sprites)., TestArtLayers, TestPalette, TestPortraits, TestTimelineIcons

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "make_plan"
Cohesion: 0.22
Nodes (3): make_plan(), TestPlan, TestPlanningSystemReplan

### Community 68 - "TestCheckInjectionBlock"
Cohesion: 0.05
Nodes (21): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+13 more)

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "TestChains"
Cohesion: 0.09
Nodes (25): callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_meta_cognitive_action_chain(), Enhanced action decision with meta-cognitive monitoring, Cognition and Decision Making Submodule This submodule handles all aspects of…, WorldState, Chain Tests README (+17 more)

### Community 72 - "Design"
Cohesion: 0.11
Nodes (18): 10. Code changes, 1. Pages, 2. Shell, 3. Left column: the timeline, 4. The event log, 5. Right column: the status rail, 6. The runner, 7. Bug fixes in scope (+10 more)

### Community 73 - "TestConversation"
Cohesion: 0.13
Nodes (8): Test that last_interaction updates when adding messages, Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, TestConversation

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.20
Nodes (8): Initialize social interaction tracker., Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts., Tracks all of Jenbina's social interactions during the session. Only the…, SocialInteractionTracker

### Community 75 - "history_context"
Cohesion: 0.27
Nodes (6): history_context(), ``section[key]`` for the nested world-summary shape, the value itself for a…, ``(recent_actions, world_context)`` read from the records the runners append to…, _summary_field(), history_context reads the records the runners append to simulation_history., TestHistoryContext

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

### Community 83 - "EventLog"
Cohesion: 0.08
Nodes (17): EventLog, Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., NullRail, A rail that draws nothing: headless runs and tests., build_env(), _plan_fixture() (+9 more)

### Community 84 - "_make_mock_llm"
Cohesion: 0.15
Nodes (11): _make_mock_llm(), Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data., Whitespace is stripped from the LLM response., Without social cognition, the no-dossier prompt is used. (+3 more)

### Community 85 - "3_🌍_Environment.py"
Cohesion: 0.21
Nodes (14): Jenbina — Environment & Debug page., Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar (+6 more)

### Community 86 - "Message"
Cohesion: 0.12
Nodes (11): Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Reconstruct a Person from a JSON string. Args: json_str: JSON produced by…, Get all messages of a specific type, Tests for the Message dataclass., TestMessage, Test Message functionality (+3 more)

### Community 87 - "TestTitles"
Cohesion: 0.15
Nodes (7): lessons_text(), mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, Lessons as one line: lists joined with '; ', strings as they are., ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 88 - "Emotion"
Cohesion: 0.25
Nodes (4): Emotion, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "display_jenbina_image"
Cohesion: 0.10
Nodes (14): _data_uri(), Base64 data URI of a committed asset, cached for the process lifetime. Assets…, The animated sprite for ``state`` with an optional caption. ``scale`` 4 is the…, sprite_html(), display_jenbina_image(), _portrait_path(), Show the painterly portrait for the state named by ``image_path`` in a game…, The portrait file for ``state``, the ``base`` portrait if that is missing, else… (+6 more)

### Community 90 - ".record_social_action"
Cohesion: 0.25
Nodes (4): Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Generate a simple automatic sentiment string., Try to extract a person/entity name from a simulated action string. The action…

### Community 91 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 92 - "HybridMemorySystem"
Cohesion: 0.11
Nodes (14): HybridMemorySystem, Any, datetime, OpenAI embeddings client, built lazily so an API key is only needed once…, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Retrieve memories based on semantic similarity (+6 more)

### Community 93 - "SocialInteraction"
Cohesion: 0.29
Nodes (4): Any, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, TestSocialInteraction

### Community 94 - "MemoryEvent"
Cohesion: 0.14
Nodes (11): MemoryEvent, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID, Store event in ChromaDB for semantic search, Store event relationships in Neo4j, Represents a memory event with all its components, Store event in SQLite for chronological tracking, Test MemoryEvent functionality (+3 more)

### Community 95 - "compose"
Cohesion: 0.36
Nodes (3): compose(), Draw ``layers`` in order onto a transparent RGBA canvas. A ``"."`` pixel leaves…, TestCompose

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

### Community 100 - "run_single_iteration"
Cohesion: 0.11
Nodes (25): action_icon(), delta_badge_html(), event_html(), The icon name for an action's row, by keyword; the star when none fits., One timeline row for a life event. ``details`` is ``(summary, body)`` rendered…, The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests., _now_hhmm(), _print_json() (+17 more)

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "render_frame"
Cohesion: 0.25
Nodes (6): frame_layers(), FrameSpec, Body, hair, face, props, effects — in drawing order., render_frame(), Layer, TestActionSheets

### Community 103 - "make_experience"
Cohesion: 0.21
Nodes (5): make_experience(), Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete., TestPlanningSystemEvaluation, TestPlanningSystemIntegration

### Community 105 - "build.py"
Cohesion: 0.36
Nodes (6): _file_matches(), _pixels(), png_bytes(), Pillow compositor and build CLI for the pixel sprites. Run ``python -m…, PNG encoding with fixed settings and no timestamps. Bytes are stable for one…, Image

### Community 106 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 108 - "render_sheet"
Cohesion: 0.43
Nodes (3): The 96x48 two-frame sheet for ``state``; unknown state raises KeyError., render_sheet(), TestEmotionSheets

### Community 111 - "generate_proactive_message"
Cohesion: 0.27
Nodes (3): generate_proactive_message(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, TestGenerateProactiveMessage

### Community 112 - "6_🔑_Admin.py"
Cohesion: 0.40
Nodes (5): _is_admin(), _is_local_request(), Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, Check if the request originates from localhost., Return True if the current visitor is allowed to see the admin panel.

### Community 113 - "art.py"
Cohesion: 0.14
Nodes (8): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, Pixel sprite assets for the Jenbina UI. Only paths and constants live here;…, Path of the 96x48 sheet for ``state``; unknown states get the ``base`` sheet., sprite_path(), Palette for the pixel art. One character per color in the art strings. This…, TestPaths

### Community 114 - "simulation.py"
Cohesion: 0.07
Nodes (36): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, check_proactive_message(), get_event_log(), _get_user_db_and_id(), handle_user_input(), Chat UI components for Jenbina app, Return (UserDatabase, user_id) if authenticated, else (None, None). (+28 more)

### Community 115 - "Jenbina Blob Character"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "clear_chromadb.py"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 117 - "_make_mock_llm_failing"
Cohesion: 0.17
Nodes (7): _make_mock_llm_failing(), Falls back to static greeting on LLM failure (gap < 6h)., Falls back to static greeting on LLM failure (6-24h)., Falls back to static greeting on LLM failure (24-72h)., Falls back to static greeting on LLM failure (>72h)., Falls back to static greeting when LLM fails., Create a mock LLM that raises an exception.

### Community 118 - "SimpleEmbeddings"
Cohesion: 0.20
Nodes (6): Initialize or load the Chroma vector store, Simple hash-based embeddings for when OpenAI is not available, Generate a simple hash-based embedding, Embed multiple documents, Initialize Chroma-based memory manager Args: embeddings_provider: Which…, SimpleEmbeddings

### Community 120 - ".create_plan"
Cohesion: 0.20
Nodes (5): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id.

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 122 - "auth_page.py"
Cohesion: 0.27
Nodes (9): _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only., Return path to Google credentials file. Locally, reads…, Return the OAuth redirect URI. Uses the ``REDIRECT_URI`` env var if set…, Return a shared UserDatabase instance via session state., Show Google sign-in. Returns True once authenticated. (+1 more)

### Community 123 - "shared_init.py"
Cohesion: 0.08
Nodes (41): _latest_world(), main(), Jenbina - AGI Simulation Streamlit App Main entry point — the home screen: the…, ``(world_summary, chosen_action)`` of the last iteration this session, or…, _top_goal(), Jenbina — Console Log page., Jenbina — Debug Info page., Show logged-in user info and a logout button in the sidebar. (+33 more)

### Community 125 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 128 - "generate_first_greeting"
Cohesion: 0.39
Nodes (3): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting

### Community 129 - "match_action_key"
Cohesion: 0.36
Nodes (3): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, TestActionKeywordMatch

### Community 136 - "MaslowNeed"
Cohesion: 0.07
Nodes (18): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Initialize all needs in Maslow's hierarchy, Initialize all needs across all five levels, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy (+10 more)

### Community 137 - "Deploying Jenbina to Railway"
Cohesion: 0.25
Nodes (7): Deploying, Deploying Jenbina to Railway, Environment variables, Not deployed yet: the scheduler, Optional: Neo4j, Setting up from scratch, The existing deployment

### Community 139 - "TestChainRealWorldScenarios"
Cohesion: 0.29
Nodes (4): Test chains with realistic scenarios, Test chains in a morning routine scenario, Test chains in a stressful situation, TestChainRealWorldScenarios

### Community 140 - "TestChainEdgeCases"
Cohesion: 0.29
Nodes (4): Test edge cases and boundary conditions for chains, Test chains with empty or minimal needs, Test chains with very large world descriptions, TestChainEdgeCases

### Community 141 - "render_icon"
Cohesion: 0.40
Nodes (3): One 8x8 icon; unknown name raises KeyError., render_icon(), TestIcons

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls
- `run_simulation_loop()` → `APScheduler (background scheduling)`  [AMBIGUOUS]
  requirements.txt · relation: conceptually_related_to

## Knowledge Gaps
- **60 isolated node(s):** `The existing deployment`, `Deploying`, `Setting up from scratch`, `Environment variables`, `Optional: Neo4j` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `run_simulation_loop()` and `APScheduler (background scheduling)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Person` connect `Person` to `InnerMonologueSystem`, `world_state.py`, `CLAUDE.md Project Instructions`, `MaslowNeedsSystem`, `test_pixel_ui.py`, `SocialCognitionSystem`, `TestChainRealWorldScenarios`, `TestChainEdgeCases`, `InsightSystem`, `CuriositySystem`, `TestPerson`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `SelfNarrativeSystem`, `Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)`, `simulation_runner.py`, `GoalSystem`, `PlanningSystem`, `TestMemoryIntegration`, `_invoke_and_parse`, `Experience`, `WorkingMemorySystem`, `MemoryIntegration`, `Goal`, `Plan`, `EmotionSystem`, `create_asimov_check_system`, `TestChains`, `SocialInteractionTracker`, `infer_emotional_tone`, `Conversation`, `EventLog`, `Message`, `shared_init.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `CLAUDE.md Project Instructions` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `TestCheckInjectionBlock`, `MaslowNeedsSystem`, `test_pixel_ui.py`, `TestChains`, `StreamCapture`, `maslow_needs.py`, `requirements.txt Dependency Manifest`, `ChromaMemoryManager`, `Deep Emotional Mirror Implementation Plan`, `fix_llm_json`, `clear_chromadb.py`, `create_asimov_check_system`, `Test Suite README`, `shared_init.py`, `HybridMemorySystem`, `get_llm`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `Jenbina README` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `GoalSystem`, `MetaCognitiveSystem`, `TestChains`, `EnvironmentSimulator`, `Person`, `SocialCognitionSystem`, `requirements.txt Dependency Manifest`, `InsightSystem`, `CuriositySystem`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `SelfNarrativeSystem`, `EmotionSystem`, `create_asimov_check_system`, `Test Suite README`, `shared_init.py`, `get_llm`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `Jenbina README` and `Reptile Brain (motivational core)`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `WorkingMemorySystem` (e.g. with `Experience` and `MaslowNeedsSystem`) actually correct?**
  _`WorkingMemorySystem` has 15 INFERRED edges - model-reasoned connections that need verification._