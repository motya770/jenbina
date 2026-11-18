# Graph Report - objective-shirley  (2026-11-18)

## Corpus Check
- 213 files · ~534,224 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4327 nodes · 9120 edges · 206 communities (177 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 534 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8587ce46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_llm
- WorldLauncher
- CLAUDE.md Project Instructions
- TestChains
- MetaCognitiveSystem
- .ready
- Conversation
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- .update_all_needs
- Design
- InsightSystem
- voice_prompt
- Person
- TestPerson
- LearningSystem
- CuriositySystem
- TestTalk
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- core/__init__.py
- make_mock_llm
- say.test.js
- world_state.py
- StreamCapture
- BeingStore
- get_llm
- PaloAltoLocationSystem
- chat_handler.py
- GoalSystem
- PlanningSystem
- test_minecraft_world.py
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- _invoke_and_parse
- Experience
- WorkingMemorySystem
- done
- UserDatabase
- MemoryIntegration
- TestSocialInteractionTracker
- TestEmotionSystem
- make_goal
- Goal
- ChromaMemoryManager
- guardrails.py
- handle_chat_interaction
- test_chains.py
- test_planning_system.py
- TestLesson
- EmotionSystem
- HostCase
- create_action_decision_chain
- TestHybridMemorySystem
- MinecraftWorld
- TestUserCRUD
- WorkingMemoryItem
- JenbinaHost
- File Structure
- simulation_runner.py
- scene.py
- build.py
- _run_one_iteration
- Inhabitants: someone to talk to in her Minecraft world
- bridge/package.json
- FirebaseAuth
- Conversation
- Deep Emotional Mirror Implementation Plan
- Design
- test_live.py
- SocialInteractionTracker
- test_minecraft_inhabitants.py
- test_simulation.py
- File Structure
- WeatherData
- TestRunnerInMinecraft
- Design
- Person
- test_working_memory.py
- test_simulation_runner.py
- Jenbina's Minecraft world
- TestOwnership
- build_scene
- recording.py
- Emotion
- The design
- Lesson
- Minecraft world: Jenbina lives in a real place
- HybridMemorySystem
- fix_llm_json
- MaslowNeedsSystem
- user_db.py
- Review Focus
- EventLog
- bridge.js
- generate_first_greeting
- adoption.py
- make_needs
- test_user_db.py
- TestBeatWithCompany
- test_pixel_ui.py
- stage_pill_html
- Step
- .from_dict
- render_frame
- words.js
- make_plan
- Design
- is_admin
- WorldUnavailable
- chat.py
- Jenbina Blob Character
- clear_chromadb.py
- main
- actions.js
- PersonModel
- Blade Runner 2049 Theme Redesign
- TestFocusNoise
- players.test.js
- shared_init.py
- TestHearingAcrossBeats
- File Structure
- .update
- .from_dict
- choose_outreach_target
- Any
- MaslowNeed
- TestAdoption
- observation
- art.py
- test_privacy.py
- store.py
- TestUiExports
- build_timeline
- pixel_theme.py
- session.test.js
- TestEvents
- TestPerform
- TestCheckInjectionBlock
- TimelineEvent
- Deploying Jenbina to Railway
- hunt.test.js
- TestLearningSystemDecay
- .create_plan
- Need
- render_sheet
- TestHostLeavesTheWorld
- heartbeat/__init__.py
- test_timeline.py
- run.test.js
- .add_note
- .waiting
- TestCheckInjectionWarn
- TestResolveAction
- build_person
- TestChainRealWorldScenarios
- MinecraftBridge
- _format_current_events
- test_sprites.py
- TestLearningSystemStats
- run_server.sh
- setup_server.sh
- .voice
- .fresh
- compose
- streamlit_server
- .generate_insight
- TestBridgeClient
- TestLearningSystemSerialization
- setup_inhabitants.sh
- make_experience
- .get_current_step
- world_from_env
- test_goal_system.py
- TestPerPersonInsights
- TestMessages
- test_heartbeat_store.py
- match_action_key
- FakeEmotions
- within.test.js
- .get_or_create_model
- .from_dict
- render_icon
- build_search_query
- Inner Life Surfacing via Prompt Engineering
- TestMemoryIntegrationFactory
- .test_full_plan_lifecycle
- TestGoalSystemFormatting
- .test_handles_search_failure
- TestContextSwitch
- .from_dict
- dependencies
- Planning System Design
- _format_weather_details
- railway.ts

## God Nodes (most connected - your core abstractions)
1. `Person` - 125 edges
2. `GoalSystem` - 81 edges
3. `WorkingMemorySystem` - 76 edges
4. `Person` - 67 edges
5. `PlanningSystem` - 65 edges
6. `InnerMonologueSystem` - 64 edges
7. `UserDatabase` - 62 edges
8. `MaslowNeedsSystem` - 59 edges
9. `JenbinaHost` - 57 edges
10. `Step` - 53 edges

## Surprising Connections (you probably didn't know these)
- `create_maslow_goal_setter()` --semantically_similar_to--> `Goal System Design`  [INFERRED] [semantically similar]
  core/needs/maslow_decision_chain.py → docs/plans/2026-02-07-goal-system-design.md
- `run_single_iteration_headless()` --semantically_similar_to--> `app.py Simulation Data Flow (6-step button-click pipeline + chat flow)`  [INFERRED] [semantically similar]
  core/simulation_runner.py → CURRENT_ARCHITECTURE_DIAGRAMS.md
- `search_web()` --semantically_similar_to--> `query_llm_knowledge() (planned function)`  [INFERRED] [semantically similar]
  core/research/user_research.py → docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md
- `create_action_decision_chain()` --references--> `Goal System Design`  [INFERRED]
  core/cognition/action_decision_chain.py → docs/plans/2026-02-07-goal-system-design.md
- `create_action_decision_chain()` --references--> `Planning System Design`  [INFERRED]
  core/cognition/action_decision_chain.py → docs/plans/2026-02-07-planning-system-design.md

## Import Cycles
- None detected.

## Communities (206 total, 29 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (38): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+30 more)

### Community 1 - "_make_mock_llm"
Cohesion: 0.06
Nodes (26): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+18 more)

