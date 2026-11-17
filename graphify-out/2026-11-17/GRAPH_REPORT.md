# Graph Report - jenbina-virtual-world-c16b9b  (2026-11-17)

## Corpus Check
- 192 files · ~502,231 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3869 nodes · 8196 edges · 185 communities (160 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f1c4bbf1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_llm
- Event
- CLAUDE.md Project Instructions
- timeline.py
- MetaCognitiveSystem
- Lesson
- Person
- .get_dynamic_recommendations
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
- TestChains
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)
- Test Suite README
- Inner Life Surfacing via Prompt Engineering
- world_state.py
- StreamCapture
- BeingStore
- get_llm
- PaloAltoLocationSystem
- chat_handler.py
- GoalSystem
- PlanningSystem
- host.py
- TestEmotion
- MemoryIntegration
- TestMaslowNeedsSystem
- core/__init__.py
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
- guardrails.py
- handle_chat_interaction
- Need
- test_planning_system.py
- TestLesson
- EmotionSystem
- .advance
- simulation_runner.py
- MemoryEvent
- MinecraftWorld
- TestUserCRUD
- WorkingMemoryItem
- JenbinaHost
- test_user_db.py
- make_mock_llm
- TestCheckInjectionBlock
- check
- test_feedback_loop.py
- make_plan
- package.json
- FirebaseAuth
- Conversation
- create_basic_needs_chain
- Design
- TestConversation
- SocialInteractionTracker
- scene.py
- Tamagotchi UI Implementation Plan
- File Structure
- TestLearningSystemSerialization
- test_social_interaction_tracker.py
- Design
- Conversation
- test_working_memory.py
- test_simulation_runner.py
- EventLog
- TestOwnership
- observation
- TestTitles
- Emotion
- TestLearningSystemDecay
- .record_social_action
- .create_plan
- HybridMemorySystem
- SocialInteraction
- MaslowNeedsSystem
- StatusRail
- Review Focus
- test_timeline.py
- bridge.js
- generate_first_greeting
- adoption.py
- make_needs
- app.py
- .get_needs_summary
- test_pixel_ui.py
- MinecraftBridge
- Step
- .from_dict
- render_frame
- words.js
- timeline/__init__.py
- Design
- is_admin
- test_goal_system.py
- ChatTurn
- Jenbina Blob Character
- clear_chromadb.py
- main
- observe.js
- inject_pixel_css
- Blade Runner 2049 Theme Redesign
- TestFocusNoise
- TestLearningSystemStats
- shared_init.py
- TestContextSwitch
- File Structure
- .update
- .from_dict
- choose_outreach_target
- 3_🌍_Environment.py
- MaslowNeed
- TestAdoption
- test_minecraft_world.py
- art.py
- test_privacy.py
- test_heartbeat_store.py
- TestUiExports
- build_timeline
- pixel_theme.py
- build.py
- TestEvents
- TestPerform
- fix_llm_json
- TestRunnerInMinecraft
- needs/__init__.py
- hunt.test.js
- simulation.py
- .suspend_until
- TestBasicNeedsBackwardCompatibility
- render_sheet
- TestPromptTemplates
- heartbeat/__init__.py
- render_icon
- run.test.js
- .add_note
- _MindLockRelease
- .from_dict
- TestResolveAction
- .from_dict
- build_person
- TimelineEvent
- TestBridgeClient
- TestBeats
- test_sprites.py
- SimpleEmbeddings
- run_server.sh
- setup_server.sh
- maslow_needs.py
- .fresh
- compose
- streamlit_server
- match_action_key
- TestTalkingDuringAMoment
- .add_conversation
- TestIsolation
- TestGoalSystemFormatting
- TestGrowthStageLadder
- Planning System Design
- .get_planning_stats

## God Nodes (most connected - your core abstractions)
1. `Person` - 122 edges
2. `GoalSystem` - 81 edges
3. `WorkingMemorySystem` - 76 edges
4. `Person` - 66 edges
5. `PlanningSystem` - 65 edges
6. `InnerMonologueSystem` - 64 edges
7. `UserDatabase` - 62 edges
8. `MaslowNeedsSystem` - 59 edges
9. `JenbinaHost` - 53 edges
10. `Step` - 50 edges

## Surprising Connections (you probably didn't know these)
- `create_maslow_goal_setter()` --semantically_similar_to--> `Goal System Design`  [INFERRED] [semantically similar]
  core/needs/maslow_decision_chain.py → docs/plans/2026-02-07-goal-system-design.md
- `search_web()` --semantically_similar_to--> `query_llm_knowledge() (planned function)`  [INFERRED] [semantically similar]
  core/research/user_research.py → docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md
