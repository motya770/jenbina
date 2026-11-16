# Graph Report - jenbina-launch-readiness-8129fa  (2026-11-16)

## Corpus Check
- 174 files · ~485,827 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3469 nodes · 7379 edges · 167 communities (143 shown, 24 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 450 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `962d1b2e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_llm
- DynamicEventsSystem
- CLAUDE.md Project Instructions
- needs/__init__.py
- MetaCognitiveSystem
- Lesson
- Person
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- .update_all_needs
- Test Suite Workflow (push/manual)
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
- Inner Life Surfacing via Prompt Engineering
- TestEnvironmentSimulator
- StreamCapture
- BeingStore
- get_llm
- PaloAltoLocationSystem
- test_chat_handler.py
- GoalSystem
- PlanningSystem
- host.py
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- create_action_decision_chain
- TestExperience
- WorkingMemorySystem
- test_timeline.py
- UserDatabase
- MemoryIntegration
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- TestCheckInjectionBlock
- handle_chat_interaction
- Need
- Plan
- TestLesson
- EmotionSystem
- .advance
- create_asimov_check_system
- MemoryEvent
- core/__init__.py
- TestUserCRUD
- WorkingMemoryItem
- JenbinaHost
- test_user_db.py
- MaslowNeedsSystem
- test_live.py
- test_sprites.py
- _run_one_iteration
- make_plan
- PersonModel
- FirebaseAuth
- Conversation
- simulation_runner.py
- Design
- TestConversation
- SocialInteractionTracker
- history_context
- test_simulation.py
- File Structure
- .deserialize
- infer_emotional_tone
- Design
- Conversation
- test_working_memory.py
- test_simulation_runner.py
- EventLog
- TestOwnership
- TestMessage
- TestTitles
- Emotion
- display_jenbina_image
- .record_social_action
- streamlit_server
- Any
- SocialInteraction
- HybridMemorySystem
- StatusRail
- Review Focus
- fix_llm_json
- .get_current_step
- generate_first_greeting
- adoption.py
- make_needs
- TestLease
- .get_needs_summary
- simulation.py
- .generate_insight
- Step
- .from_dict
- .fresh
- auth_page.py
- LifeEventLog
- Design
- is_admin
- SimpleEmbeddings
- ChatTurn
- Jenbina Blob Character
- clear_chromadb.py
- main
- .test_full_plan_lifecycle
- test_pixel_ui.py
- Blade Runner 2049 Theme Redesign
- TestFocusNoise
- maslow_needs.py
- app.py
- TestContextSwitch
- File Structure
- .update
- .from_dict
- choose_outreach_target
- sidebar.py
- MaslowNeed
- TestAdoption
- TestBasicNeedsBackwardCompatibility
- sprite_path
- test_privacy.py
- test_heartbeat_host.py
- TestUiExports
- build_timeline
- build_person
- stage_pill_html
- TestEvents
- TestStateAndEvents
- TestChainEdgeCases
- FakeEmotions
- TestPerPersonInsights
- TestMessages
- run_heartbeat.py
- .suspend_until
- TestSharedHost
- .test_handles_search_failure
- TestPromptTemplates
- heartbeat/__init__.py
- TestGrowthStageLadder
- .get_planning_stats
- .add_note
- _StatusSink
- .from_dict
- .add_conversation
- TestAdminMessageCounts
- TestMessageOrdering
- init_session_state

## God Nodes (most connected - your core abstractions)
1. `Person` - 119 edges
2. `GoalSystem` - 81 edges
3. `WorkingMemorySystem` - 76 edges
4. `PlanningSystem` - 65 edges
5. `InnerMonologueSystem` - 64 edges
6. `Person` - 64 edges
7. `UserDatabase` - 62 edges
8. `MaslowNeedsSystem` - 59 edges
9. `JenbinaHost` - 47 edges
10. `CLAUDE.md Project Instructions` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Goal System Design` --semantically_similar_to--> `create_maslow_goal_setter()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-07-goal-system-design.md → core/needs/maslow_decision_chain.py
- `query_llm_knowledge() (planned function)` --semantically_similar_to--> `search_web()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md → core/research/user_research.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration_headless()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/simulation_runner.py
- `Goal System Design` --references--> `create_action_decision_chain()`  [INFERRED]
  docs/plans/2026-02-07-goal-system-design.md → core/cognition/action_decision_chain.py
- `Planning System Design` --references--> `create_action_decision_chain()`  [INFERRED]
  docs/plans/2026-02-07-planning-system-design.md → core/cognition/action_decision_chain.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Deep Emotional Mirror feature flow (research -> dossier -> insights -> greetings -> chat)** — core_research_user_research_research_user, core_research_user_research_generate_user_dossier, core_social_social_cognition_personmodel, core_insights_insight_system_insightsystem, core_interaction_chat_handler_handle_chat_interaction, core_interaction_chat_handler_generate_first_greeting, core_interaction_chat_handler_generate_return_greeting, core_ui_chat_check_return_greeting, core_ui_shared_init_init_session_state, core_ui_shared_init_init_llm, core_interaction_guardrails_jenbina_system_prompt [EXTRACTED 1.00]
- **Jenbina Visual Identity (pink blob mascot, happy expression, Tamagotchi styling)** — assets_favicon, assets_favicon_jenbina_blob_character, assets_favicon_content_happy_expression, assets_favicon_tamagotchi_mascot_design [INFERRED 0.85]
- **Motivation-to-action stack injected into the action decision prompt (working memory, plan step, goals, lessons)** — core_working_memory_working_memory_system_workingmemorysystem, core_planning_planning_system_planningsystem, core_goals_goal_system_goalsystem, core_learning_learning_system_learningsystem, core_needs_maslow_needs_maslowneedssystem, core_cognition_action_decision_chain_create_action_decision_chain [INFERRED 0.85]

## Communities (167 total, 24 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "_make_mock_llm"
Cohesion: 0.06
Nodes (26): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+18 more)