### Community 2 - "WorldLauncher"
Cohesion: 0.08
Nodes (21): is_local(), port_open(), Path, Start and stop the processes her Minecraft world needs. Besides her mind, the…, The port the server listens on: ``MC_PORT``, else ``server.properties``., Owns the server, bridge and inhabitants processes this process started., Start whichever of the server and the bridge is not running. Returns as soon as…, Start what is missing and wait until the world can be joined. Costs two quick… (+13 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.11
Nodes (43): .env.example template, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, CLAUDE.md Project Instructions, Code Conventions (PascalCase classes, snake_case funcs, dataclasses, LangChain chains, factory functions, type hints), Environment Variables (.env / .env.example), Layered Architecture (UI -> Interaction -> Cognition -> Core -> DB -> LLM) (+35 more)

### Community 4 - "TestChains"
Cohesion: 0.05
Nodes (24): BasicNeeds, Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem, Update all needs (decrease satisfaction over time), Satisfy a specific need, Get satisfaction level for a specific need, Calculate overall satisfaction percentage across all needs, Get list of needs that are critically low, Get list of needs that are low (+16 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.08
Nodes (20): CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes, Suggest thinking strategies based on meta-cognitive insights (+12 more)

### Community 6 - ".ready"
Cohesion: 0.05
Nodes (14): inhabitant_settings(), Mindcraft's settings for her world, passed to it as ``SETTINGS_JSON``.…, FakeBridge, FakeProcess, InhabitantsCase, LauncherCase, A world that is up, with Mindcraft set up beside it., The real watcher thread, ticking fast, against fake processes. (+6 more)

### Community 7 - "Conversation"
Cohesion: 0.07
Nodes (19): Conversation, Message, Represents a single message in a conversation, Get conversation history with a specific outsider, Get all conversations, Represents a conversation with a specific outsider, Add a new message to the conversation, Reconstruct a Person from a JSON string. Args: json_str: JSON produced by… (+11 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.11
Nodes (14): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Calculate how environment affects mood, Get local events based on Palo Alto location system (+6 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.13
Nodes (7): Initialize social cognition / theory-of-mind system., Tracks social models and chooses social strategy for conversations., Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy., SocialCognitionSystem, TestPersonSocialSerialization, TestSocialCognitionSystem

### Community 10 - "rail.py"
Cohesion: 0.07
Nodes (32): HeartStatus, _about_you_lines(), _card_title(), env_line_html(), _goal_lines(), heartbeat_lines(), _lesson_lines(), NullRail (+24 more)

### Community 11 - ".update_all_needs"
Cohesion: 0.29
Nodes (5): datetime, timedelta, Update all needs based on time passed, Update the current growth stage based on need satisfaction, Update need satisfaction over time

### Community 12 - "Design"
Cohesion: 0.12
Nodes (17): Actions, Code changes, Death, Design, Leaving the world safely, Needs the world owns, Observation, One beat in Minecraft (+9 more)

### Community 13 - "InsightSystem"
Cohesion: 0.19
Nodes (6): InsightSystem, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Generates deep perceptive observations about users mid-conversation., _make_mock_llm(), dict, TestInsightSystem

### Community 14 - "voice_prompt"
Cohesion: 0.20
Nodes (5): The whole prompt for her next line to ``partner``. ``last_lines`` are the last…, voice_prompt(), Answers only what the voice may read; anything else fails the test., StrictPerson, TestVoicePrompt

### Community 15 - "Person"
Cohesion: 0.09
Nodes (11): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+3 more)

### Community 16 - "TestPerson"
Cohesion: 0.05
Nodes (19): Test Person functionality, Test person initialization, Test person with default name, Test updating all needs, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider (+11 more)

### Community 17 - "LearningSystem"
Cohesion: 0.10
Nodes (17): LearningSystem, Any, Records experiences, extracts lessons via LLM, and formats them for prompts., Decay all lessons and prune dead ones., make_mock_llm(), Test LLM-based lesson extraction, Test that valid LLM JSON response creates lessons, Should extract at most 3 lessons (+9 more)

### Community 18 - "CuriositySystem"
Cohesion: 0.10
Nodes (9): CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking…, Tracks curiosity, boredom, novelty, and exploration opportunities., Update curiosity state from current world and repetition patterns., Initialize curiosity / exploration system., TestCuriositySystem (+1 more)

### Community 19 - "TestTalk"
Cohesion: 0.15
Nodes (5): chatty_voice(), A voice that says ``lines`` in turn, each ``(text, end)``, then falls silent., scripted_voice(), TalkCase, TestTalk

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.11
Nodes (10): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Person Management Submodule This submodule handles the AI's person… (+2 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.17
Nodes (10): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., Exception, _make_mock_llm(), _make_mock_person(), Create a minimal mock Person with all subsystems stubbed. (+2 more)

### Community 23 - "core/__init__.py"
Cohesion: 0.13
Nodes (18): Jenbina AGI System - Core Module This is the main core module for the Jenbina…, ConversationMemory, Represents a conversation memory entry, LocationNode, MemoryEvent, PersonNode, Represents a memory event with all its components, Represents a person in the graph database (+10 more)

### Community 24 - "make_mock_llm"
Cohesion: 0.30
Nodes (4): make_experience(), make_mock_llm(), TestGoalSystemMilestone, TestGoalSystemProgress

### Community 25 - "say.test.js"
Cohesion: 0.12
Nodes (11): createHearing(), assert, { createHearing }, test, { ACTIONS }, assert, { cleanLine, sayAndListen }, { createHearing } (+3 more)

### Community 26 - "world_state.py"
Cohesion: 0.07
Nodes (34): DynamicEventsSystem, Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API (+26 more)

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
Nodes (8): PlanningSystem, Any, Decomposes goals into plans and tracks execution across cycles., make_mock_llm(), TestPlanningSystem, TestPlanningSystemCreation, TestPlanningSystemReplan, TestPlanningSystemStats

### Community 34 - "test_minecraft_world.py"
Cohesion: 0.10
Nodes (22): process_host(), Own the single live mind, its process lease, and its continuous rhythm., The one host of this process, built on first use. Kept on ``sys`` rather than…, beats_today(), effective_interval(), _elapsed(), is_night(), lost_time() (+14 more)

### Community 35 - "TestEmotion"
Cohesion: 0.07
Nodes (14): Test individual Emotion functionality, Intensity above baseline should decay downward, Intensity below baseline should rise toward it, Decay should not go below baseline when coming from above, Recovery should not go above baseline when coming from below, No time passed should leave intensity unchanged, Negative hours should leave intensity unchanged, At baseline, decay should have no effect (+6 more)

### Community 36 - "TestMemoryIntegration"
Cohesion: 0.06
Nodes (17): Test storing action memory, Test storing action memory with people and location, Test storing need change memory, Test storing need change memory with current needs state, Test MemoryIntegration functionality, Test getting relevant context for a query, Test getting context for a specific person, Test getting recent memories (+9 more)

### Community 37 - "TestMaslowNeedsSystem"
Cohesion: 0.07
Nodes (15): Test the complete Maslow needs system, Test system initialization with all needs, Test updating all needs over time, Test satisfying a specific need, Test getting average satisfaction for a level, Test overall satisfaction calculation, Test getting critical needs, Test getting low needs (+7 more)

### Community 38 - "_invoke_and_parse"
Cohesion: 0.12
Nodes (14): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for core/cognition/action_decision_chain.py., Tests for the prompt template definitions. (+6 more)

### Community 39 - "Experience"
Cohesion: 0.09
Nodes (14): Learning system for Jenbina - extracts lessons from experiences, Experience, Learning system for Jenbina — records experiences, extracts lessons, and…, Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3)., Check each active lesson against a new experience., Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set (+6 more)

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.12
Nodes (8): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Working Memory Design, Focus Tied to Sleep Need, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestFormatting, TestSalienceScoring

### Community 41 - "done"
Cohesion: 0.26
Nodes (19): approachPlayer(), count(), done(), drink(), eat(), explore(), failed(), gatherWood() (+11 more)

### Community 42 - "UserDatabase"
Cohesion: 0.08
Nodes (16): Connection, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first., The most recent ``limit`` events for a user, oldest first. (+8 more)

### Community 43 - "MemoryIntegration"
Cohesion: 0.12
Nodes (15): example_usage(), MemoryIntegration, Any, Person, Integrates the hybrid memory system with Jenbina's existing components, Store a memory of need state changes Args: need_name: Name of the need that…, Get relevant context for decision making Args: query: Query to search for…, Get comprehensive context about a person Args: person_name: Name of the person… (+7 more)

### Community 44 - "TestSocialInteractionTracker"
Cohesion: 0.08
Nodes (3): Test the intended usage: infer tone separately, pass only tone., Ensure no message text leaks into the stored interaction., TestSocialInteractionTracker

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
Nodes (29): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+21 more)

### Community 49 - "guardrails.py"
Cohesion: 0.11
Nodes (17): Safety Constraints (Asimov check chain + guardrails), build_system_message(), check_injection(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Check user input for injection patterns. Returns: (should_block, should_warn) (+9 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.24
Nodes (5): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "test_chains.py"
Cohesion: 0.09
Nodes (27): .coveragerc coverage config, GitHub Actions Workflows README, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action), Test Suite Workflow (push/manual), Testing Guidelines (unittest.TestCase, mock external services, tests mirror modules), GitHub Actions CI/CD (+19 more)

### Community 52 - "test_planning_system.py"
Cohesion: 0.16
Nodes (8): PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., make_step(), Tests for the planning system., TestPlanStep, _plan_fixture(), Two plans: one finished earlier, one whose last step completes this iteration;…

### Community 53 - "TestLesson"
Cohesion: 0.09
Nodes (11): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+3 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.14
Nodes (9): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}., Get the top-k emotions by intensity. (+1 more)

### Community 55 - "HostCase"
Cohesion: 0.11
Nodes (4): HostCase, TestLostTime, TestSleep, TestTurnsAndStepOnce

### Community 56 - "create_action_decision_chain"
Cohesion: 0.06
Nodes (35): callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead. (+27 more)

### Community 57 - "TestHybridMemorySystem"
Cohesion: 0.06
Nodes (16): Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval, Test temporal memory retrieval with event type filter, Test needs history retrieval (+8 more)

### Community 58 - "MinecraftWorld"
Cohesion: 0.08
Nodes (29): Jenbina's Minecraft world: a real, persistent place she perceives and acts in.…, MinecraftWorld, Outcome, Any, datetime, The Minecraft world as the simulation runner sees it. A beat calls ``observe``…, Start the world's processes if they are ours to start. Returns once they are…, Stop the processes ``start`` launched. Never raises. It does not log her out:… (+21 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.24
Nodes (4): Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "JenbinaHost"
Cohesion: 0.10
Nodes (11): JenbinaHost, datetime, timedelta, Attach the lock-releasing callback to an LLM the beats use., Stop the heart, save her and release the lease. With ``patience`` (seconds) it…, Start a real world's own processes; a described world has none., Log her out of a real world; a described world has nothing to leave. It waits…, Log her out if that was asked for while the mind lock was held. (+3 more)

### Community 62 - "File Structure"
Cohesion: 0.12
Nodes (15): File Structure, Global Constraints, Minecraft Inhabitants Implementation Plan, Review Focus, Task 10: Live check and documents, Task 1: Try Mindcraft on this machine, Task 2: Bridge hearing, Task 3: Bridge sees players (+7 more)

### Community 63 - "simulation_runner.py"
Cohesion: 0.11
Nodes (24): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, BeatAbandoned, _check_proactive_triggers(), credit_completed_plan(), _detect_location_from_action(), get_person_dict(), _print_json() (+16 more)

### Community 64 - "scene.py"
Cohesion: 0.14
Nodes (26): _article(), available_actions(), best_food(), build_world_state(), celsius(), _craft_label(), describe(), distance_from_home() (+18 more)

### Community 65 - "build.py"
Cohesion: 0.19
Nodes (15): check(), _file_matches(), main(), _pixels(), png_bytes(), Path, Pillow compositor and build CLI for the pixel sprites. Run ``python -m…, Every output image, keyed by path relative to ``assets/sprites``. (+7 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "Inhabitants: someone to talk to in her Minecraft world"
Cohesion: 0.17
Nodes (12): Anti-goals, Approaches, Code changes, Goals, How it works today, Inhabitants: someone to talk to in her Minecraft world, Intent, Left to the builder (+4 more)

### Community 68 - "bridge/package.json"
Cohesion: 0.08
Nodes (24): canvas, dependencies, mineflayer, mineflayer-collectblock, mineflayer-pathfinder, vec3, description, engines (+16 more)

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.07
Nodes (17): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+9 more)

### Community 71 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.19
Nodes (18): generate_user_dossier(), parse_research_results(), Any, Background user research for the Deep Emotional Mirror feature. Searches the…, Full pipeline: search web -> parse -> generate dossier. Returns a dossier dict,…, Call the SerpAPI web search API (serpapi.com). Returns raw JSON response from…, Extract useful text snippets from search results., Use LLM to generate a psychological profile from research snippets. (+10 more)

### Community 72 - "Design"
Cohesion: 0.11
Nodes (18): 10. Code changes, 1. Pages, 2. Shell, 3. Left column: the timeline, 4. The event log, 5. Right column: the status rail, 6. The runner, 7. Bug fixes in scope (+10 more)

### Community 73 - "test_live.py"
Cohesion: 0.11
Nodes (9): NotHostingError, RuntimeError, She is not (or no longer) living in this process., draw_guarded(), Periodic UI drawing that tolerates changes to the live mind., Live drawing and shared-host session integration without external services., TestHomeScreen, TestLiveDrawing (+1 more)

### Community 74 - "SocialInteractionTracker"
Cohesion: 0.07
Nodes (22): Initialize social interaction tracker., infer_emotional_tone(), Any, Social interaction tracker for Jenbina. Records each social interaction (chat,…, Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Return interactions from today (or since *day_start_ts*)., Return unique person names encountered today. (+14 more)

### Community 75 - "test_minecraft_inhabitants.py"
Cohesion: 0.09
Nodes (19): clean_line(), inhabitant_key(), _known_lines(), Her voice in the Minecraft world: the one prompt that writes what she says…, Writes her next line in a talk. Never raises: when no usable line comes, the…, The name she knows an inhabitant of the world by in her social memory, kept…, Her line, safe to say aloud: one line, never a command, at most ``MAX_LINE``…, How things stand between her and ``partner``, from her social memory. Only… (+11 more)

### Community 76 - "test_simulation.py"
Cohesion: 0.20
Nodes (9): fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the home screen loads with the timeline and heartbeat card., Click 'Step once' and verify the rail and the timeline fill in., sim_page() (+1 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - "WeatherData"
Cohesion: 0.12
Nodes (9): TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator, TestTimeData (+1 more)

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Person"
Cohesion: 0.04
Nodes (25): Person, Any, datetime, Initialize the insight system with an LLM instance., Decay needs, emotions, lessons and goals by elapsed real time., Move decay clocks past time when the heart was not running., Get current needs as a flat dict (for learning system), Get current emotions as a flat dict (for learning system) (+17 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.17
Nodes (6): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "test_simulation_runner.py"
Cohesion: 0.16
Nodes (4): HeadlessFixture, TestHeadlessParity, TestHeadlessProactive, TestSleepGate

### Community 84 - "Jenbina's Minecraft world"
Cohesion: 0.17
Nodes (12): Checking it by hand, Company, Jenbina's Minecraft world, Requirements, Run, Set up, once, Settings, The world's rules (+4 more)

### Community 85 - "TestOwnership"
Cohesion: 0.08
Nodes (4): A beat is mostly waiting on LLMs. A message must not wait for all of it., TestOwnership, TestTalkingDuringAMoment, TestUnreadableState

### Community 86 - "build_scene"
Cohesion: 0.14
Nodes (8): build_scene(), place_label(), ``Home`` near her home position, otherwise the biome in plain words., ``heard`` is what other players said since she last looked; ``can_talk`` is…, talks(), TestPlayersInTheScene, with_players(), TestPlaceAndScene

### Community 87 - "recording.py"
Cohesion: 0.11
Nodes (14): Recording helpers: turn runner state into timeline events. Both…, The current inner thought, or ``None`` when there is none., A move, only when the location actually changed., The chosen action with its reasoning, lessons and world context., A mood shift, or ``None`` when nothing moved by a full point., ``{description: (status, progress)}`` for every goal, ``{}`` without a system., Goal events for what changed between two snapshots: advanced or completed goals…, record_action() (+6 more)

### Community 88 - "Emotion"
Cohesion: 0.18
Nodes (6): Emotion, datetime, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "The design"
Cohesion: 0.20
Nodes (10): Cost, Hearing, Her voice, Remembering, Seeing, Settings, Starting and stopping them, Talking (+2 more)

### Community 90 - "Lesson"
Cohesion: 0.12
Nodes (9): Lesson, A learned pattern extracted from experiences., Test format_lessons_for_prompt, No lessons should return default message, Active lessons should appear in formatted text, Lessons should be sorted by confidence descending, Inactive lessons should not appear, Should show at most 10 lessons (+1 more)

### Community 91 - "Minecraft world: Jenbina lives in a real place"
Cohesion: 0.22
Nodes (9): Anti-goals, Approaches, Goals, How it works today, Intent, Left to the builder, Minecraft world: Jenbina lives in a real place, Non-goals (+1 more)

### Community 92 - "HybridMemorySystem"
Cohesion: 0.11
Nodes (12): HybridMemorySystem, OpenAI embeddings client, built lazily so an API key is only needed once…, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID, Store event in ChromaDB for semantic search (+4 more)

### Community 93 - "fix_llm_json"
Cohesion: 0.19
Nodes (8): fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function., TestFixLlmJson

### Community 94 - "MaslowNeedsSystem"
Cohesion: 0.06
Nodes (41): Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:…, Analyze progress through Maslow's hierarchy over time Args: person_needs:… (+33 more)

### Community 95 - "user_db.py"
Cohesion: 0.12
Nodes (12): datetime, SQLite user database for authentication and conversation persistence., Store one life event. ``created_at`` is written by Python (local, naive ISO…, _get_credentials_path(), _get_redirect_uri(), _get_user_db(), Login / signup UI for Jenbina (Streamlit) — Google SSO only., Return path to Google credentials file. Locally, reads… (+4 more)

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "EventLog"
Cohesion: 0.11
Nodes (10): EventLog, make_move(), Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., build_env(), A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a…, TestHeadlessRunnerEvents (+2 more)

### Community 98 - "bridge.js"
Cohesion: 0.11
Nodes (28): act(), { ACTIONS, stopMoving }, BRIDGE_PORT, BridgeError, { cleanLine, sayAndListen }, { createHearing }, { createSession }, hearing (+20 more)

### Community 99 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 100 - "adoption.py"
Cohesion: 0.16
Nodes (16): adopt_existing(), AdoptionReport, choose_user_to_adopt(), _experience_count(), _import_partner(), datetime, Person, Adopt one existing mind and retain each account's own relationship with her. (+8 more)

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 102 - "test_user_db.py"
Cohesion: 0.07
Nodes (9): Test UserDatabase initialisation and table creation., Test person state save/load., Messages from one user should not leak to another., get_all_users_with_message_counts splits by message_type, not sender., TestAdminMessageCounts, TestIsolation, TestListPersonStates, TestPersonState (+1 more)

### Community 103 - "TestBeatWithCompany"
Cohesion: 0.18
Nodes (5): FakeBridge, A bridge that can be spoken through. ``replies`` has one entry per say: a list…, The real runner with every LLM chain mocked, a fake bridge with Mira in it, and…, TalkBridge, TestBeatWithCompany

### Community 104 - "test_pixel_ui.py"
Cohesion: 0.05
Nodes (40): Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Streamlit session_state Persistence, Superpowers executing-plans Workflow, portrait_caption_html(), The name strip under the rail portrait., Redraw mood, place, doing/goal lines, needs bars and emotion chips., _css_token(), display_jenbina_image() (+32 more)

### Community 105 - "stage_pill_html"
Cohesion: 0.33
Nodes (4): The system stage pill in the status rail., stage_pill_html(), Show the system stage in the pill and remember it for reruns., TestMarkerAndPill

### Community 106 - "Step"
Cohesion: 0.18
Nodes (8): decide(), Choose one action without mutating the situation or consulting the clock., Step, TestBeats, asleep(), awake(), TestAsleep, TestAwake

### Community 107 - ".from_dict"
Cohesion: 0.33
Nodes (3): Deserialize from dictionary., to_dict -> from_dict should preserve state, from_dict with empty data should produce system with no emotions

### Community 108 - "render_frame"
Cohesion: 0.25
Nodes (6): frame_layers(), FrameSpec, Body, hair, face, props, effects — in drawing order., render_frame(), Layer, TestActionSheets

### Community 109 - "words.js"
Cohesion: 0.16
Nodes (19): GONE, { inventoryDiff, outcomeSummary }, OVERRUN, runRoutine(), settle(), assert, {
  DIRECTIONS, bestTool, hasSameOrBetterTool, inventoryDiff, itemPhrase, itemsPhrase, outcomeSummary
}, test (+11 more)

### Community 110 - "make_plan"
Cohesion: 0.22
Nodes (4): Plan, An ordered sequence of steps to achieve a goal., make_plan(), TestPlan

### Community 111 - "Design"
Cohesion: 0.10
Nodes (19): 1. One owner, 2. One record, 3. The rhythm, 4. Sleep, 5. Lost time, 6. Chat, 7. Many people, one Jenbina, 8. The home screen (+11 more)

### Community 112 - "is_admin"
Cohesion: 0.19
Nodes (12): Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, _hostname(), is_admin(), is_local_request(), The shared admin access check for the Admin page and heartbeat card., ``localhost`` from ``localhost:8501`` or ``http://localhost:8501``., Whether the request names this machine as its host. The Host and Origin headers…, Return True if the current visitor is allowed to see the admin panel. With… (+4 more)

### Community 113 - "WorldUnavailable"
Cohesion: 0.08
Nodes (9): RuntimeError, HTTP client for the Node bridge that is Jenbina's body in Minecraft. The bridge…, The Minecraft world cannot be reached or did not answer usefully., WorldUnavailable, FakeBridge, Records every call; answers with whatever the test sets., Her world starts when she does and stops when she does., TestHostStartsAndStopsTheWorld (+1 more)

### Community 114 - "chat.py"
Cohesion: 0.13
Nodes (20): ChatTurn, check_return_greeting(), ensure_greeting(), _get_user_db_and_id(), _get_user_display_name(), handle_user_input(), datetime, Chat UI components for Jenbina app (+12 more)

### Community 115 - "Jenbina Blob Character"
Cohesion: 0.50
Nodes (5): Jenbina Favicon (assets/favicon.png), Content/Happy Expression (soft smile, round eyes), Jenbina Blob Character, Streamlit Page Icon / Browser Tab Favicon, Tamagotchi Mascot Design Language

### Community 116 - "clear_chromadb.py"
Cohesion: 0.40
Nodes (4): check_chromadb_status(), clear_chromadb(), Clear the ChromaDB database and reset collections, Check the current status of ChromaDB

### Community 117 - "main"
Cohesion: 0.15
Nodes (6): build_host(), main(), Build the shared storage and LLMs only when a host is requested., Standalone heartbeat CLI tests; no real LLMs or background threads., TestBuildHost, TestHeartbeatMain

### Community 118 - "actions.js"
Cohesion: 0.14
Nodes (28): {
  ANIMALS, CRAFT_WHITELIST, FOODS, PLAIN_NAME, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
}, carried(), craft(), craftOnce(), { DIRECTIONS, bestTool }, ensureTable(), equipBest(), FILLERS (+20 more)

### Community 119 - "PersonModel"
Cohesion: 0.22
Nodes (5): Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, RelationshipState

### Community 120 - "Blade Runner 2049 Theme Redesign"
Cohesion: 0.12
Nodes (16): 1. Palette, 2. Type, 3. Shell, 4. Timeline, 5. Status rail, 6. Code changes, 7. Sidebar and tab icon, Anti-goals (what would make this a failure even if it works) (+8 more)

### Community 121 - "TestFocusNoise"
Cohesion: 0.40
Nodes (3): At 100% focus, noise range is 0., At low focus, salience values may vary between updates., TestFocusNoise

### Community 122 - "players.test.js"
Cohesion: 0.33
Nodes (6): assert, at(), fakeBot(), { playersAround }, test, { Vec3 }

### Community 123 - "shared_init.py"
Cohesion: 0.06
Nodes (49): _latest_world(), main(), Jenbina's home screen: a private conversation beside her shared live state., World and chosen action from the host's most recent moment. The world summary…, Jenbina — Environment & Debug page., Jenbina — Console Log page., Jenbina — Debug Info page., Show logged-in user info and a logout button in the sidebar. (+41 more)

### Community 125 - "File Structure"
Cohesion: 0.11
Nodes (17): Changes made after the tasks, from review, Decisions this plan makes inside the spec's "left to the builder", File Structure, Global Constraints, Heartbeat Implementation Plan, Review Focus, Task 10: End-to-end tests, docs, final check, Task 1: Storage for the being (+9 more)

### Community 126 - ".update"
Cohesion: 0.24
Nodes (3): Any, Buffer capacity based on focus: 3 (exhausted) to 7 (rested)., Recalculate working memory from current state. Called once per cycle.

### Community 128 - "choose_outreach_target"
Cohesion: 0.21
Nodes (6): choose_outreach_target(), datetime, Choose one recent conversation partner for a proactive message., Prefer closeness, then the newest message, after recency and cooldown checks., Outreach selection uses a fixed clock and no external services., TestOutreachTarget

### Community 129 - "Any"
Cohesion: 0.18
Nodes (7): Any, datetime, Retrieve memories based on semantic similarity, Get all relationships and interactions for a person, Get memories within a time range, Get needs satisfaction history over time, Get statistics about the memory system

### Community 136 - "MaslowNeed"
Cohesion: 0.06
Nodes (19): MaslowNeed, Check if need is critically low, Check if need is adequately met, Calculate priority score based on level, satisfaction, and importance, Initialize all needs in Maslow's hierarchy, Initialize all needs across all five levels, Get satisfaction level for a specific need, Represents a single need in Maslow's hierarchy (+11 more)

### Community 138 - "observation"
Cohesion: 0.38
Nodes (3): labels(), observation(), TestAvailableActions

### Community 139 - "art.py"
Cohesion: 0.14
Nodes (8): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, Pixel sprite assets for the Jenbina UI. Only paths and constants live here;…, Path of the 96x48 sheet for ``state``; unknown states get the ``base`` sheet., sprite_path(), Palette for the pixel art. One character per color in the art strings. This…, TestPaths

### Community 140 - "test_privacy.py"
Cohesion: 0.35
Nodes (4): CapturingLLM, Private conversation content must stay out of another person's prompts., TestNothingCrossesBetweenPeople, two_people()

### Community 141 - "store.py"
Cohesion: 0.22
Nodes (8): make_owner_id(), owner_is_dead(), _pid_namespace(), SQLite storage for the single being, separate from private account data., Identify the local PID namespace where the platform exposes it., Identify this host process and this particular attempt to host her., Only a missing PID in this machine's namespace proves an owner is dead., TestOwnerIdentity

### Community 143 - "build_timeline"
Cohesion: 0.10
Nodes (16): make_thought(), build_timeline(), first_sentence(), _hhmm(), _marker_text(), _passes(), datetime, Render the rows in order; an empty list shows the empty-state marker. (+8 more)

### Community 144 - "pixel_theme.py"
Cohesion: 0.06
Nodes (30): action_icon(), _data_uri(), delta_badge_html(), dialog_html(), event_html(), icon_html(), marker_html(), nav_icon_css() (+22 more)

### Community 145 - "session.test.js"
Cohesion: 0.16
Nodes (9): createSession(), join(), start(), sessionEnded(), assert, { createSession }, fakeWorld(), world (+1 more)

### Community 149 - "TimelineEvent"
Cohesion: 0.17
Nodes (14): format_duration(), LifeEventLog, make_gap(), make_goal(), make_mood(), make_sleep(), make_wake(), timedelta (+6 more)

### Community 150 - "Deploying Jenbina to Railway"
Cohesion: 0.22
Nodes (8): Deploying, Deploying Jenbina to Railway, Environment variables, Optional: Neo4j, Railway configuration (`.railway/railway.ts`), Setting up from scratch, The existing deployment, The heartbeat on Railway

### Community 151 - "hunt.test.js"
Cohesion: 0.20
Nodes (6): ACTIONS, { ACTIONS }, assert, { EventEmitter }, test, { Vec3 }

### Community 152 - "TestLearningSystemDecay"
Cohesion: 0.18
Nodes (6): Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, TestLearningSystemDecay

### Community 153 - ".create_plan"
Cohesion: 0.20
Nodes (5): Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Check if any active plan needs replanning. Returns replanned Plan or None., Generate a new plan from current state., Get active plan for a given goal id.

### Community 154 - "Need"
Cohesion: 0.05
Nodes (21): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Legacy needs property that maps to Maslow needs, Test backward compatibility with BasicNeeds (+13 more)

### Community 155 - "render_sheet"
Cohesion: 0.43
Nodes (3): The 96x48 two-frame sheet for ``state``; unknown state raises KeyError., render_sheet(), TestEmotionSheets

### Community 156 - "TestHostLeavesTheWorld"
Cohesion: 0.15
Nodes (3): She is never left standing in a running world while asleep or stopped., True when another thread could take her mind right now., TestHostLeavesTheWorld

### Community 158 - "test_timeline.py"
Cohesion: 0.16
Nodes (8): lessons_text(), make_action(), mood_changes(), Cut ``text`` to at most ``limit`` characters, at a word boundary when there is…, Lessons as one line: lists joined with '; ', strings as they are., ``{emotion: (before, after)}`` for the ``limit`` largest changes of at least…, shorten(), TestTitles

### Community 159 - "run.test.js"
Cohesion: 0.29
Nodes (6): assert, deps(), { DIED, runRoutine }, { EventEmitter }, options(), test

### Community 161 - ".waiting"
Cohesion: 0.23
Nodes (4): BaseCallbackHandler, _MindLockRelease, For the beat's own waits that are not a single LLM call on its thread, such as…, Lets go of the mind lock while a beat only waits for an LLM. A moment of her…

### Community 165 - "build_person"
Cohesion: 0.21
Nodes (7): BeingStateError, build_person(), Person, Construct the live being without any UI or process ownership concerns., Restore her state, fill missing systems, and bind the insight LLM., Saved person state could not be restored; never replace it silently., TestBuildPerson

### Community 166 - "TestChainRealWorldScenarios"
Cohesion: 0.25
Nodes (5): Test chains with realistic scenarios, Test chains in a morning routine scenario, Test chains in a stressful situation, Test chains in a creative work scenario, TestChainRealWorldScenarios

### Community 167 - "MinecraftBridge"
Cohesion: 0.15
Nodes (9): MinecraftBridge, Any, Log her in if needed and return the observation., Log her out. Never raises: leaving must not break a beat., Run one bounded routine and return its outcome., Whisper one line to another player and wait for what they say back. Returns…, HTTPError, TestSay (+1 more)

### Community 169 - "test_sprites.py"
Cohesion: 0.18
Nodes (6): all_layers(), Tests for the pixel sprite pipeline (core.ui.sprites)., TestArtLayers, TestPalette, TestPortraits, TestTimelineIcons

### Community 170 - "TestLearningSystemStats"
Cohesion: 0.22
Nodes (5): Test get_learning_stats, Empty system should return zero counts, Stats should reflect recorded data, recent_experiences should show at most 5, TestLearningSystemStats

### Community 174 - ".fresh"
Cohesion: 0.21
Nodes (3): Restore valid fields independently; old or malformed fields default., TestSituation, TestSavedWorldMemory

### Community 175 - "compose"
Cohesion: 0.36
Nodes (3): compose(), Draw ``layers`` in order onto a transparent RGBA canvas. A ``"."`` pixel leaves…, TestCompose

### Community 176 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 177 - ".generate_insight"
Cohesion: 0.18
Nodes (6): Any, Check if conditions are met to generate a subtle insight.…, Generate a subtle perceptive observation about the user. Returns the insight…, Check if we should fire the bold first-impression insight., Generate a bold, striking first-impression observation. Returns the insight…, date

### Community 179 - "TestLearningSystemSerialization"
Cohesion: 0.18
Nodes (6): Test from_dict(to_dict()) preserves data, Test to_dict / from_dict serialization, Empty system should serialize and restore, System with experiences and lessons should roundtrip, Extraction counter should survive serialization, TestLearningSystemSerialization

### Community 182 - ".get_current_step"
Cohesion: 0.25
Nodes (3): Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None., Mark current step completed and move to next.

### Community 183 - "world_from_env"
Cohesion: 0.29
Nodes (5): ``JENBINA_MINECRAFT_TALKS_PER_DAY``: a whole number of 0 or more, else the…, The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world., _talks_per_day(), world_from_env(), TestWorldFromEnv

### Community 184 - "test_goal_system.py"
Cohesion: 0.22
Nodes (4): Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemIntegration, TestGoalSystemStats

### Community 187 - "test_heartbeat_store.py"
Cohesion: 0.08
Nodes (5): Storage for the single being, independent of accounts and Streamlit., StoreTestCase, TestLease, TestPeople, TestStateAndEvents

### Community 188 - "match_action_key"
Cohesion: 0.36
Nodes (3): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, TestActionKeywordMatch

### Community 190 - "within.test.js"
Cohesion: 0.40
Nodes (3): assert, test, { within }

### Community 191 - ".get_or_create_model"
Cohesion: 0.38
Nodes (3): Choose when to be nice, polite, or assertive., Predict likely reaction from relationship + inferred emotional state., Build a concise ToM context block for LLM prompting.

### Community 193 - "render_icon"
Cohesion: 0.40
Nodes (3): One 8x8 icon; unknown name raises KeyError., render_icon(), TestIcons

### Community 194 - "build_search_query"
Cohesion: 0.47
Nodes (3): build_search_query(), Build a web search query from user info., TestBuildSearchQuery

### Community 195 - "Inner Life Surfacing via Prompt Engineering"
Cohesion: 0.60
Nodes (6): Deep Emotional Mirror Design Doc, Deep Emotional Mirror (Wow Effect), LLM-Generated Greetings (first-time & returning), Inner Life Surfacing via Prompt Engineering, Insight Generation (one deep observation), Model Split: GPT-5.2 user-facing, GPT-5-nano JSON internals

### Community 196 - "TestMemoryIntegrationFactory"
Cohesion: 0.33
Nodes (4): Test memory integration factory functions, Test creating memory integration with default settings, Test creating memory integration with custom paths, TestMemoryIntegrationFactory

### Community 197 - ".test_full_plan_lifecycle"
Cohesion: 0.40
Nodes (3): Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete., TestPlanningSystemIntegration

### Community 202 - "dependencies"
Cohesion: 0.50
Nodes (3): railway, dependencies, railway

### Community 203 - "Planning System Design"
Cohesion: 0.67
Nodes (3): Planning System Design, Multi-step Chain-of-Thought Planning, Plan Step Completion Detection & Replan Trigger

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls

## Knowledge Gaps
- **251 isolated node(s):** `railway`, `partial`, `{ goals }`, `{ Vec3 }`, `{ DIRECTIONS, bestTool }` (+246 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **Why does `Person` connect `Person` to `choose_outreach_target`, `_make_mock_llm`, `CLAUDE.md Project Instructions`, `TestChains`, `Conversation`, `SocialCognitionSystem`, `observation`, `rail.py`, `test_privacy.py`, `InsightSystem`, `voice_prompt`, `TestPerson`, `CuriositySystem`, `SelfNarrativeSystem`, `core/__init__.py`, `world_state.py`, `GoalSystem`, `PlanningSystem`, `test_minecraft_world.py`, `TestMemoryIntegration`, `build_person`, `_invoke_and_parse`, `Experience`, `WorkingMemorySystem`, `MemoryIntegration`, `Goal`, `test_chains.py`, `EmotionSystem`, `create_action_decision_chain`, `TestPerPersonInsights`, `Deep Emotional Mirror Implementation Plan`, `SocialInteractionTracker`, `Planning System Design`, `test_minecraft_inhabitants.py`, `test_simulation_runner.py`, `TestOwnership`, `MaslowNeedsSystem`, `EventLog`, `adoption.py`, `test_pixel_ui.py`, `chat.py`?**
  _High betweenness centrality (0.224) - this node is a cross-community bridge._
- **Why does `CLAUDE.md Project Instructions` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `Deep Emotional Mirror Implementation Plan`, `test_pixel_ui.py`, `StreamCapture`, `ChromaMemoryManager`, `guardrails.py`, `test_chains.py`, `clear_chromadb.py`, `create_action_decision_chain`, `shared_init.py`, `HybridMemorySystem`, `get_llm`, `MaslowNeedsSystem`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `Jenbina README` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `GoalSystem`, `MetaCognitiveSystem`, `Deep Emotional Mirror Implementation Plan`, `EnvironmentSimulator`, `SocialCognitionSystem`, `InsightSystem`, `LearningSystem`, `CuriositySystem`, `test_chains.py`, `Person`, `SelfNarrativeSystem`, `EmotionSystem`, `create_action_decision_chain`, `shared_init.py`, `get_llm`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `Jenbina README` and `Reptile Brain (motivational core)`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `WorkingMemorySystem` (e.g. with `Experience` and `MaslowNeedsSystem`) actually correct?**
  _`WorkingMemorySystem` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Person` (e.g. with `run_simulation()` and `adopt_existing()`) actually correct?**
  _`Person` has 40 INFERRED edges - model-reasoned connections that need verification._