- `run_single_iteration_headless()` --semantically_similar_to--> `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)`  [INFERRED] [semantically similar]
  core/simulation_runner.py → CURRENT_ARCHITECTURE_DIAGRAMS.md
- `create_action_decision_chain()` --references--> `Goal System Design`  [INFERRED]
  core/cognition/action_decision_chain.py → docs/plans/2026-02-07-goal-system-design.md
- `create_action_decision_chain()` --references--> `Planning System Design`  [INFERRED]
  core/cognition/action_decision_chain.py → docs/plans/2026-02-07-planning-system-design.md

## Import Cycles
- None detected.

## Communities (185 total, 25 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "_make_mock_llm"
Cohesion: 0.06
Nodes (26): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+18 more)

### Community 2 - "Event"
Cohesion: 0.11
Nodes (13): Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API, Fetch venues from Google Places API (+5 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.11
Nodes (45): .coveragerc coverage config, GitHub Actions Workflows README, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action) (+37 more)

### Community 4 - "timeline.py"
Cohesion: 0.12
Nodes (19): action_icon(), delta_badge_html(), event_html(), The icon name for an action's row, by keyword; the star when none fits., One timeline row for a life event: a kind tag, the title, then badge and meta.…, The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests., action_details_text(), _event_row_html() (+11 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.09
Nodes (16): CognitiveProcess, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights, Get statistics about meta-cognitive performance (+8 more)

### Community 6 - "Lesson"
Cohesion: 0.12
Nodes (9): Lesson, A learned pattern extracted from experiences., Test format_lessons_for_prompt, No lessons should return default message, Active lessons should appear in formatted text, Lessons should be sorted by confidence descending, Inactive lessons should not appear, Should show at most 10 lessons (+1 more)

### Community 7 - "Person"
Cohesion: 0.06
Nodes (19): Person, Any, Initialize curiosity / exploration system., Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system), Get a summary of conversation with a specific outsider, Get overall communication statistics, Return a first-person narrative of Jenbina's social day. (+11 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Tracks social models and chooses social strategy for conversations., Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy. (+7 more)

### Community 10 - "rail.py"
Cohesion: 0.14
Nodes (21): HeartStatus, UI components for Jenbina Streamlit app., _about_you_lines(), _card_title(), _goal_lines(), heartbeat_lines(), _lesson_lines(), _plan_lines() (+13 more)

### Community 11 - ".update_all_needs"
Cohesion: 0.29
Nodes (5): datetime, timedelta, Update all needs based on time passed, Update the current growth stage based on need satisfaction, Update need satisfaction over time

### Community 12 - "Design"
Cohesion: 0.05
Nodes (35): Actions, Anti-goals, Approaches, Code changes, Death, Design, Goals, How it works today (+27 more)

### Community 13 - "InsightSystem"
Cohesion: 0.09
Nodes (14): InsightSystem, Any, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Check if conditions are met to generate a subtle insight.…, Generate a subtle perceptive observation about the user. Returns the insight…, Generates deep perceptive observations about users mid-conversation., Check if we should fire the bold first-impression insight., Generate a bold, striking first-impression observation. Returns the insight… (+6 more)

### Community 14 - "CuriositySystem"
Cohesion: 0.11
Nodes (8): CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., TestCuriositySystem, TestPersonCuriositySerialization

### Community 15 - "Person"
Cohesion: 0.09
Nodes (11): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+3 more)

### Community 16 - "TestPerson"
Cohesion: 0.05
Nodes (19): Test Person functionality, Test person initialization, Test person with default name, Test updating all needs, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider (+11 more)

### Community 17 - "LearningSystem"
Cohesion: 0.09
Nodes (19): LearningSystem, Any, Records experiences, extracts lessons via LLM, and formats them for prompts., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Decay all lessons and prune dead ones., make_mock_llm(), Test LLM-based lesson extraction (+11 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.13
Nodes (23): build_search_query(), generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,…, Build a web search query from user info., Call the SerpAPI web search API (serpapi.com). Returns raw JSON response from… (+15 more)

### Community 19 - "TestChains"
Cohesion: 0.07
Nodes (19): BasicNeeds, Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Add a new need to the system, Remove a need from the system (+11 more)

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.15
Nodes (9): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., Exception, _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateProactiveMessage (+1 more)

### Community 23 - "Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)"
Cohesion: 0.29
Nodes (8): ConversationMemory, Represents a conversation memory entry, LocationNode, PersonNode, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)