### Community 2 - "DynamicEventsSystem"
Cohesion: 0.11
Nodes (14): DynamicEventsSystem, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API, Flexible system to fetch real-time events and venue information (+6 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.11
Nodes (40): .env.example template, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, CLAUDE.md Project Instructions, Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), Environment Variables (.env / .env.example), Layered Architecture (UI -> Interaction -> Cognition -> Core -> DB -> LLM) (+32 more)

### Community 4 - "needs/__init__.py"
Cohesion: 0.20
Nodes (14): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+6 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.08
Nodes (20): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+12 more)

### Community 6 - "Lesson"
Cohesion: 0.08
Nodes (15): Lesson, A learned pattern extracted from experiences., Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, Test format_lessons_for_prompt (+7 more)

### Community 7 - "Person"
Cohesion: 0.06
Nodes (18): Person, Any, Initialize the insight system with an LLM instance., Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Get a summary of conversation with a specific outsider, Get overall communication statistics, Return a first-person narrative of Jenbina's social day. (+10 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.10
Nodes (16): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Get local events based on Palo Alto location system, Get a natural language description of the current environment (+8 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.12
Nodes (9): Initialize social cognition / theory-of-mind system., Tracks social models and chooses social strategy for conversations., Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., Choose when to be nice, polite, or assertive., Predict likely reaction from relationship + inferred emotional state., Build a concise ToM context block for LLM prompting., SocialCognitionSystem (+1 more)

### Community 10 - "rail.py"
Cohesion: 0.14
Nodes (20): HeartStatus, _about_you_lines(), _card_title(), env_line_html(), _goal_lines(), heartbeat_lines(), _lesson_lines(), _plan_lines() (+12 more)

### Community 11 - ".update_all_needs"
Cohesion: 0.29
Nodes (5): datetime, timedelta, Update all needs based on time passed, Update the current growth stage based on need satisfaction, Update need satisfaction over time

### Community 12 - "Test Suite Workflow (push/manual)"
Cohesion: 0.31
Nodes (9): .coveragerc coverage config, GitHub Actions Workflows README, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action), Test Suite Workflow (push/manual), GitHub Actions CI/CD, pytest / pytest-cov / pytest-playwright / pytest-timeout (+1 more)

