# Graph Report - jenbina-virtual-world-c16b9b  (2026-11-17)

## Corpus Check
- 192 files · ~500,600 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3834 nodes · 8121 edges · 173 communities (147 shown, 26 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 481 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e567bb79`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_llm
- DynamicEventsSystem
- CLAUDE.md Project Instructions
- MaslowNeedsSystem
- MetaCognitiveSystem
- test_pixel_ui.py
- Person
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- .update_all_needs
- Design
- InsightSystem
- CuriositySystem
- Person
- TestPerson
- LearningSystem
- Deep Emotional Mirror Implementation Plan
- MinecraftWorld
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- HybridMemorySystem
- Test Suite README
- Background User Research -> Psychological Dossier
- WeatherData
- StreamCapture
- BeingStore
- get_llm
- PaloAltoLocationSystem
- chat_handler.py
- GoalSystem
- PlanningSystem
- host.py
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- create_action_decision_chain
- Experience
- WorkingMemorySystem
- actions.js
- UserDatabase
- Any
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- TestCheckInjectionBlock
- handle_chat_interaction
- test_maslow_needs.py
- Plan
- TestLesson
- EmotionSystem
- HostCase
- create_asimov_check_system
- MemoryEvent
- core/__init__.py
- TestUserCRUD
- WorkingMemoryItem
- JenbinaHost
- timeline.py
- person/person.py
- simulation_runner.py
- test_sprites.py
- _run_one_iteration
- test_user_db.py
- package.json
- FirebaseAuth
- Conversation
- create_basic_needs_chain
- Design
- TestConversation
- SocialInteractionTracker
- scene.py
- test_simulation.py
- File Structure
- .deserialize
- test_social_interaction_tracker.py
- Design
- Conversation
- test_working_memory.py
- TestRunnerInMinecraft
- make_move
- test_heartbeat_host.py
- observation
- TestTitles
- Emotion
- simulation.py
- .record_social_action
- streamlit_server
- Any
- SocialInteraction
- .store_memory
- StatusRail
- Review Focus
- fix_llm_json
- bridge.js
- generate_first_greeting
- adoption.py
- make_needs
- TestChains
- BasicNeeds
- test_minecraft_world.py
- MinecraftBridge
- Step
- .from_dict
- .fresh
- words.js
- test_timeline.py
- Design
- is_admin
- test_goal_system.py
- EventLog
- Jenbina Blob Character
- clear_chromadb.py
- main
- observe.js
- pixel_theme.py
- Blade Runner 2049 Theme Redesign
- TestFocusNoise
- TestLease
- shared_init.py
- TestContextSwitch
- File Structure
- .update
- .from_dict
- choose_outreach_target
- 3_🌍_Environment.py
- MaslowNeed
- TestAdoption
- TestBasicNeedsBackwardCompatibility
- TestBridgeClient
- test_privacy.py
- test_heartbeat_store.py
- TestUiExports
- build_timeline
- build_person
- stage_pill_html
- TestEvents
- TestPerform
- TestChainEdgeCases
- .generate_insight
- .analyze_cognitive_patterns
- hunt.test.js
- TestStateAndEvents
- TestPerPersonInsights
- TestHostLeavesTheWorld
- TestMessages
- LifeEventLog
- heartbeat/__init__.py
- auth_page.py
- run.test.js
- .add_note
- _StatusSink
- TestHomeScreen
- TestResolveAction
- .__init__
- .get_or_create_model
- TestSharedHost
- TestPersonState
- .from_dict
- parse_research_results
- TestMemoryIntegrationFactory
- run_server.sh
- setup_server.sh

## God Nodes (most connected - your core abstractions)
1. `Person` - 122 edges
2. `GoalSystem` - 81 edges
3. `WorkingMemorySystem` - 76 edges
4. `Person` - 66 edges
5. `PlanningSystem` - 65 edges
6. `InnerMonologueSystem` - 64 edges
7. `UserDatabase` - 62 edges
8. `MaslowNeedsSystem` - 59 edges
9. `JenbinaHost` - 50 edges
10. `CLAUDE.md Project Instructions` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Goal System Design` --semantically_similar_to--> `create_maslow_goal_setter()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-07-goal-system-design.md → core/needs/maslow_decision_chain.py
- `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)` --semantically_similar_to--> `run_single_iteration_headless()`  [INFERRED] [semantically similar]
  CURRENT_ARCHITECTURE_DIAGRAMS.md → core/simulation_runner.py
- `query_llm_knowledge() (planned function)` --semantically_similar_to--> `search_web()`  [INFERRED] [semantically similar]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md → core/research/user_research.py
- `LLM JSON Parsing via fix_llm_json` --conceptually_related_to--> `get_json_llm()`  [INFERRED]
  CLAUDE.md → core/connect.py
- `Goal System Design` --references--> `create_action_decision_chain()`  [INFERRED]
  docs/plans/2026-02-07-goal-system-design.md → core/cognition/action_decision_chain.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Deep Emotional Mirror feature flow (research -> dossier -> insights -> greetings -> chat)** — core_research_user_research_research_user, core_research_user_research_generate_user_dossier, core_social_social_cognition_personmodel, core_insights_insight_system_insightsystem, core_interaction_chat_handler_handle_chat_interaction, core_interaction_chat_handler_generate_first_greeting, core_interaction_chat_handler_generate_return_greeting, core_ui_chat_check_return_greeting, core_ui_shared_init_init_session_state, core_ui_shared_init_init_llm, core_interaction_guardrails_jenbina_system_prompt [EXTRACTED 1.00]
- **Jenbina Visual Identity (pink blob mascot, happy expression, Tamagotchi styling)** — assets_favicon, assets_favicon_jenbina_blob_character, assets_favicon_content_happy_expression, assets_favicon_tamagotchi_mascot_design [INFERRED 0.85]
- **Motivation-to-action stack injected into the action decision prompt (working memory, plan step, goals, lessons)** — core_working_memory_working_memory_system_workingmemorysystem, core_planning_planning_system_planningsystem, core_goals_goal_system_goalsystem, core_learning_learning_system_learningsystem, core_needs_maslow_needs_maslowneedssystem, core_cognition_action_decision_chain_create_action_decision_chain [INFERRED 0.85]

## Communities (173 total, 26 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "_make_mock_llm"
Cohesion: 0.07
Nodes (26): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+18 more)

### Community 2 - "DynamicEventsSystem"
Cohesion: 0.11
Nodes (14): DynamicEventsSystem, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API, Flexible system to fetch real-time events and venue information (+6 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.10
Nodes (45): .coveragerc coverage config, GitHub Actions Workflows README, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action) (+37 more)

### Community 4 - "MaslowNeedsSystem"
Cohesion: 0.08
Nodes (30): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+22 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.09
Nodes (20): create_meta_cognitive_action_chain(), Enhanced action decision with meta-cognitive monitoring, Cognition and Decision Making Submodule This submodule handles all aspects of…, CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, BaseLLM, Represents a single cognitive process/decision (+12 more)

### Community 6 - "test_pixel_ui.py"
Cohesion: 0.09
Nodes (25): Streamlit session_state Persistence, Redraw mood, place, doing/goal lines, needs bars and emotion chips., Render Maslow needs as thin bars; a need below 30% is marked critical., Render the strongest emotions (above 15, at most four) as text chips; the…, Render a badge with Jenbina's dominant mood, styled positive or negative., render_emotion_chips(), render_mood_indicator(), render_needs_bars() (+17 more)

### Community 7 - "Person"
Cohesion: 0.05
Nodes (23): Person, Any, datetime, Initialize self-narrative / identity system., Initialize the insight system with an LLM instance., Decay needs, emotions, lessons and goals by elapsed real time., Move decay clocks past time when the heart was not running., Get current needs as a flat dict (for learning system) (+15 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.11
Nodes (13): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Get local events based on Palo Alto location system, Get a natural language description of the current environment (+5 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.10
Nodes (12): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Tracks social models and chooses social strategy for conversations., Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy. (+4 more)

### Community 10 - "rail.py"
Cohesion: 0.16
Nodes (17): HeartStatus, _about_you_lines(), _card_title(), _goal_lines(), heartbeat_lines(), _lesson_lines(), _plan_lines(), datetime (+9 more)

### Community 11 - ".update_all_needs"
Cohesion: 0.29
Nodes (5): datetime, timedelta, Update all needs based on time passed, Update the current growth stage based on need satisfaction, Update need satisfaction over time

### Community 12 - "Design"
Cohesion: 0.05
Nodes (35): Actions, Anti-goals, Approaches, Code changes, Death, Design, Goals, How it works today (+27 more)

### Community 13 - "InsightSystem"
Cohesion: 0.18
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
Cohesion: 0.04
Nodes (39): LearningSystem, Lesson, Any, Records experiences, extracts lessons via LLM, and formats them for prompts., Decay all lessons and prune dead ones., A learned pattern extracted from experiences., make_mock_llm(), Test lesson reinforcement and contradiction (+31 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.15
Nodes (20): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, build_search_query(), generate_user_dossier(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,…, Build a web search query from user info. (+12 more)

### Community 19 - "MinecraftWorld"
Cohesion: 0.11
Nodes (21): Jenbina's Minecraft world: a real, persistent place she perceives and acts in.…, MinecraftWorld, Outcome, Any, datetime, The Minecraft world as the simulation runner sees it. A beat calls ``observe``…, Log in, look, log out. Raises ``WorldUnavailable`` if she cannot., Do what she chose and report what really happened. Never raises. (+13 more)

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.13
Nodes (8): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, TestSelfNarrativeSystem

### Community 22 - "generate_return_greeting"
Cohesion: 0.17
Nodes (10): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., Exception, _make_mock_llm(), _make_mock_person(), Create a minimal mock Person with all subsystems stubbed. (+2 more)

### Community 23 - "HybridMemorySystem"
Cohesion: 0.14
Nodes (18): ConversationMemory, Represents a conversation memory entry, HybridMemorySystem, LocationNode, PersonNode, OpenAI embeddings client, built lazily so an API key is only needed once…, Represents a person in the graph database, Represents a location in the graph database (+10 more)

### Community 24 - "Test Suite README"
Cohesion: 0.25
Nodes (8): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), Run a specific test module, run_specific_test(), Run all tests and provide comprehensive reporting, run_comprehensive_tests()

### Community 25 - "Background User Research -> Psychological Dossier"
Cohesion: 0.29
Nodes (11): .env.example template, Environment Variables (.env / .env.example), Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals (+3 more)

### Community 26 - "WeatherData"
Cohesion: 0.11
Nodes (10): Calculate how environment affects mood, TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator (+2 more)

### Community 27 - "StreamCapture"
Cohesion: 0.10
Nodes (11): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Jenbina — Console Log page., Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper. (+3 more)

### Community 28 - "BeingStore"
Cohesion: 0.14
Nodes (11): BeingStore, Lease, Connection, datetime, timedelta, Save only for the current lease holder when an owner is supplied., The newest events, oldest first, in UserDatabase.get_events format., Copy a user's event rows, keeping their timestamps and content. (+3 more)

### Community 29 - "get_llm"
Cohesion: 0.10
Nodes (18): get_json_llm(), get_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Use a finite positive timeout, falling back to sixty seconds., Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service…, timeout_from_env() (+10 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.08
Nodes (16): PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type, Get locations within a certain radius of current location (+8 more)

### Community 31 - "chat_handler.py"
Cohesion: 0.07
Nodes (25): Safety Constraints (Asimov check chain + guardrails), basic_needs_to_json(), _build_subsystem_context(), _chat_avatar(), create_metadata_from_person_state(), history_context(), ``section[key]`` for the nested world-summary shape, the value itself for a…, ``(recent_actions, world_context)`` read from the records the runners append to… (+17 more)

### Community 32 - "GoalSystem"
Cohesion: 0.09
Nodes (16): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals), Goal Horizons (short / mid / long-term) (+8 more)

### Community 33 - "PlanningSystem"
Cohesion: 0.08
Nodes (16): PlanningSystem, Any, Decomposes goals into plans and tracks execution across cycles., make_experience(), make_mock_llm(), make_plan(), Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete. (+8 more)

### Community 34 - "host.py"
Cohesion: 0.16
Nodes (17): Own the single live mind, its process lease, and its continuous rhythm., beats_today(), effective_interval(), _elapsed(), is_night(), lost_time(), next_beat_at(), datetime (+9 more)

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
Cohesion: 0.09
Nodes (20): callable, create_action_decision_chain(), _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, _make_mock_llm() (+12 more)

### Community 39 - "Experience"
Cohesion: 0.09
Nodes (14): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set (+6 more)

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.12
Nodes (8): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestFormatting, TestSalienceScoring

### Community 41 - "actions.js"
Cohesion: 0.17
Nodes (32): {
  ANIMALS, CRAFT_WHITELIST, FOODS, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
}, carried(), count(), craft(), craftOnce(), { DIRECTIONS, bestTool }, done(), drink() (+24 more)

### Community 42 - "UserDatabase"
Cohesion: 0.09
Nodes (16): Connection, datetime, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first. (+8 more)

### Community 43 - "Any"
Cohesion: 0.11
Nodes (12): example_usage(), Any, Person, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person…, Get recent memories within a time window Args: hours: Number of hours to look…, Get trends in needs satisfaction over time Args: need_name: Optional specific… (+4 more)

### Community 45 - "TestEmotionSystem"
Cohesion: 0.08
Nodes (13): Test EmotionSystem functionality, Should initialize with 8 Plutchik emotions, Check Jenbina's character baselines, Initially, intensity should equal base_intensity, Should spike the named emotion, Triggering unknown emotion should be a no-op, Should apply multiple adjustments at once, Should return top-k emotions by intensity (+5 more)

### Community 47 - "Goal"
Cohesion: 0.12
Nodes (6): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing.

### Community 48 - "ChromaMemoryManager"
Cohesion: 0.06
Nodes (28): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+20 more)

### Community 49 - "TestCheckInjectionBlock"
Cohesion: 0.06
Nodes (17): build_system_message(), check_injection(), make_refusal_response(), In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn), Return the system prompt, optionally with a warning addendum., Tests for core/interaction/guardrails.py — prompt injection detection., Normal messages should return (False, False). (+9 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.24
Nodes (5): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "test_maslow_needs.py"
Cohesion: 0.09
Nodes (14): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Test the legacy Need class, Test legacy Need initialization (+6 more)

### Community 52 - "Plan"
Cohesion: 0.07
Nodes (19): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None. (+11 more)

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.14
Nodes (9): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}., Get the top-k emotions by intensity. (+1 more)

### Community 55 - "HostCase"
Cohesion: 0.11
Nodes (4): HostCase, TestLostTime, TestSleep, TestTurnsAndStepOnce

### Community 56 - "create_asimov_check_system"
Cohesion: 0.10
Nodes (16): _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead., create_state_analysis_system(), Any, BaseLLM (+8 more)

### Community 57 - "MemoryEvent"
Cohesion: 0.07
Nodes (22): MemoryEvent, Represents a memory event with all its components, Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval (+14 more)

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
Nodes (5): JenbinaHost, datetime, timedelta, Stop the heart, save her and release the lease. With ``patience`` (seconds) it…, Log her out of a real world; a described world has nothing to leave.

### Community 62 - "timeline.py"
Cohesion: 0.12
Nodes (19): action_icon(), delta_badge_html(), event_html(), The icon name for an action's row, by keyword; the star when none fits., One timeline row for a life event: a kind tag, the title, then badge and meta.…, The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests., action_details_text(), _event_row_html() (+11 more)

### Community 64 - "simulation_runner.py"
Cohesion: 0.07
Nodes (32): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, _check_proactive_triggers(), credit_completed_plan(), _detect_location_from_action(), get_person_dict(), _print_json(), Headless simulation runner — no Streamlit dependency. Provides… (+24 more)

### Community 65 - "test_sprites.py"
Cohesion: 0.05
Nodes (41): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, check(), compose(), _file_matches(), frame_layers(), main() (+33 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "test_user_db.py"
Cohesion: 0.08
Nodes (9): Test UserDatabase initialisation and table creation., Messages from one user should not leak to another., get_all_users_with_message_counts splits by message_type, not sender., Same-second writes must be deterministic by id tiebreaker., TestAdminMessageCounts, TestIsolation, TestListPersonStates, TestMessageOrdering (+1 more)

### Community 68 - "package.json"
Cohesion: 0.08
Nodes (24): canvas, dependencies, mineflayer, mineflayer-collectblock, mineflayer-pathfinder, vec3, description, engines (+16 more)

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "create_basic_needs_chain"
Cohesion: 0.09
Nodes (22): create_basic_needs_chain(), Legacy function for backward compatibility - now uses Maslow decision system, Chain Tests README, main(), Main function to run tests, Run all chain tests and return results, Run a specific test by name, run_chain_tests() (+14 more)

### Community 72 - "Design"
Cohesion: 0.11
Nodes (18): 10. Code changes, 1. Pages, 2. Shell, 3. Left column: the timeline, 4. The event log, 5. Right column: the status rail, 6. The runner, 7. Bug fixes in scope (+10 more)

### Community 73 - "TestConversation"
Cohesion: 0.13
Nodes (8): Test Conversation functionality, Test conversation initialization, Test adding messages to conversation, Test adding message with specific type, Test getting recent messages, Test getting messages by type, Test that last_interaction updates when adding messages, TestConversation

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.18
Nodes (9): Initialize social interaction tracker., Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today., How many distinct people Jenbina interacted with today., Produce a first-person summary Jenbina can use to describe her social day.…, Short context block suitable for injection into LLM prompts. ``names=False``…, Tracks all of Jenbina's social interactions during the session. Only the…, SocialInteractionTracker (+1 more)

### Community 75 - "scene.py"
Cohesion: 0.15
Nodes (22): _article(), available_actions(), best_food(), build_world_state(), celsius(), _craft_label(), describe(), distance_from_home() (+14 more)

### Community 76 - "test_simulation.py"
Cohesion: 0.20
Nodes (9): fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the home screen loads with the timeline and heartbeat card., Click 'Step once' and verify the rail and the timeline fill in., sim_page() (+1 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - ".deserialize"
Cohesion: 0.17
Nodes (5): Reconstruct a Person from a JSON string. Args: json_str: JSON produced by…, Test from_dict(to_dict()) preserves data, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization

### Community 79 - "test_social_interaction_tracker.py"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Conversation"
Cohesion: 0.06
Nodes (21): Person Management Submodule This submodule handles the AI's person…, Conversation, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation (+13 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "TestRunnerInMinecraft"
Cohesion: 0.06
Nodes (16): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, The real runner with every LLM chain mocked and a fake bridge for a world., TestRunnerInMinecraft, build_env(), HeadlessFixture, _plan_fixture(), A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a… (+8 more)

### Community 85 - "test_heartbeat_host.py"
Cohesion: 0.07
Nodes (6): process_host(), The one host of this process, built on first use. Kept on ``sys`` rather than…, The host owns one live mind; its clock, runner and database are local fakes., TestBeats, TestOwnership, TestUnreadableState

### Community 86 - "observation"
Cohesion: 0.21
Nodes (7): build_scene(), place_label(), ``Home`` near her home position, otherwise the biome in plain words., labels(), observation(), TestAvailableActions, TestPlaceAndScene

### Community 87 - "TestTitles"
Cohesion: 0.14
Nodes (7): lessons_text(), mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, Lessons as one line: lists joined with '; ', strings as they are., ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 88 - "Emotion"
Cohesion: 0.18
Nodes (6): Emotion, datetime, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "simulation.py"
Cohesion: 0.09
Nodes (21): inject_pixel_css(), nav_icon_css(), portrait_caption_html(), The name strip under the rail portrait., Inject the theme. Call once per page, right after ``st.set_page_config``.…, CSS that puts Jenbina's face before the first sidebar link, or "" when the file…, _css_token(), display_jenbina_image() (+13 more)

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

### Community 94 - ".store_memory"
Cohesion: 0.20
Nodes (5): Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID, Store event in ChromaDB for semantic search, Store event relationships in Neo4j, Store event in SQLite for chronological tracking

### Community 95 - "StatusRail"
Cohesion: 0.10
Nodes (9): env_line_html(), NullRail, Append a row to the timeline's live slot (a thought or action in progress)., A rail that draws nothing: headless runs and tests., ``Jenbina's House · Night · Clear skies, 15°C``; the bare home name when there…, Handles on the Now card's placeholders, plus the timeline's live slot., StatusRail, TestTimelineAndRail (+1 more)

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "fix_llm_json"
Cohesion: 0.17
Nodes (9): LLM JSON Parsing via fix_llm_json, fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function. (+1 more)

### Community 98 - "bridge.js"
Cohesion: 0.17
Nodes (21): act(), { ACTIONS, stopMoving }, BRIDGE_PORT, BridgeError, connected(), endSession(), http, { inventoryCounts, observe } (+13 more)

### Community 99 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 100 - "adoption.py"
Cohesion: 0.15
Nodes (16): adopt_existing(), AdoptionReport, choose_user_to_adopt(), _experience_count(), _import_partner(), datetime, Person, Adopt one existing mind and retain each account's own relationship with her. (+8 more)

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "TestChains"
Cohesion: 0.09
Nodes (15): Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), run_simulation(), create_world_description_system(), BaseLLM, Creates and returns a function that generates world descriptions. Args: llm:…, Test the Maslow decision chain, Test cases for all chain functions in the Jenbina system, Test error handling in chains (+7 more)

### Community 103 - "BasicNeeds"
Cohesion: 0.07
Nodes (18): BasicNeeds, Any, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+10 more)

### Community 104 - "test_minecraft_world.py"
Cohesion: 0.12
Nodes (7): The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world., world_from_env(), FakeBridge, ProviderCase, Records every call; answers with whatever the test sets., TestObserve, TestWorldFromEnv

### Community 105 - "MinecraftBridge"
Cohesion: 0.16
Nodes (10): MinecraftBridge, Any, RuntimeError, HTTP client for the Node bridge that is Jenbina's body in Minecraft. The bridge…, The Minecraft world cannot be reached or did not answer usefully., Log her in if needed and return the observation., Log her out. Never raises: leaving must not break a beat., Run one bounded routine and return its outcome. (+2 more)

### Community 106 - "Step"
Cohesion: 0.26
Nodes (7): decide(), Choose one action without mutating the situation or consulting the clock., Step, asleep(), awake(), TestAsleep, TestAwake

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 108 - ".fresh"
Cohesion: 0.23
Nodes (3): Restore valid fields independently; old or malformed fields default., TestSituation, TestSavedWorldMemory

### Community 109 - "words.js"
Cohesion: 0.18
Nodes (16): { inventoryDiff, outcomeSummary }, OVERRUN, runRoutine(), assert, {
  DIRECTIONS, bestTool, hasSameOrBetterTool, inventoryDiff, itemPhrase, itemsPhrase, outcomeSummary
}, test, DIRECTIONS, hasSameOrBetterTool() (+8 more)

### Community 110 - "test_timeline.py"
Cohesion: 0.19
Nodes (25): format_duration(), make_action(), make_gap(), make_goal(), make_mood(), make_plan(), make_sleep(), make_thought() (+17 more)

### Community 111 - "Design"
Cohesion: 0.10
Nodes (19): 1. One owner, 2. One record, 3. The rhythm, 4. Sleep, 5. Lost time, 6. Chat, 7. Many people, one Jenbina, 8. The home screen (+11 more)

### Community 112 - "is_admin"
Cohesion: 0.19
Nodes (12): Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, _hostname(), is_admin(), is_local_request(), The shared admin access check for the Admin page and heartbeat card., ``localhost`` from ``localhost:8501`` or ``http://localhost:8501``., Whether the request names this machine as its host. The Host and Origin headers…, Return True if the current visitor is allowed to see the admin panel. With… (+4 more)

### Community 113 - "test_goal_system.py"
Cohesion: 0.17
Nodes (6): make_experience(), Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemIntegration, TestGoalSystemMilestone, TestGoalSystemProgress

### Community 114 - "EventLog"
Cohesion: 0.14
Nodes (14): ChatTurn, EventLog, Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., handle_user_input(), Handle one submitted chat message and return the chat result, or ``None`` when…, patch (+6 more)

### Community 115 - "Jenbina Blob Character"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "clear_chromadb.py"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 117 - "main"
Cohesion: 0.15
Nodes (6): build_host(), main(), Build the shared storage and LLMs only when a host is requested., Standalone heartbeat CLI tests; no real LLMs or background threads., TestBuildHost, TestHeartbeatMain

### Community 118 - "observe.js"
Cohesion: 0.22
Nodes (14): ANIMALS, biomeAt(), blockIds(), CRAFT_WHITELIST, craftable(), FOODS, { hasSameOrBetterTool }, HOSTILES (+6 more)

### Community 119 - "pixel_theme.py"
Cohesion: 0.11
Nodes (16): _data_uri(), dialog_html(), icon_html(), The UI theme: the page CSS and the HTML helpers for timeline rows, markers, the…, Base64 data URI of a committed asset, cached for the process lifetime. Assets…, The animated sprite for ``state`` with an optional caption. ``scale`` 4 is the…, An inline 16x16 pixel icon, or an empty span when the icon does not exist. Only…, An RPG dialog box around escaped ``body`` text (newlines become ``<br>``). (+8 more)

### Community 120 - "Blade Runner 2049 Theme Redesign"
Cohesion: 0.12
Nodes (16): 1. Palette, 2. Type, 3. Shell, 4. Timeline, 5. Status rail, 6. Code changes, 7. Sidebar and tab icon, Anti-goals (what would make this a failure even if it works) (+8 more)

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 122 - "TestLease"
Cohesion: 0.13
Nodes (3): StoreTestCase, TestLease, TestPeople

### Community 123 - "shared_init.py"
Cohesion: 0.07
Nodes (45): _latest_world(), main(), Jenbina's home screen: a private conversation beside her shared live state., World and chosen action from the host's most recent moment. The world summary…, NotHostingError, RuntimeError, She is not (or no longer) living in this process., Jenbina — Debug Info page. (+37 more)

### Community 125 - "File Structure"
Cohesion: 0.11
Nodes (17): Changes made after the tasks, from review, Decisions this plan makes inside the spec's "left to the builder", File Structure, Global Constraints, Heartbeat Implementation Plan, Review Focus, Task 10: End-to-end tests, docs, final check, Task 1: Storage for the being (+9 more)

### Community 126 - ".update"
Cohesion: 0.24
Nodes (3): Any, Buffer capacity based on focus: 3 (exhausted) to 7 (rested)., Recalculate working memory from current state. Called once per cycle.

### Community 128 - "choose_outreach_target"
Cohesion: 0.20
Nodes (6): choose_outreach_target(), datetime, Choose one recent conversation partner for a proactive message., Prefer closeness, then the newest message, after recency and cooldown checks., Outreach selection uses a fixed clock and no external services., TestOutreachTarget

### Community 129 - "3_🌍_Environment.py"
Cohesion: 0.21
Nodes (14): Jenbina — Environment & Debug page., Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar (+6 more)

### Community 136 - "MaslowNeed"
Cohesion: 0.06
Nodes (19): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Initialize all needs in Maslow's hierarchy, Initialize all needs across all five levels, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy (+11 more)

### Community 138 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 140 - "test_privacy.py"
Cohesion: 0.31
Nodes (4): CapturingLLM, Private conversation content must stay out of another person's prompts., TestNothingCrossesBetweenPeople, two_people()

### Community 141 - "test_heartbeat_store.py"
Cohesion: 0.19
Nodes (10): SQLite user database for authentication and conversation persistence., make_owner_id(), owner_is_dead(), _pid_namespace(), SQLite storage for the single being, separate from private account data., Identify the local PID namespace where the platform exposes it., Identify this host process and this particular attempt to host her., Only a missing PID in this machine's namespace proves an owner is dead. (+2 more)

### Community 143 - "build_timeline"
Cohesion: 0.13
Nodes (9): build_timeline(), first_sentence(), Render the rows in order; an empty list shows the empty-state marker., ``(first sentence, remainder)``; the whole text and ``""`` when it has no…, Merge chat messages and life events by time, apply the filter, keep the newest…, render_timeline(), TestBuildTimeline, TestCorruptRows (+1 more)

### Community 144 - "build_person"
Cohesion: 0.21
Nodes (7): BeingStateError, build_person(), Person, Construct the live being without any UI or process ownership concerns., Restore her state, fill missing systems, and bind the insight LLM., Saved person state could not be restored; never replace it silently., TestBuildPerson

### Community 145 - "stage_pill_html"
Cohesion: 0.25
Nodes (6): marker_html(), A centered time/place divider between timeline rows., The system stage pill in the status rail., stage_pill_html(), Show the system stage in the pill and remember it for reruns., TestMarkerAndPill

### Community 148 - "TestChainEdgeCases"
Cohesion: 0.22
Nodes (5): Test edge cases and boundary conditions for chains, Test chains with empty or minimal needs, Test chains with extreme need values, Test chains with very large world descriptions, TestChainEdgeCases

### Community 149 - ".generate_insight"
Cohesion: 0.20
Nodes (6): Any, Check if conditions are met to generate a subtle insight.…, Generate a subtle perceptive observation about the user. Returns the insight…, Check if we should fire the bold first-impression insight., Generate a bold, striking first-impression observation. Returns the insight…, date

### Community 150 - ".analyze_cognitive_patterns"
Cohesion: 0.29
Nodes (4): Any, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights, Get statistics about meta-cognitive performance

### Community 151 - "hunt.test.js"
Cohesion: 0.20
Nodes (6): ACTIONS, { ACTIONS }, assert, { EventEmitter }, test, { Vec3 }

### Community 158 - "auth_page.py"
Cohesion: 0.25
Nodes (7): _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only., Return path to Google credentials file. Locally, reads…, Return the OAuth redirect URI. Uses the ``REDIRECT_URI`` env var if set…, Return a shared UserDatabase instance via session state.

### Community 159 - "run.test.js"
Cohesion: 0.29
Nodes (6): assert, deps(), { DIED, runRoutine }, { EventEmitter }, options(), test

### Community 164 - ".__init__"
Cohesion: 0.29
Nodes (3): Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data

### Community 165 - ".get_or_create_model"
Cohesion: 0.38
Nodes (3): Choose when to be nice, polite, or assertive., Predict likely reaction from relationship + inferred emotional state., Build a concise ToM context block for LLM prompting.

### Community 169 - "parse_research_results"
Cohesion: 0.47
Nodes (3): parse_research_results(), Extract useful text snippets from search results., TestParseResearchResults

### Community 170 - "TestMemoryIntegrationFactory"
Cohesion: 0.33
Nodes (4): Test memory integration factory functions, Test creating memory integration with default settings, Test creating memory integration with custom paths, TestMemoryIntegrationFactory

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls

## Knowledge Gaps
- **182 isolated node(s):** `{ goals }`, `{ Vec3 }`, `{ DIRECTIONS, bestTool }`, `{
  ANIMALS, CRAFT_WHITELIST, FOODS, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
}`, `FILLERS` (+177 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **Why does `Person` connect `Person` to `choose_outreach_target`, `_make_mock_llm`, `CLAUDE.md Project Instructions`, `MaslowNeedsSystem`, `MetaCognitiveSystem`, `test_pixel_ui.py`, `SocialCognitionSystem`, `rail.py`, `test_privacy.py`, `InsightSystem`, `CuriositySystem`, `build_person`, `TestPerson`, `Deep Emotional Mirror Implementation Plan`, `TestChainEdgeCases`, `HybridMemorySystem`, `TestPerPersonInsights`, `GoalSystem`, `PlanningSystem`, `host.py`, `create_action_decision_chain`, `Experience`, `WorkingMemorySystem`, `Any`, `Plan`, `EmotionSystem`, `core/__init__.py`, `person/person.py`, `simulation_runner.py`, `create_basic_needs_chain`, `SocialInteractionTracker`, `.deserialize`, `test_social_interaction_tracker.py`, `Conversation`, `TestRunnerInMinecraft`, `test_heartbeat_host.py`, `observation`, `adoption.py`, `TestChains`, `test_minecraft_world.py`, `EventLog`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `Person` connect `Person` to `choose_outreach_target`, `_make_mock_llm`, `MaslowNeedsSystem`, `test_pixel_ui.py`, `Person`, `SocialCognitionSystem`, `rail.py`, `test_privacy.py`, `CuriositySystem`, `build_person`, `TestPerson`, `TestChainEdgeCases`, `TestPerPersonInsights`, `TestMemoryIntegration`, `create_action_decision_chain`, `Experience`, `HostCase`, `JenbinaHost`, `Conversation`, `create_basic_needs_chain`, `Conversation`, `TestRunnerInMinecraft`, `test_heartbeat_host.py`, `observation`, `adoption.py`, `TestChains`, `test_minecraft_world.py`, `EventLog`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `MaslowNeedsSystem` connect `MaslowNeedsSystem` to `GoalSystem`, `CLAUDE.md Project Instructions`, `MetaCognitiveSystem`, `test_pixel_ui.py`, `BasicNeeds`, `MaslowNeed`, `Person`, `WorkingMemorySystem`, `.update_all_needs`, `TestMaslowNeedsSystem`, `Person`, `test_maslow_needs.py`, `EmotionSystem`, `HybridMemorySystem`, `core/__init__.py`, `person/person.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `WorkingMemorySystem` (e.g. with `EmotionSystem` and `Goal`) actually correct?**
  _`WorkingMemorySystem` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Person` (e.g. with `run_simulation()` and `adopt_existing()`) actually correct?**
  _`Person` has 39 INFERRED edges - model-reasoned connections that need verification._