### Community 24 - "Test Suite README"
Cohesion: 0.15
Nodes (14): Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), Test Suite README, Mock LLM invoke Pattern, Isolated Test Environment (temp dirs, mocked Neo4j), main(), Main function to run tests, Run all chain tests and return results, Run a specific test by name (+6 more)

### Community 25 - "Inner Life Surfacing via Prompt Engineering"
Cohesion: 0.33
Nodes (9): .env.example template, Environment Variables (.env / .env.example), Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals (+1 more)

### Community 26 - "world_state.py"
Cohesion: 0.05
Nodes (42): DynamicEventsSystem, Flexible system to fetch real-time events and venue information, EnvironmentSimulator, EnvironmentState, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state (+34 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "BeingStore"
Cohesion: 0.07
Nodes (14): BeingStore, Lease, Connection, datetime, timedelta, Save only for the current lease holder when an owner is supplied., The newest events, oldest first, in UserDatabase.get_events format., Copy a user's event rows, keeping their timestamps and content. (+6 more)

### Community 29 - "get_llm"
Cohesion: 0.10
Nodes (19): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Use a finite positive timeout, falling back to sixty seconds., Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service… (+11 more)

### Community 30 - "PaloAltoLocationSystem"
Cohesion: 0.10
Nodes (17): Location, PaloAltoLocationSystem, any, datetime, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name, Get all locations of a specific type (+9 more)

### Community 31 - "chat_handler.py"
Cohesion: 0.08
Nodes (21): basic_needs_to_json(), _build_subsystem_context(), _chat_avatar(), create_metadata_from_person_state(), history_context(), ``section[key]`` for the nested world-summary shape, the value itself for a…, ``(recent_actions, world_context)`` read from the records the runners append to…, Convert BasicNeeds object to JSON-serializable format (+13 more)

### Community 32 - "GoalSystem"
Cohesion: 0.11
Nodes (7): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., TestGoalSystem, TestGoalSystemGeneration

### Community 33 - "PlanningSystem"
Cohesion: 0.14
Nodes (9): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., make_experience(), make_mock_llm(), Test: create plan → execute steps → complete., TestPlanningSystem, TestPlanningSystemCreation, TestPlanningSystemEvaluation (+1 more)

### Community 34 - "host.py"
Cohesion: 0.13
Nodes (19): Own the single live mind, its process lease, and its continuous rhythm., Ask the heart for a moment now, without waiting for it. The heart takes it on…, _StatusSink, beats_today(), effective_interval(), _elapsed(), is_night(), lost_time() (+11 more)

### Community 35 - "TestEmotion"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "MemoryIntegration"
Cohesion: 0.05
Nodes (26): create_memory_integration(), MemoryIntegration, Memory Integration Module Shows how to integrate the hybrid memory system with…, Integrates the hybrid memory system with Jenbina's existing components, Create a memory integration instance with default settings Returns:…, Test storing action memory, Test storing action memory with people and location, Test storing need change memory (+18 more)

### Community 37 - "TestMaslowNeedsSystem"
Cohesion: 0.07
Nodes (15): Test the complete Maslow needs system, Test system initialization with all needs, Test updating all needs over time, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs (+7 more)

### Community 38 - "core/__init__.py"
Cohesion: 0.08
Nodes (27): callable, create_action_decision_chain(), _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, create_meta_cognitive_action_chain() (+19 more)

### Community 39 - "Experience"
Cohesion: 0.11
Nodes (12): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set, Test that world_context defaults to empty dict, Test Experience dataclass (+4 more)

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
Cohesion: 0.08
Nodes (18): Connection, datetime, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first. (+10 more)

### Community 43 - "Any"
Cohesion: 0.11
Nodes (12): example_usage(), Any, Person, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person…, Get recent memories within a time window Args: hours: Number of hours to look…, Get trends in needs satisfaction over time Args: need_name: Optional specific… (+4 more)

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

### Community 49 - "guardrails.py"
Cohesion: 0.11
Nodes (17): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+9 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "Need"
Cohesion: 0.09
Nodes (13): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Legacy needs property that maps to Maslow needs, Test the legacy Need class (+5 more)

### Community 52 - "test_planning_system.py"
Cohesion: 0.15
Nodes (8): PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., make_step(), Tests for the planning system., Test: create plan → get stuck → replan → complete., TestPlanningSystemIntegration, TestPlanStep

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.14
Nodes (9): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}., Get the top-k emotions by intensity. (+1 more)

### Community 55 - ".advance"
Cohesion: 0.11
Nodes (4): HostCase, TestLostTime, TestSleep, TestTurnsAndStepOnce

### Community 56 - "simulation_runner.py"
Cohesion: 0.07
Nodes (37): _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead., create_state_analysis_system(), Any, BaseLLM (+29 more)