### Community 13 - "InsightSystem"
Cohesion: 0.19
Nodes (6): InsightSystem, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Generates deep perceptive observations about users mid-conversation., _make_mock_llm(), dict, TestInsightSystem

### Community 14 - "CuriositySystem"
Cohesion: 0.10
Nodes (9): CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., Initialize curiosity / exploration system., TestCuriositySystem (+1 more)

### Community 15 - "Person"
Cohesion: 0.09
Nodes (11): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+3 more)

### Community 16 - "TestPerson"
Cohesion: 0.05
Nodes (19): Test Person functionality, Test person initialization, Test person with default name, Test updating all needs, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider (+11 more)

### Community 17 - "LearningSystem"
Cohesion: 0.07
Nodes (27): Learning system for Jenbina - extracts lessons from experiences, Experience, LearningSystem, Any, Learning system for Jenbina — records experiences, extracts lessons, and…, Records experiences, extracts lessons via LLM, and formats them for prompts., Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3). (+19 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.14
Nodes (23): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, build_search_query(), generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,… (+15 more)

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
Nodes (9): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., Exception, _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateProactiveMessage (+1 more)

### Community 23 - "memory/__init__.py"
Cohesion: 0.15
Nodes (12): LocationNode, PersonNode, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, create_memory_integration(), Memory Integration Module Shows how to integrate the hybrid memory system with…, Create a memory integration instance with default settings Returns:… (+4 more)

### Community 24 - "Test Suite README"
Cohesion: 0.25
Nodes (8): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), Run a specific test module, run_specific_test(), Run all tests and provide comprehensive reporting, run_comprehensive_tests()

### Community 25 - "Inner Life Surfacing via Prompt Engineering"
Cohesion: 0.60
Nodes (6): Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals

### Community 26 - "TestEnvironmentSimulator"
Cohesion: 0.11
Nodes (10): Calculate how environment affects mood, TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator (+2 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "BeingStore"
Cohesion: 0.14
Nodes (11): BeingStore, Lease, Connection, datetime, timedelta, Save only for the current lease holder when an owner is supplied., The newest events, oldest first, in UserDatabase.get_events format., Copy a user's event rows, keeping their timestamps and content. (+3 more)

### Community 29 - "get_llm"
Cohesion: 0.10
Nodes (19): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Use a finite positive timeout, falling back to sixty seconds., Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service… (+11 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.08
Nodes (16): PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type, Get locations within a certain radius of current location (+8 more)

### Community 31 - "test_chat_handler.py"
Cohesion: 0.12
Nodes (11): basic_needs_to_json(), _build_subsystem_context(), create_metadata_from_person_state(), Convert BasicNeeds object to JSON-serializable format, Create metadata dictionary from person state and other context, Extract formatted context from all person subsystems. Returns a list of (label,…, Interaction and Communication Submodule This submodule handles all aspects of…, Tests for core/interaction/chat_handler.py — chat orchestration. (+3 more)

### Community 32 - "GoalSystem"
Cohesion: 0.07
Nodes (21): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals), Hybrid Goal Progress Tracking (+13 more)

### Community 33 - "PlanningSystem"
Cohesion: 0.15
Nodes (8): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation, TestPlanningSystemReplan, TestPlanningSystemSerialization, TestPlanningSystemStats

### Community 34 - "host.py"
Cohesion: 0.14
Nodes (17): Own the single live mind, its process lease, and its continuous rhythm., Ask the heart for a moment now, without waiting for it. The heart takes it on…, beats_today(), _elapsed(), is_night(), lost_time(), next_beat_at(), datetime (+9 more)

### Community 35 - "TestEmotion"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "TestMemoryIntegration"
Cohesion: 0.06
Nodes (17): Test storing action memory, Test storing action memory with people and location, Test storing need change memory, Test storing need change memory with current needs state, Test MemoryIntegration functionality, Test getting relevant context for a query, Test getting context for a specific person, Test getting recent memories (+9 more)

### Community 37 - "TestMaslowNeedsSystem"
Cohesion: 0.07
Nodes (15): Test the complete Maslow needs system, Test system initialization with all needs, Test updating all needs over time, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs (+7 more)

### Community 38 - "create_action_decision_chain"
Cohesion: 0.12
Nodes (18): callable, create_action_decision_chain(), _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_meta_cognitive_action_chain() (+10 more)

### Community 39 - "TestExperience"
Cohesion: 0.14
Nodes (7): Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set, Test that world_context defaults to empty dict, Test Experience dataclass, Test experience stores all fields, Test serialization to dict, TestExperience

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.12
Nodes (8): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestFormatting, TestSalienceScoring

### Community 41 - "test_timeline.py"
Cohesion: 0.13
Nodes (32): format_duration(), make_action(), make_gap(), make_goal(), make_mood(), make_plan(), make_sleep(), make_thought() (+24 more)

### Community 42 - "UserDatabase"
Cohesion: 0.09
Nodes (18): Connection, datetime, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first. (+10 more)

### Community 43 - "MemoryIntegration"
Cohesion: 0.12
Nodes (15): example_usage(), MemoryIntegration, Any, Person, Integrates the hybrid memory system with Jenbina's existing components, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person… (+7 more)

### Community 45 - "TestEmotionSystem"
Cohesion: 0.08
Nodes (13): Test EmotionSystem functionality, Should initialize with 8 Plutchik emotions, Check Jenbina's character baselines, Initially, intensity should equal base_intensity, Should spike the named emotion, Triggering unknown emotion should be a no-op, Should apply multiple adjustments at once, Should return top-k emotions by intensity (+5 more)

### Community 47 - "Goal"
Cohesion: 0.12
Nodes (7): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing., Goal Horizons (short / mid / long-term)

### Community 48 - "ChromaMemoryManager"
Cohesion: 0.07
Nodes (26): clear_memory(), _chat_avatar(), Avatar for a chat row: Jenbina's portrait, or Streamlit's own user icon.…, ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Generate a unique ID for the embedding (+18 more)

### Community 49 - "TestCheckInjectionBlock"
Cohesion: 0.05
Nodes (21): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+13 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "Need"
Cohesion: 0.09
Nodes (13): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Legacy needs property that maps to Maslow needs, Test the legacy Need class (+5 more)

### Community 52 - "Plan"
Cohesion: 0.11
Nodes (13): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., Use LLM to decompose a goal into steps., Get active plan for a given goal id., An ordered sequence of steps to achieve a goal., Planning System Design (+5 more)

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.13
Nodes (10): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}., Get the top-k emotions by intensity. (+2 more)

### Community 55 - ".advance"
Cohesion: 0.11
Nodes (4): HostCase, TestLostTime, TestSleep, TestTurnsAndStepOnce

### Community 56 - "create_asimov_check_system"
Cohesion: 0.14
Nodes (15): _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead., create_state_analysis_system(), Any, BaseLLM (+7 more)

### Community 57 - "MemoryEvent"
Cohesion: 0.07
Nodes (21): MemoryEvent, Represents a memory event with all its components, Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval (+13 more)

### Community 58 - "core/__init__.py"
Cohesion: 0.11
Nodes (27): Event, Venue, EnvironmentState, Environment and World Simulation Submodule This submodule handles all aspects…, Location, Neighborhood, create_comprehensive_world_state(), _format_current_events() (+19 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.24
Nodes (4): Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "JenbinaHost"
Cohesion: 0.18
Nodes (5): JenbinaHost, datetime, timedelta, Stop the heart, save her and release the lease. With ``patience`` (seconds) it…, Consume a pending request; True when the beat should run now.

### Community 62 - "test_user_db.py"
Cohesion: 0.09
Nodes (7): Test UserDatabase initialisation and table creation., Test person state save/load., Messages from one user should not leak to another., TestIsolation, TestListPersonStates, TestPersonState, TestUserDatabase

### Community 63 - "MaslowNeedsSystem"
Cohesion: 0.10
Nodes (12): MaslowNeedsSystem, Complete Maslow's hierarchy of needs system, Initialize all needs in Maslow's hierarchy, Initialize all needs across all five levels, Satisfy a specific need, Calculate weighted overall satisfaction across all levels, Get list of needs that are critically low, prioritized by level, Get list of needs that are low, prioritized by level (+4 more)

### Community 64 - "test_live.py"
Cohesion: 0.19
Nodes (7): NotHostingError, She is not (or no longer) living in this process., draw_guarded(), Periodic UI drawing that tolerates changes to the live mind., Live drawing and shared-host session integration without external services., TestHomeScreen, TestLiveDrawing

### Community 65 - "test_sprites.py"
Cohesion: 0.05
Nodes (40): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, check(), compose(), _file_matches(), frame_layers(), main() (+32 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "make_plan"
Cohesion: 0.22
Nodes (4): make_experience(), make_plan(), TestPlan, TestPlanningSystemEvaluation

### Community 68 - "PersonModel"
Cohesion: 0.18
Nodes (6): Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, RelationshipState, TestPersonSocialSerialization

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "simulation_runner.py"
Cohesion: 0.06
Nodes (40): create_world_description_system(), BaseLLM, Creates and returns a function that generates world descriptions. Args: llm:…, create_basic_needs_chain(), Legacy function for backward compatibility - now uses Maslow decision system, _check_proactive_triggers(), credit_completed_plan(), _detect_location_from_action() (+32 more)

### Community 72 - "Design"
Cohesion: 0.11
Nodes (18): 10. Code changes, 1. Pages, 2. Shell, 3. Left column: the timeline, 4. The event log, 5. Right column: the status rail, 6. The runner, 7. Bug fixes in scope (+10 more)

### Community 73 - "TestConversation"
Cohesion: 0.13
Nodes (8): Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, Test that last_interaction updates when adding messages, TestConversation

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.18
Nodes (9): Initialize social interaction tracker., Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts. ``names=False``…, Tracks all of Jenbina's social interactions during the session. Only the…, SocialInteractionTracker (+1 more)

### Community 75 - "history_context"
Cohesion: 0.27
Nodes (6): history_context(), ``section[key]`` for the nested world-summary shape, the value itself for a…, ``(recent_actions, world_context)`` read from the records the runners append to…, _summary_field(), history_context reads the records the runners append to simulation_history., TestHistoryContext

### Community 76 - "test_simulation.py"
Cohesion: 0.20
Nodes (9): fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the home screen loads with the timeline and heartbeat card., Click 'Step once' and verify the rail and the timeline fill in., sim_page() (+1 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - ".deserialize"
Cohesion: 0.15
Nodes (7): Reconstruct a Person from a JSON string. Args: json_str: JSON produced by…, Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 79 - "infer_emotional_tone"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Conversation"
Cohesion: 0.09
Nodes (15): Person Management Submodule This submodule handles the AI's person…, Conversation, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation (+7 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "test_simulation_runner.py"
Cohesion: 0.08
Nodes (14): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, build_env(), HeadlessFixture, _plan_fixture(), A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a…, Two plans: one finished earlier, one whose last step completes this iteration;…, TestActionKeywordMatch (+6 more)

### Community 84 - "EventLog"
Cohesion: 0.13
Nodes (8): EventLog, make_move(), Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., A move, only when the location actually changed., record_move(), TestEventLog

### Community 85 - "TestOwnership"
Cohesion: 0.08
Nodes (3): TestBeats, TestOwnership, TestUnreadableState

### Community 86 - "TestMessage"
Cohesion: 0.29
Nodes (4): Test Message functionality, Test message initialization, Test message with default values, TestMessage

### Community 87 - "TestTitles"
Cohesion: 0.14
Nodes (7): lessons_text(), mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, Lessons as one line: lists joined with '; ', strings as they are., ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 88 - "Emotion"
Cohesion: 0.18
Nodes (6): Emotion, datetime, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "display_jenbina_image"
Cohesion: 0.12
Nodes (12): portrait_caption_html(), The name strip under the rail portrait., display_jenbina_image(), _portrait_path(), The portrait file for ``state``, the ``base`` portrait if that is missing, else…, Show the painterly portrait for the state named by ``image_path``, unaltered in…, patch, TestChatHandlerAvatars (+4 more)

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

### Community 95 - "StatusRail"
Cohesion: 0.11
Nodes (12): NullRail, A rail that draws nothing: headless runs and tests., Handles on the Now card's placeholders, plus the timeline's live slot., Append a row to the timeline's live slot (a thought or action in progress)., StatusRail, FakePerson, The markup of one needs-bar row, from its class to the next row., rendered() (+4 more)

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "fix_llm_json"
Cohesion: 0.15
Nodes (10): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility. (+2 more)

### Community 98 - ".get_current_step"
Cohesion: 0.14
Nodes (6): Extract steps array from various LLM response formats., Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Mark current step completed and move to next.

### Community 99 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 100 - "adoption.py"
Cohesion: 0.16
Nodes (16): adopt_existing(), AdoptionReport, choose_user_to_adopt(), _experience_count(), _import_partner(), datetime, Person, Adopt one existing mind and retain each account's own relationship with her. (+8 more)

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "TestLease"
Cohesion: 0.13
Nodes (3): StoreTestCase, TestLease, TestPeople

### Community 103 - ".get_needs_summary"
Cohesion: 0.12
Nodes (10): Any, Get average satisfaction for a specific level, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+2 more)

### Community 104 - "simulation.py"
Cohesion: 0.13
Nodes (18): Redraw mood, place, doing/goal lines, needs bars and emotion chips., _css_token(), get_jenbina_image_for_action(), Portrait and state renderers for Jenbina's UI., Render Maslow needs as thin bars; a need below 30% is marked critical., Lower-case ``name`` reduced to [a-z0-9_] so it is safe inside a class attribute., Render the strongest emotions (above 15, at most four) as text chips; the…, Render a badge with Jenbina's dominant mood, styled positive or negative. (+10 more)

### Community 105 - ".generate_insight"
Cohesion: 0.18
Nodes (6): Any, Check if conditions are met to generate a subtle insight.…, Generate a subtle perceptive observation about the user. Returns the insight…, Check if we should fire the bold first-impression insight., Generate a bold, striking first-impression observation. Returns the insight…, date

### Community 106 - "Step"
Cohesion: 0.25
Nodes (8): decide(), effective_interval(), Choose one action without mutating the situation or consulting the clock., Step, asleep(), awake(), TestAsleep, TestAwake

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 109 - "auth_page.py"
Cohesion: 0.21
Nodes (11): _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only., Show logged-in user info and a logout button in the sidebar., Return path to Google credentials file. Locally, reads…, Return the OAuth redirect URI. Uses the ``REDIRECT_URI`` env var if set…, Return a shared UserDatabase instance via session state. (+3 more)

### Community 111 - "Design"
Cohesion: 0.10
Nodes (19): 1. One owner, 2. One record, 3. The rhythm, 4. Sleep, 5. Lost time, 6. Chat, 7. Many people, one Jenbina, 8. The home screen (+11 more)

### Community 112 - "is_admin"
Cohesion: 0.19
Nodes (12): Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, _hostname(), is_admin(), is_local_request(), The shared admin access check for the Admin page and heartbeat card., ``localhost`` from ``localhost:8501`` or ``http://localhost:8501``., Whether the request names this machine as its host. The Host and Origin headers…, Return True if the current visitor is allowed to see the admin panel. With… (+4 more)

### Community 113 - "SimpleEmbeddings"
Cohesion: 0.20
Nodes (6): Initialize or load the Chroma vector store, Simple hash-based embeddings for when OpenAI is not available, Generate a simple hash-based embedding, Embed multiple documents, Initialize Chroma-based memory manager Args: embeddings_provider: Which…, SimpleEmbeddings

### Community 114 - "ChatTurn"
Cohesion: 0.22
Nodes (10): ChatTurn, handle_user_input(), Handle one submitted chat message and return the chat result, or ``None`` when…, patch, TestHandleUserInput, TestHistoryShapedContext, TestOutreachTypes, _FakeSessionState (+2 more)

### Community 115 - "Jenbina Blob Character"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "clear_chromadb.py"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 117 - "main"
Cohesion: 0.16
Nodes (3): main(), RuntimeError, TestHeartbeatMain

### Community 118 - ".test_full_plan_lifecycle"
Cohesion: 0.40
Nodes (3): Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete., TestPlanningSystemIntegration

### Community 119 - "test_pixel_ui.py"
Cohesion: 0.08
Nodes (22): action_icon(), _data_uri(), delta_badge_html(), dialog_html(), event_html(), icon_html(), nav_icon_css(), The icon name for an action's row, by keyword; the star when none fits. (+14 more)

### Community 120 - "Blade Runner 2049 Theme Redesign"
Cohesion: 0.12
Nodes (16): 1. Palette, 2. Type, 3. Shell, 4. Timeline, 5. Status rail, 6. Code changes, 7. Sidebar and tab icon, Anti-goals (what would make this a failure even if it works) (+8 more)

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 122 - "maslow_needs.py"
Cohesion: 0.29
Nodes (7): NeedCategory, NeedLevel, Enum, Maslow's hierarchy levels, Categories within each need level, Add a new need to the system, Create from dictionary

### Community 123 - "app.py"
Cohesion: 0.07
Nodes (41): _latest_world(), main(), Jenbina's home screen: a private conversation beside her shared live state., World and chosen action from the host's most recent moment. The world summary…, process_host(), The one host of this process, built on first use. Kept on ``sys`` rather than…, Jenbina — Environment & Debug page., Jenbina — Console Log page. (+33 more)

### Community 125 - "File Structure"
Cohesion: 0.11
Nodes (17): Changes made after the tasks, from review, Decisions this plan makes inside the spec's "left to the builder", File Structure, Global Constraints, Heartbeat Implementation Plan, Review Focus, Task 10: End-to-end tests, docs, final check, Task 1: Storage for the being (+9 more)

### Community 126 - ".update"
Cohesion: 0.24
Nodes (3): Any, Buffer capacity based on focus: 3 (exhausted) to 7 (rested)., Recalculate working memory from current state. Called once per cycle.

### Community 128 - "choose_outreach_target"
Cohesion: 0.19
Nodes (6): choose_outreach_target(), datetime, Choose one recent conversation partner for a proactive message., Prefer closeness, then the newest message, after recency and cooldown checks., Outreach selection uses a fixed clock and no external services., TestOutreachTarget

### Community 129 - "sidebar.py"
Cohesion: 0.20
Nodes (13): Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar, render_debug_controls() (+5 more)

### Community 136 - "MaslowNeed"
Cohesion: 0.07
Nodes (17): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy, Increase satisfaction by given amount, Test that satisfaction doesn't exceed 100 for regular needs (+9 more)

### Community 138 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 139 - "sprite_path"
Cohesion: 0.20
Nodes (6): icon_path(), Pixel sprite assets for the Jenbina UI. Only paths and constants live here;…, Path of the 96x48 sheet for ``state``; unknown states get the ``base`` sheet., Path of the 8x8 icon ``name`` (may not exist for unknown names)., sprite_path(), TestPaths

### Community 140 - "test_privacy.py"
Cohesion: 0.31
Nodes (4): CapturingLLM, Private conversation content must stay out of another person's prompts., TestNothingCrossesBetweenPeople, two_people()

### Community 141 - "test_heartbeat_host.py"
Cohesion: 0.17
Nodes (11): SQLite user database for authentication and conversation persistence., make_owner_id(), owner_is_dead(), _pid_namespace(), SQLite storage for the single being, separate from private account data., Identify the local PID namespace where the platform exposes it., Identify this host process and this particular attempt to host her., Only a missing PID in this machine's namespace proves an owner is dead. (+3 more)

### Community 143 - "build_timeline"
Cohesion: 0.10
Nodes (20): action_details_text(), build_timeline(), _event_row_html(), first_sentence(), _hhmm(), _marker_text(), _number(), _passes() (+12 more)

### Community 144 - "build_person"
Cohesion: 0.21
Nodes (7): BeingStateError, build_person(), Person, Construct the live being without any UI or process ownership concerns., Restore her state, fill missing systems, and bind the insight LLM., Saved person state could not be restored; never replace it silently., TestBuildPerson

### Community 145 - "stage_pill_html"
Cohesion: 0.25
Nodes (6): marker_html(), A centered time/place divider between timeline rows., The system stage pill in the status rail., stage_pill_html(), Show the system stage in the pill and remember it for reruns., TestMarkerAndPill

### Community 148 - "TestChainEdgeCases"
Cohesion: 0.22
Nodes (5): Test edge cases and boundary conditions for chains, Test chains with empty or minimal needs, Test chains with extreme need values, Test chains with very large world descriptions, TestChainEdgeCases

### Community 152 - "run_heartbeat.py"
Cohesion: 0.38
Nodes (4): build_host(), Build the shared storage and LLMs only when a host is requested., Standalone heartbeat CLI tests; no real LLMs or background threads., TestBuildHost

### Community 153 - ".suspend_until"
Cohesion: 0.40
Nodes (3): datetime, Decay needs, emotions, lessons and goals by elapsed real time., Move decay clocks past time when the heart was not running.

### Community 163 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 166 - "init_session_state"
Cohesion: 0.50
Nodes (4): init_session_state(), Persist the shared being through her owner., Initialize session resources; the host owns the live mind., save_person_state()

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls

## Knowledge Gaps
- **102 isolated node(s):** `Global Constraints`, `Review Focus`, `Task 1: Palette and compositor`, `Task 2: Body, hair, faces and the emotion states`, `Task 3: Props, effects and the action states` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **Why does `Person` connect `Person` to `choose_outreach_target`, `_make_mock_llm`, `CLAUDE.md Project Instructions`, `EnvironmentSimulator`, `SocialCognitionSystem`, `rail.py`, `test_privacy.py`, `InsightSystem`, `CuriositySystem`, `test_heartbeat_host.py`, `build_person`, `TestPerson`, `Deep Emotional Mirror Implementation Plan`, `TestChains`, `TestChainEdgeCases`, `SelfNarrativeSystem`, `TestPerPersonInsights`, `memory/__init__.py`, `LearningSystem`, `.suspend_until`, `GoalSystem`, `PlanningSystem`, `host.py`, `.add_conversation`, `TestMemoryIntegration`, `create_action_decision_chain`, `WorkingMemorySystem`, `MemoryIntegration`, `Plan`, `EmotionSystem`, `create_asimov_check_system`, `core/__init__.py`, `MaslowNeedsSystem`, `PersonModel`, `simulation_runner.py`, `SocialInteractionTracker`, `.deserialize`, `infer_emotional_tone`, `Conversation`, `test_simulation_runner.py`, `TestOwnership`, `StatusRail`, `adoption.py`, `ChatTurn`, `test_pixel_ui.py`, `app.py`?**
  _High betweenness centrality (0.235) - this node is a cross-community bridge._
- **Why does `Jenbina README` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `MetaCognitiveSystem`, `Person`, `EnvironmentSimulator`, `SocialCognitionSystem`, `Test Suite Workflow (push/manual)`, `InsightSystem`, `CuriositySystem`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `SelfNarrativeSystem`, `Test Suite README`, `get_llm`, `GoalSystem`, `create_action_decision_chain`, `EmotionSystem`, `create_asimov_check_system`, `MaslowNeedsSystem`, `simulation_runner.py`, `app.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `MaslowNeedsSystem` connect `MaslowNeedsSystem` to `GoalSystem`, `CLAUDE.md Project Instructions`, `needs/__init__.py`, `TestMaslowNeedsSystem`, `maslow_needs.py`, `.get_needs_summary`, `MaslowNeed`, `Person`, `simulation.py`, `.update_all_needs`, `WorkingMemorySystem`, `EnvironmentSimulator`, `create_action_decision_chain`, `Person`, `EmotionSystem`, `create_asimov_check_system`, `core/__init__.py`, `TestGrowthStageLadder`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `WorkingMemorySystem` (e.g. with `EmotionSystem` and `Goal`) actually correct?**
  _`WorkingMemorySystem` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `PlanningSystem` (e.g. with `TestPlanningSystem` and `TestPlanningSystemCreation`) actually correct?**
  _`PlanningSystem` has 7 INFERRED edges - model-reasoned connections that need verification._