### Community 57 - "MemoryEvent"
Cohesion: 0.07
Nodes (21): MemoryEvent, Represents a memory event with all its components, Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval (+13 more)

### Community 58 - "MinecraftWorld"
Cohesion: 0.11
Nodes (21): HTTP client for the Node bridge that is Jenbina's body in Minecraft. The bridge…, Jenbina's Minecraft world: a real, persistent place she perceives and acts in.…, MinecraftWorld, Outcome, Any, datetime, The Minecraft world as the simulation runner sees it. A beat calls ``observe``…, Log in, look, log out. Raises ``WorldUnavailable`` if she cannot. ``waiting``… (+13 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.24
Nodes (4): Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "JenbinaHost"
Cohesion: 0.15
Nodes (7): JenbinaHost, datetime, timedelta, Attach the lock-releasing callback to an LLM the beats use., Stop the heart, save her and release the lease. With ``patience`` (seconds) it…, Log her out of a real world; a described world has nothing to leave., Consume a pending request; True when the beat should run now.

### Community 62 - "test_user_db.py"
Cohesion: 0.06
Nodes (9): Test conversation message storage and retrieval., Test UserDatabase initialisation and table creation., Test person state save/load., get_all_users_with_message_counts splits by message_type, not sender., TestAdminMessageCounts, TestListPersonStates, TestMessages, TestPersonState (+1 more)

### Community 63 - "make_mock_llm"
Cohesion: 0.30
Nodes (4): make_experience(), make_mock_llm(), TestGoalSystemMilestone, TestGoalSystemProgress

### Community 64 - "TestCheckInjectionBlock"
Cohesion: 0.11
Nodes (4): Tier 1 BLOCK patterns should return (True, *)., Tier 2 WARN patterns should return (False, True)., TestCheckInjectionBlock, TestCheckInjectionWarn

### Community 65 - "check"
Cohesion: 0.29
Nodes (9): check(), main(), Every output image, keyed by path relative to ``assets/sprites``., Write every sheet, the avatar and the icons under ``out_dir``. When ``favicon``…, Relative paths under ``out_dir`` (plus the favicon) that are missing, differ…, render_all(), write_all(), Path (+1 more)

### Community 66 - "test_feedback_loop.py"
Cohesion: 0.17
Nodes (14): skip, fixture, Page, Playwright E2E test — verify the simulation feedback loop: 1. Actions affect…, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page… (+6 more)

### Community 67 - "make_plan"
Cohesion: 0.16
Nodes (5): Plan, An ordered sequence of steps to achieve a goal., make_plan(), TestPlan, TestPlanningSystemReplan

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
Cohesion: 0.07
Nodes (20): create_basic_needs_chain(), Legacy function for backward compatibility - now uses Maslow decision system, Chain Tests README, Test meta-cognitive system integration with chains, Test error recovery and graceful degradation in chains, Test chain performance with multiple rapid calls, Test chains with different person states, Test integration scenarios between different chains (+12 more)

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
Cohesion: 0.14
Nodes (23): _article(), available_actions(), best_food(), build_world_state(), celsius(), _craft_label(), describe(), distance_from_home() (+15 more)

### Community 76 - "Tamagotchi UI Implementation Plan"
Cohesion: 0.14
Nodes (14): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Streamlit session_state Persistence, Superpowers executing-plans Workflow, Tamagotchi UI Implementation Plan, Streamlit (web UI), fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and… (+6 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - "TestLearningSystemSerialization"
Cohesion: 0.18
Nodes (6): Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 79 - "test_social_interaction_tracker.py"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Conversation"
Cohesion: 0.07
Nodes (20): Person Management Submodule This submodule handles the AI's person…, Conversation, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation (+12 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "test_simulation_runner.py"
Cohesion: 0.10
Nodes (10): build_env(), HeadlessFixture, _plan_fixture(), A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a…, Two plans: one finished earlier, one whose last step completes this iteration;…, TestHeadlessParity, TestHeadlessProactive, TestHeadlessRunnerEvents (+2 more)

### Community 84 - "EventLog"
Cohesion: 0.16
Nodes (9): EventLog, make_goal(), make_move(), Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, A move, only when the location actually changed., Goal events for what changed between two snapshots: advanced or completed goals…, record_goal_changes(), record_move() (+1 more)

### Community 86 - "observation"
Cohesion: 0.21
Nodes (7): build_scene(), place_label(), ``Home`` near her home position, otherwise the biome in plain words., labels(), observation(), TestAvailableActions, TestPlaceAndScene

### Community 87 - "TestTitles"
Cohesion: 0.19
Nodes (6): make_action(), mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 88 - "Emotion"
Cohesion: 0.18
Nodes (6): Emotion, datetime, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "TestLearningSystemDecay"
Cohesion: 0.18
Nodes (6): Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, TestLearningSystemDecay

### Community 90 - ".record_social_action"
Cohesion: 0.25
Nodes (4): Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Generate a simple automatic sentiment string., Try to extract a person/entity name from a simulated action string. The action…

### Community 91 - ".create_plan"
Cohesion: 0.11
Nodes (8): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id., Mark current step completed and move to next.

### Community 92 - "HybridMemorySystem"
Cohesion: 0.07
Nodes (21): HybridMemorySystem, Any, datetime, OpenAI embeddings client, built lazily so an API key is only needed once…, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object… (+13 more)

### Community 93 - "SocialInteraction"
Cohesion: 0.29
Nodes (4): Any, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, TestSocialInteraction

### Community 94 - "MaslowNeedsSystem"
Cohesion: 0.09
Nodes (12): MaslowNeedsSystem, Complete Maslow's hierarchy of needs system, Initialize all needs in Maslow's hierarchy, Initialize all needs across all five levels, Satisfy a specific need, Get satisfaction level for a specific need, Calculate weighted overall satisfaction across all levels, Get list of needs that are critically low, prioritized by level (+4 more)

### Community 95 - "StatusRail"
Cohesion: 0.09
Nodes (10): env_line_html(), NullRail, Append a row to the timeline's live slot (a thought or action in progress)., A rail that draws nothing: headless runs and tests., ``Jenbina's House · Night · Clear skies, 15°C``; the bare home name when there…, Handles on the Now card's placeholders, plus the timeline's live slot., Show the system stage in the pill and remember it for reruns., StatusRail (+2 more)

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "test_timeline.py"
Cohesion: 0.12
Nodes (18): make_mood(), make_plan(), Recording helpers: turn runner state into timeline events. Both…, A replanned goal with its new first step., The current inner thought, or ``None`` when there is none., The chosen action with its reasoning, lessons and world context., A mood shift, or ``None`` when nothing moved by a full point., ``{description: (status, progress)}`` for every goal, ``{}`` without a system. (+10 more)

### Community 98 - "bridge.js"
Cohesion: 0.17
Nodes (21): act(), { ACTIONS, stopMoving }, BRIDGE_PORT, BridgeError, connected(), endSession(), http, { inventoryCounts, observe } (+13 more)

### Community 99 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 100 - "adoption.py"
Cohesion: 0.16
Nodes (16): adopt_existing(), AdoptionReport, choose_user_to_adopt(), _experience_count(), _import_partner(), datetime, Person, Adopt one existing mind and retain each account's own relationship with her. (+8 more)

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "app.py"
Cohesion: 0.12
Nodes (20): _latest_world(), main(), Jenbina's home screen: a private conversation beside her shared live state., World and chosen action from the host's most recent moment. The world summary…, check_return_greeting(), ensure_greeting(), datetime, Chat UI components for Jenbina app (+12 more)

### Community 103 - ".get_needs_summary"
Cohesion: 0.12
Nodes (10): Any, Get average satisfaction for a specific level, Get the most urgent needs to address, Get insights about personal growth and development, Get human-readable name for growth stage, Get a comprehensive summary of all needs, String representation of the needs system, Convert to dictionary for serialization (+2 more)

### Community 104 - "test_pixel_ui.py"
Cohesion: 0.08
Nodes (25): marker_html(), A centered time/place divider between timeline rows., Redraw mood, place, doing/goal lines, needs bars and emotion chips., Render Maslow needs as thin bars; a need below 30% is marked critical., Render the strongest emotions (above 15, at most four) as text chips; the…, Render a badge with Jenbina's dominant mood, styled positive or negative., render_emotion_chips(), render_mood_indicator() (+17 more)

### Community 105 - "MinecraftBridge"
Cohesion: 0.25
Nodes (6): MinecraftBridge, Any, Log her in if needed and return the observation., Log her out. Never raises: leaving must not break a beat., Run one bounded routine and return its outcome., HTTPError

### Community 106 - "Step"
Cohesion: 0.26
Nodes (7): decide(), Choose one action without mutating the situation or consulting the clock., Step, asleep(), awake(), TestAsleep, TestAwake

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 108 - "render_frame"
Cohesion: 0.25
Nodes (6): frame_layers(), FrameSpec, Body, hair, face, props, effects — in drawing order., render_frame(), Layer, TestActionSheets

### Community 109 - "words.js"
Cohesion: 0.18
Nodes (16): { inventoryDiff, outcomeSummary }, OVERRUN, runRoutine(), assert, {
  DIRECTIONS, bestTool, hasSameOrBetterTool, inventoryDiff, itemPhrase, itemsPhrase, outcomeSummary
}, test, DIRECTIONS, hasSameOrBetterTool() (+8 more)

### Community 110 - "timeline/__init__.py"
Cohesion: 0.25
Nodes (10): format_duration(), lessons_text(), make_gap(), make_sleep(), make_wake(), timedelta, The vocabulary of Jenbina's life events, their one-line titles, and the…, Whole elapsed minutes, with hours when needed and no negative time. (+2 more)

### Community 111 - "Design"
Cohesion: 0.10
Nodes (19): 1. One owner, 2. One record, 3. The rhythm, 4. Sleep, 5. Lost time, 6. Chat, 7. Many people, one Jenbina, 8. The home screen (+11 more)

### Community 112 - "is_admin"
Cohesion: 0.19
Nodes (12): Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, _hostname(), is_admin(), is_local_request(), The shared admin access check for the Admin page and heartbeat card., ``localhost`` from ``localhost:8501`` or ``http://localhost:8501``., Whether the request names this machine as its host. The Host and Origin headers…, Return True if the current visitor is allowed to see the admin panel. With… (+4 more)

### Community 113 - "test_goal_system.py"
Cohesion: 0.22
Nodes (4): Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemIntegration, TestGoalSystemStats

### Community 114 - "ChatTurn"
Cohesion: 0.08
Nodes (21): ChatTurn, NotHostingError, RuntimeError, She is not (or no longer) living in this process., _get_user_db_and_id(), _get_user_display_name(), handle_user_input(), Return the authenticated user's display name, or 'User' as fallback. (+13 more)

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

### Community 119 - "inject_pixel_css"
Cohesion: 0.14
Nodes (12): inject_pixel_css(), nav_icon_css(), Inject the theme. Call once per page, right after ``st.set_page_config``.…, CSS that puts Jenbina's face before the first sidebar link, or "" when the file…, display_jenbina_image(), Show the painterly portrait for the state named by ``image_path``, unaltered in…, patch, TestChatHandlerAvatars (+4 more)

### Community 120 - "Blade Runner 2049 Theme Redesign"
Cohesion: 0.12
Nodes (16): 1. Palette, 2. Type, 3. Shell, 4. Timeline, 5. Status rail, 6. Code changes, 7. Sidebar and tab icon, Anti-goals (what would make this a failure even if it works) (+8 more)

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 122 - "TestLearningSystemStats"
Cohesion: 0.22
Nodes (5): Test get_learning_stats, Empty system should return zero counts, Stats should reflect recorded data, recent_experiences should show at most 5, TestLearningSystemStats

### Community 123 - "shared_init.py"
Cohesion: 0.09
Nodes (30): SQLite user database for authentication and conversation persistence., process_host(), The one host of this process, built on first use. Kept on ``sys`` rather than…, Jenbina — Debug Info page., _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only. (+22 more)

### Community 125 - "File Structure"
Cohesion: 0.11
Nodes (17): Changes made after the tasks, from review, Decisions this plan makes inside the spec's "left to the builder", File Structure, Global Constraints, Heartbeat Implementation Plan, Review Focus, Task 10: End-to-end tests, docs, final check, Task 1: Storage for the being (+9 more)

### Community 126 - ".update"
Cohesion: 0.24
Nodes (3): Any, Buffer capacity based on focus: 3 (exhausted) to 7 (rested)., Recalculate working memory from current state. Called once per cycle.

### Community 128 - "choose_outreach_target"
Cohesion: 0.21
Nodes (6): choose_outreach_target(), datetime, Choose one recent conversation partner for a proactive message., Prefer closeness, then the newest message, after recency and cooldown checks., Outreach selection uses a fixed clock and no external services., TestOutreachTarget

### Community 129 - "3_🌍_Environment.py"
Cohesion: 0.21
Nodes (14): Jenbina — Environment & Debug page., Sidebar UI components for Jenbina app, Render environment info as a full-width section (formerly sidebar), Render location exploration section in sidebar, Render dynamic events and venues section, Render the environment information in the sidebar, Render location recommendations section, Render debug controls in sidebar (+6 more)

### Community 136 - "MaslowNeed"
Cohesion: 0.07
Nodes (16): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Represents a single need in Maslow's hierarchy, Increase satisfaction by given amount, Test that satisfaction doesn't exceed 100 for regular needs, Test that self-actualization needs can grow beyond 100 (+8 more)

### Community 138 - "test_minecraft_world.py"
Cohesion: 0.10
Nodes (10): RuntimeError, The Minecraft world cannot be reached or did not answer usefully., WorldUnavailable, The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world., world_from_env(), FakeBridge, ProviderCase, Records every call; answers with whatever the test sets. (+2 more)

### Community 139 - "art.py"
Cohesion: 0.14
Nodes (8): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, Pixel sprite assets for the Jenbina UI. Only paths and constants live here;…, Path of the 96x48 sheet for ``state``; unknown states get the ``base`` sheet., sprite_path(), Palette for the pixel art. One character per color in the art strings. This…, TestPaths

### Community 140 - "test_privacy.py"
Cohesion: 0.31
Nodes (4): CapturingLLM, Private conversation content must stay out of another person's prompts., TestNothingCrossesBetweenPeople, two_people()

### Community 141 - "test_heartbeat_store.py"
Cohesion: 0.14
Nodes (10): make_owner_id(), owner_is_dead(), _pid_namespace(), SQLite storage for the single being, separate from private account data., Identify the local PID namespace where the platform exposes it., Identify this host process and this particular attempt to host her., Only a missing PID in this machine's namespace proves an owner is dead., Storage for the single being, independent of accounts and Streamlit. (+2 more)

### Community 143 - "build_timeline"
Cohesion: 0.14
Nodes (9): make_thought(), build_timeline(), first_sentence(), Render the rows in order; an empty list shows the empty-state marker., ``(first sentence, remainder)``; the whole text and ``""`` when it has no…, Merge chat messages and life events by time, apply the filter, keep the newest…, render_timeline(), TestBuildTimeline (+1 more)

### Community 144 - "pixel_theme.py"
Cohesion: 0.12
Nodes (14): Jenbina — Console Log page., _data_uri(), dialog_html(), icon_html(), The UI theme: the page CSS and the HTML helpers for timeline rows, markers, the…, Base64 data URI of a committed asset, cached for the process lifetime. Assets…, The animated sprite for ``state`` with an optional caption. ``scale`` 4 is the…, An inline 16x16 pixel icon, or an empty span when the icon does not exist. Only… (+6 more)

### Community 145 - "build.py"
Cohesion: 0.36
Nodes (6): _file_matches(), _pixels(), png_bytes(), Pillow compositor and build CLI for the pixel sprites. Run ``python -m…, PNG encoding with fixed settings and no timestamps. Bytes are stable for one…, Image

### Community 147 - "TestPerform"
Cohesion: 0.10
Nodes (3): She is never left standing in a running world while asleep or stopped., TestHostLeavesTheWorld, TestPerform

### Community 148 - "fix_llm_json"
Cohesion: 0.15
Nodes (10): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility. (+2 more)

### Community 150 - "needs/__init__.py"
Cohesion: 0.20
Nodes (14): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+6 more)

### Community 151 - "hunt.test.js"
Cohesion: 0.20
Nodes (6): ACTIONS, { ACTIONS }, assert, { EventEmitter }, test, { Vec3 }

### Community 152 - "simulation.py"
Cohesion: 0.15
Nodes (13): portrait_caption_html(), The name strip under the rail portrait., _css_token(), _get_image_path(), get_jenbina_image_for_action(), get_jenbina_image_for_emotion(), _portrait_path(), Portrait and state renderers for Jenbina's UI. (+5 more)

### Community 153 - ".suspend_until"
Cohesion: 0.40
Nodes (3): datetime, Decay needs, emotions, lessons and goals by elapsed real time., Move decay clocks past time when the heart was not running.

### Community 154 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 155 - "render_sheet"
Cohesion: 0.43
Nodes (3): The 96x48 two-frame sheet for ``state``; unknown state raises KeyError., render_sheet(), TestEmotionSheets

### Community 158 - "render_icon"
Cohesion: 0.40
Nodes (3): One 8x8 icon; unknown name raises KeyError., render_icon(), TestIcons

### Community 159 - "run.test.js"
Cohesion: 0.29
Nodes (6): assert, deps(), { DIED, runRoutine }, { EventEmitter }, options(), test

### Community 161 - "_MindLockRelease"
Cohesion: 0.21
Nodes (4): BaseCallbackHandler, _MindLockRelease, For the beat's own waits that are not a single LLM call on its thread, such as…, Lets go of the mind lock while a beat only waits for an LLM. A moment of her…

### Community 165 - "build_person"
Cohesion: 0.23
Nodes (7): BeingStateError, build_person(), Person, Construct the live being without any UI or process ownership concerns., Restore her state, fill missing systems, and bind the insight LLM., Saved person state could not be restored; never replace it silently., TestBuildPerson

### Community 166 - "TimelineEvent"
Cohesion: 0.15
Nodes (6): LifeEventLog, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., Her shared life stream, persisted without a per-account owner., One entry of Jenbina's day. ``title`` is the line the timeline shows., TimelineEvent

### Community 169 - "test_sprites.py"
Cohesion: 0.18
Nodes (6): all_layers(), Tests for the pixel sprite pipeline (core.ui.sprites)., TestArtLayers, TestPalette, TestPortraits, TestTimelineIcons

### Community 170 - "SimpleEmbeddings"
Cohesion: 0.20
Nodes (6): Initialize or load the Chroma vector store, Simple hash-based embeddings for when OpenAI is not available, Generate a simple hash-based embedding, Embed multiple documents, Initialize Chroma-based memory manager Args: embeddings_provider: Which…, SimpleEmbeddings

### Community 173 - "maslow_needs.py"
Cohesion: 0.29
Nodes (7): NeedCategory, NeedLevel, Enum, Maslow's hierarchy levels, Categories within each need level, Add a new need to the system, Create from dictionary

### Community 175 - "compose"
Cohesion: 0.36
Nodes (3): compose(), Draw ``layers`` in order onto a transparent RGBA canvas. A ``"."`` pixel leaves…, TestCompose

### Community 176 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 177 - "match_action_key"
Cohesion: 0.36
Nodes (3): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, TestActionKeywordMatch

### Community 179 - ".add_conversation"
Cohesion: 0.33
Nodes (3): Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider

### Community 183 - "Planning System Design"
Cohesion: 0.67
Nodes (3): Planning System Design, Multi-step Chain-of-Thought Planning, Plan Step Completion Detection & Replan Trigger

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls

## Knowledge Gaps
- **182 isolated node(s):** `{ goals }`, `{ Vec3 }`, `{ DIRECTIONS, bestTool }`, `{
  ANIMALS, CRAFT_WHITELIST, FOODS, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
}`, `FILLERS` (+177 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **Why does `Person` connect `Person` to `choose_outreach_target`, `_make_mock_llm`, `CLAUDE.md Project Instructions`, `SocialCognitionSystem`, `test_minecraft_world.py`, `rail.py`, `test_privacy.py`, `InsightSystem`, `CuriositySystem`, `TestPerson`, `Deep Emotional Mirror Implementation Plan`, `TestChains`, `SelfNarrativeSystem`, `Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)`, `.suspend_until`, `world_state.py`, `GoalSystem`, `PlanningSystem`, `host.py`, `MemoryIntegration`, `build_person`, `core/__init__.py`, `Experience`, `WorkingMemorySystem`, `Any`, `Goal`, `.add_conversation`, `EmotionSystem`, `Planning System Design`, `simulation_runner.py`, `create_basic_needs_chain`, `SocialInteractionTracker`, `test_social_interaction_tracker.py`, `Conversation`, `test_simulation_runner.py`, `TestOwnership`, `observation`, `MaslowNeedsSystem`, `adoption.py`, `app.py`, `test_pixel_ui.py`, `ChatTurn`, `shared_init.py`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **Why does `MaslowNeedsSystem` connect `MaslowNeedsSystem` to `GoalSystem`, `CLAUDE.md Project Instructions`, `TestMaslowNeedsSystem`, `core/__init__.py`, `.get_needs_summary`, `Person`, `test_pixel_ui.py`, `WorkingMemorySystem`, `.update_all_needs`, `maslow_needs.py`, `Goal`, `Person`, `needs/__init__.py`, `Entity-Relationship Model (Person / Needs / Memory / Environment / Cognition)`, `simulation_runner.py`, `EmotionSystem`, `TestGrowthStageLadder`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `CLAUDE.md Project Instructions` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `app.py`, `shared_init.py`, `Tamagotchi UI Implementation Plan`, `maslow_needs.py`, `ChromaMemoryManager`, `guardrails.py`, `Deep Emotional Mirror Implementation Plan`, `clear_chromadb.py`, `fix_llm_json`, `needs/__init__.py`, `Test Suite README`, `simulation_runner.py`, `Inner Life Surfacing via Prompt Engineering`, `StreamCapture`, `HybridMemorySystem`, `get_llm`, `MaslowNeedsSystem`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `WorkingMemorySystem` (e.g. with `Experience` and `MaslowNeedsSystem`) actually correct?**
  _`WorkingMemorySystem` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Person` (e.g. with `run_simulation()` and `adopt_existing()`) actually correct?**
  _`Person` has 39 INFERRED edges - model-reasoned connections that need verification._