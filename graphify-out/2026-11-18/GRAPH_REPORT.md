# Graph Report - jenbina-virtual-world-c16b9b  (2026-11-18)

## Corpus Check
- 209 files · ~531,125 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4283 nodes · 9033 edges · 187 communities (157 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 532 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9c44b1c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InnerMonologueSystem
- _make_mock_llm
- WorldLauncher
- CLAUDE.md Project Instructions
- timeline.py
- MetaCognitiveSystem
- Lesson
- .init_planning_system
- EnvironmentSimulator
- SocialCognitionSystem
- rail.py
- .update_all_needs
- Design
- InsightSystem
- .voice
- Person
- TestPerson
- LearningSystem
- Deep Emotional Mirror Implementation Plan
- TestTalk
- make_experience
- SelfNarrativeSystem
- generate_return_greeting
- memory/__init__.py
- make_mock_llm
- say.test.js
- DynamicEventsSystem
- StreamCapture
- BeingStore
- get_llm
- world_state.py
- chat_handler.py
- GoalSystem
- PlanningSystem
- RhythmConfig
- TestEmotion
- TestMemoryIntegration
- TestMaslowNeedsSystem
- _invoke_and_parse
- TestExperience
- WorkingMemorySystem
- done
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
- HostCase
- WorldState
- MemoryEvent
- MinecraftWorld
- TestUserCRUD
- WorkingMemoryItem
- JenbinaHost
- File Structure
- .launcher
- simulation.py
- build.py
- _run_one_iteration
- Inhabitants: someone to talk to in her Minecraft world
- package.json
- FirebaseAuth
- Conversation
- simulation_runner.py
- Design
- TestConversation
- SocialInteractionTracker
- scene.py
- test_simulation.py
- File Structure
- WeatherData
- test_social_interaction_tracker.py
- Design
- Person
- test_working_memory.py
- test_simulation_runner.py
- Jenbina's Minecraft world
- TestOwnership
- test_minecraft_world.py
- test_timeline.py
- Emotion
- The design
- .record_social_action
- Minecraft world: Jenbina lives in a real place
- HybridMemorySystem
- SocialInteraction
- MaslowNeedsSystem
- env_line_html
- Review Focus
- EventLog
- bridge.js
- generate_first_greeting
- saved_state
- make_needs
- TestHomeScreen
- TestBeatWithCompany
- render_needs_bars
- match_action_key
- Step
- .from_dict
- render_frame
- words.js
- LifeEventLog
- Design
- is_admin
- FakeBridge
- chat.py
- Jenbina Blob Character
- clear_chromadb.py
- main
- actions.js
- inject_pixel_css
- Blade Runner 2049 Theme Redesign
- TestFocusNoise
- players.test.js
- shared_init.py
- TestHearingAcrossBeats
- File Structure
- .update
- .from_dict
- choose_outreach_target
- 3_🌍_Environment.py
- TestMaslowNeed
- TestAdoption
- .get_daily_activity_suggestion
- art.py
- test_privacy.py
- make_owner_id
- TestUiExports
- build_timeline
- test_pixel_ui.py
- session.test.js
- TestEvents
- TestPerform
- fix_llm_json
- TestRunnerInMinecraft
- .from_dict
- hunt.test.js
- TestProfiles
- TestPromptTemplates
- TestBasicNeedsBackwardCompatibility
- render_sheet
- TestHostLeavesTheWorld
- heartbeat/__init__.py
- _StatusSink
- run.test.js
- .add_note
- .waiting
- Any
- TestResolveAction
- host.py
- run_chain_tests.py
- MinecraftBridge
- _format_mood_factors
- test_sprites.py
- SimpleEmbeddings
- run_server.sh
- setup_server.sh
- _format_nearby_locations
- .fresh
- compose
- streamlit_server
- build_env
- TestTalkingDuringAMoment
- _format_time_details
- setup_inhabitants.sh
- world_from_env
- .get_planning_stats
- FakeEmotions
- TestSharedHost
- within.test.js
- TestPaths

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

## Communities (187 total, 30 thin omitted)

### Community 0 - "InnerMonologueSystem"
Cohesion: 0.05
Nodes (39): InnerMonologueSystem, InnerThought, Any, Enum, Internal monologue / stream-of-consciousness system for Jenbina. Generates the…, Generates Jenbina's internal stream of consciousness between decisions., Determine which thought mode to activate based on current state. Priority…, Use the LLM to generate an inner-monologue thought in the given mode. (+31 more)

### Community 1 - "_make_mock_llm"
Cohesion: 0.06
Nodes (26): _make_mock_llm(), _make_mock_llm_failing(), _make_mock_person(), Tests for GPT-generated greeting functions., LLM response is returned when generation succeeds., The prompt sent to the LLM includes the user's display name., The prompt includes the person's emotional state., Goals are included in the prompt when the goal system exists. (+18 more)

### Community 2 - "WorldLauncher"
Cohesion: 0.06
Nodes (32): RuntimeError, HTTP client for the Node bridge that is Jenbina's body in Minecraft. The bridge…, The Minecraft world cannot be reached or did not answer usefully., WorldUnavailable, Jenbina's Minecraft world: a real, persistent place she perceives and acts in.…, inhabitant_settings(), is_local(), port_open() (+24 more)

### Community 3 - "CLAUDE.md Project Instructions"
Cohesion: 0.08
Nodes (55): .coveragerc coverage config, GitHub Actions Workflows README, Playwright E2E Tests Workflow, JENBINA_SKIP_AUTH E2E Auth Bypass Flag, Feedback Loop E2E Test Workflow, Run Unit Tests Workflow (PR gate), Codecov Coverage Upload, Pytest Coverage PR Comment (MishaKav action) (+47 more)

### Community 4 - "timeline.py"
Cohesion: 0.15
Nodes (16): action_icon(), event_html(), The icon name for an action's row, by keyword; the star when none fits., One timeline row for a life event: a kind tag, the title, then badge and meta.…, action_details_text(), _event_row_html(), _hhmm(), _marker_text() (+8 more)

### Community 5 - "MetaCognitiveSystem"
Cohesion: 0.08
Nodes (24): Cognition and Decision Making Submodule This submodule handles all aspects of…, CognitiveProcess, MetaCognitiveInsight, MetaCognitiveSystem, Any, BaseLLM, Represents a single cognitive process/decision, Analyze patterns across multiple cognitive processes (+16 more)

### Community 6 - "Lesson"
Cohesion: 0.06
Nodes (20): Lesson, A learned pattern extracted from experiences., Test lesson decay and pruning, All lessons should lose confidence, Lessons at or below threshold are removed, Heavy decay should prune all low-confidence lessons, Zero hours decay should not change anything, Test format_lessons_for_prompt (+12 more)

### Community 8 - "EnvironmentSimulator"
Cohesion: 0.11
Nodes (14): EnvironmentSimulator, any, Fetch real weather data from OpenWeatherMap, Simulate realistic weather based on time and season, Update time-related data, Get complete environment state, Calculate how environment affects mood, Get local events based on Palo Alto location system (+6 more)

### Community 9 - "SocialCognitionSystem"
Cohesion: 0.09
Nodes (15): Initialize social cognition / theory-of-mind system., Social cognition submodule (Theory of Mind)., PersonModel, Any, Social cognition / Theory-of-Mind system for Jenbina. Tracks beliefs about…, Tracks social models and chooses social strategy for conversations., Update person model from an incoming message., Estimate relationship drift after Jenbina's response strategy. (+7 more)

### Community 10 - "rail.py"
Cohesion: 0.07
Nodes (30): HeartStatus, _about_you_lines(), _card_title(), _goal_lines(), heartbeat_lines(), _lesson_lines(), NullRail, _plan_lines() (+22 more)

### Community 11 - ".update_all_needs"
Cohesion: 0.29
Nodes (5): datetime, timedelta, Update all needs based on time passed, Update the current growth stage based on need satisfaction, Update need satisfaction over time

### Community 12 - "Design"
Cohesion: 0.12
Nodes (17): Actions, Code changes, Death, Design, Leaving the world safely, Needs the world owns, Observation, One beat in Minecraft (+9 more)

### Community 13 - "InsightSystem"
Cohesion: 0.09
Nodes (14): InsightSystem, Any, Insight generation system for the Deep Emotional Mirror feature. Two modes: 1.…, Check if conditions are met to generate a subtle insight.…, Generate a subtle perceptive observation about the user. Returns the insight…, Generates deep perceptive observations about users mid-conversation., Check if we should fire the bold first-impression insight., Generate a bold, striking first-impression observation. Returns the insight… (+6 more)

### Community 14 - ".voice"
Cohesion: 0.07
Nodes (17): clean_line(), inhabitant_key(), Her voice in the Minecraft world: the one prompt that writes what she says…, Writes her next line in a talk. Never raises: when no usable line comes, the…, The name she knows an inhabitant of the world by in her social memory, kept…, Her line, safe to say aloud: one line, never a command, at most ``MAX_LINE``…, The whole prompt for her next line to ``partner``. ``last_lines`` are the last…, _read_answer() (+9 more)

### Community 15 - "Person"
Cohesion: 0.09
Nodes (11): Any, Person, Get overall communication statistics, Get a summary of the person's current state, Update all needs for this person, Start a new conversation with an outsider, Receive a message from an outsider, Send a message to an outsider (+3 more)

### Community 16 - "TestPerson"
Cohesion: 0.05
Nodes (19): Test Person functionality, Test person initialization, Test person with default name, Test updating all needs, Test adding a new conversation, Test adding conversation with existing person, Test receiving a message from outsider, Test sending a message to outsider (+11 more)

### Community 17 - "LearningSystem"
Cohesion: 0.06
Nodes (30): Learning system for Jenbina - extracts lessons from experiences, Experience, LearningSystem, Any, Learning system for Jenbina — records experiences, extracts lessons, and…, Records experiences, extracts lessons via LLM, and formats them for prompts., Before/after snapshot around an action., Use LLM to analyse recent experiences and add new lessons (max 3). (+22 more)

### Community 18 - "Deep Emotional Mirror Implementation Plan"
Cohesion: 0.05
Nodes (43): .env.example template, Environment Variables (.env / .env.example), Plan Document Format (Goal/Architecture/Tech Stack/Tasks with files, steps, tests, commit), Superpowers executing-plans Workflow, CuriositySystem, NoveltyEvent, Any, Curiosity and exploration system for Jenbina. Implements: - Information-seeking… (+35 more)

### Community 19 - "TestTalk"
Cohesion: 0.17
Nodes (5): chatty_voice(), A voice that says ``lines`` in turn, each ``(text, end)``, then falls silent., scripted_voice(), TalkCase, TestTalk

### Community 20 - "make_experience"
Cohesion: 0.07
Nodes (19): make_experience(), Test LearningSystem without LLM (unit-level), Test system initializes with empty state, Test recording a single experience, Test that deltas are computed correctly, Test emotion delta computation, Test that experiences are capped at MAX_EXPERIENCES, Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences (+11 more)

### Community 21 - "SelfNarrativeSystem"
Cohesion: 0.12
Nodes (9): Identity / self-narrative submodule., NarrativeEvent, Any, Self-narrative and identity system for Jenbina. Builds a stable-but-evolving…, Tracks identity and narrative continuity from experiences., Update identity from a new experience and current lessons., SelfNarrativeSystem, Initialize self-narrative / identity system. (+1 more)

### Community 22 - "generate_return_greeting"
Cohesion: 0.14
Nodes (9): generate_proactive_message(), generate_return_greeting(), Generate a 1-3 sentence natural message Jenbina sends on her own. Args: person:…, Generate a dynamic return greeting based on Jenbina's state and relationship., Exception, _make_mock_person(), Create a minimal mock Person with all subsystems stubbed., TestGenerateProactiveMessage (+1 more)

### Community 23 - "memory/__init__.py"
Cohesion: 0.15
Nodes (12): LocationNode, PersonNode, Represents a person in the graph database, Represents a location in the graph database, Memory Management Submodule This submodule handles all aspects of the AI's…, create_memory_integration(), Memory Integration Module Shows how to integrate the hybrid memory system with…, Create a memory integration instance with default settings Returns:… (+4 more)

### Community 24 - "make_mock_llm"
Cohesion: 0.17
Nodes (8): make_experience(), make_mock_llm(), Tests for the goal system., Test: generate → advance → decay → abandon., TestGoalSystemFormatting, TestGoalSystemIntegration, TestGoalSystemMilestone, TestGoalSystemProgress

### Community 25 - "say.test.js"
Cohesion: 0.12
Nodes (11): createHearing(), assert, { createHearing }, test, { ACTIONS }, assert, { cleanLine, sayAndListen }, { createHearing } (+3 more)

### Community 26 - "DynamicEventsSystem"
Cohesion: 0.13
Nodes (15): DynamicEventsSystem, Event, Get events from multiple sources, Get venues from multiple sources, Fetch events from Eventbrite API, Fetch events from Ticketmaster API, Fetch events from Yelp API, Fetch venues from Yelp API (+7 more)

### Community 27 - "StreamCapture"
Cohesion: 0.11
Nodes (10): install_capture(), Capture stdout/stderr to session state while preserving console output., Tee-style stream wrapper that captures output and forwards to original stream., Sync the global log buffer into session state. Call on every page load., StreamCapture, Tests for core/log_capture.py — StreamCapture and global log buffer., Tests for the StreamCapture tee-style stream wrapper., Tests for install_capture() function. (+2 more)

### Community 28 - "BeingStore"
Cohesion: 0.06
Nodes (16): BeingStore, Lease, Connection, datetime, timedelta, Save only for the current lease holder when an owner is supplied., The newest events, oldest first, in UserDatabase.get_events format., Copy a user's event rows, keeping their timestamps and content. (+8 more)

### Community 29 - "get_llm"
Cohesion: 0.09
Nodes (19): LLM JSON Parsing via fix_llm_json, get_json_llm(), get_llm(), get_recommended_llm(), Get LLM with recommended configuration for specific use case. Args: use_case:…, Use a finite positive timeout, falling back to sixty seconds., Get LLM instance based on provider preference. Args: provider: Which LLM…, Get LLM configured for reliable JSON output. Args: provider: Which LLM service… (+11 more)

### Community 30 - "world_state.py"
Cohesion: 0.08
Nodes (26): EnvironmentState, Environment and World Simulation Submodule This submodule handles all aspects…, Location, Neighborhood, PaloAltoLocationSystem, Initialize neighborhoods in Palo Alto and surrounding areas, Get a specific location by name, Get a specific neighborhood by name (+18 more)

### Community 31 - "chat_handler.py"
Cohesion: 0.09
Nodes (17): basic_needs_to_json(), _build_subsystem_context(), _chat_avatar(), create_metadata_from_person_state(), ``section[key]`` for the nested world-summary shape, the value itself for a…, Convert BasicNeeds object to JSON-serializable format, Avatar for a chat row: Jenbina's portrait, or Streamlit's own user icon.…, Create metadata dictionary from person state and other context (+9 more)

### Community 32 - "GoalSystem"
Cohesion: 0.09
Nodes (9): GoalSystem, Any, Generates, tracks, and manages goals across time horizons., Set experience list for milestone checking., Decay confidence and abandon dead goals., Initialize the goal system with an LLM instance. Called separately because LLM…, TestGoalSystem, TestGoalSystemGeneration (+1 more)

### Community 33 - "PlanningSystem"
Cohesion: 0.09
Nodes (16): PlanningSystem, Decomposes goals into plans and tracks execution across cycles., make_experience(), make_mock_llm(), make_plan(), Tests for the planning system., Test: create plan → execute steps → complete., Test: create plan → get stuck → replan → complete. (+8 more)

### Community 34 - "RhythmConfig"
Cohesion: 0.14
Nodes (16): Attach the lock-releasing callback to an LLM the beats use., Ask the heart for a moment now, without waiting for it. The heart takes it on…, beats_today(), _elapsed(), is_night(), lost_time(), next_beat_at(), datetime (+8 more)

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
Cohesion: 0.16
Nodes (12): _invoke_and_parse(), Any, BaseLLM, Invoke the LLM and parse the JSON response, repairing if needed., _make_mock_llm(), patch, Tests for core/cognition/action_decision_chain.py., Tests for the _invoke_and_parse helper. (+4 more)

### Community 39 - "TestExperience"
Cohesion: 0.14
Nodes (7): Test that from_dict(to_dict()) preserves data, Test that timestamp is auto-set, Test that world_context defaults to empty dict, Test Experience dataclass, Test experience stores all fields, Test serialization to dict, TestExperience

### Community 40 - "WorkingMemorySystem"
Cohesion: 0.12
Nodes (6): Maintains a salience-ranked buffer of what Jenbina is currently thinking about., WorkingMemorySystem, Salience-Based Working Memory Buffer (3-7 items), TestBufferCapacity, TestContextSwitch, TestSalienceScoring

### Community 41 - "done"
Cohesion: 0.26
Nodes (19): approachPlayer(), count(), done(), drink(), eat(), explore(), failed(), gatherWood() (+11 more)

### Community 42 - "UserDatabase"
Cohesion: 0.04
Nodes (29): Connection, datetime, SQLite-backed storage for users, conversations, and person state., Lookup a user by Firebase UID. Returns dict or None., Lookup a user by their integer primary key. Returns dict or None., Return all users as a list of dicts., Store a chat message. Returns the new row id., Retrieve the most recent messages for a user, oldest-first. (+21 more)

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
Cohesion: 0.09
Nodes (13): Goal, Goal system for Jenbina — generates and tracks short/mid/long-term goals., Use LLM to propose new goals based on current state., Update goal progress based on a new experience. Returns goals that advanced., Ask LLM whether a goal has been achieved., A goal Jenbina is pursuing., Goal System Design, Goal Generation Prompt (needs, traits, emotions, lessons -> up to 3 goals) (+5 more)

### Community 48 - "ChromaMemoryManager"
Cohesion: 0.07
Nodes (25): clear_memory(), ChromaMemoryManager, parse_basic_needs_from_json(), Any, datetime, Initialize or load the Chroma vector store, Generate a unique ID for the embedding, Store a conversation message in Chroma Args: person_name: Name of the person… (+17 more)

### Community 49 - "TestCheckInjectionBlock"
Cohesion: 0.05
Nodes (19): Safety Constraints (Asimov check chain + guardrails), build_system_message(), JENBINA_SYSTEM_PROMPT, make_refusal_response(), Prompt-injection guardrails for Jenbina's chat interface. All detection is…, In-character vague deflection for blocked messages., Return the system prompt, optionally with a warning addendum., Ethical AI Framework (Asimov's laws compliance, safety-first decisions, transparent reasoning) (+11 more)

### Community 50 - "handle_chat_interaction"
Cohesion: 0.29
Nodes (6): handle_chat_interaction(), Handle chat interactions with Jenbina using Chroma memory., _make_mock_llm(), _make_mock_st(), Create a mock Streamlit module., TestHandleChatInteraction

### Community 51 - "Need"
Cohesion: 0.09
Nodes (13): Need, Legacy Need class for backward compatibility, Decrease satisfaction over time, Increase satisfaction by given amount, Check if need is critically low (below 20), Check if need is low (below 50), Legacy needs property that maps to Maslow needs, Test the legacy Need class (+5 more)

### Community 52 - "Plan"
Cohesion: 0.07
Nodes (17): Plan, PlanStep, Planning system for Jenbina — decomposes goals into multi-step plans., A single step in a plan., Use LLM to decompose a goal into steps., Extract steps array from various LLM response formats., Return (plan, step) for the highest-priority active plan., Evaluate current step after a cycle. Returns status string or None. (+9 more)

### Community 53 - "TestLesson"
Cohesion: 0.08
Nodes (12): Test Lesson dataclass, Test lesson stores all fields, Test that reinforce increases confidence and confirm count, Test that confidence doesn't exceed 1.0, Test that contradict decreases confidence, Test that confidence doesn't go below 0.0, Test that decay reduces confidence over time, Test decay doesn't go below 0 (+4 more)

### Community 54 - "EmotionSystem"
Cohesion: 0.15
Nodes (9): EmotionSystem, Any, Serialize to dictionary., Complete emotion system with decay toward character baselines., Initialize Jenbina's default character emotions (Plutchik's wheel)., Spike a specific emotion by amount (positive or negative)., Apply a dict of emotion adjustments, e.g. {"joy": 15, "fear": -10}., Get the top-k emotions by intensity. (+1 more)

### Community 55 - "HostCase"
Cohesion: 0.11
Nodes (4): HostCase, TestLostTime, TestSleep, TestTurnsAndStepOnce

### Community 56 - "WorldState"
Cohesion: 0.04
Nodes (62): callable, create_action_decision_chain(), Return a callable that runs a 3-step chain-of-thought action decision. Steps:…, _as_bool(), create_asimov_check_system(), BaseLLM, Creates and returns a function that checks if actions comply with Asimov's…, JSON booleans as they come; the strings an LLM sometimes writes instead. (+54 more)

### Community 57 - "MemoryEvent"
Cohesion: 0.07
Nodes (21): MemoryEvent, Represents a memory event with all its components, Clean up test fixtures, Test system initialization, Test storing a memory event, Test storing memory with auto-generated ID, Test semantic memory retrieval, Test temporal memory retrieval (+13 more)

### Community 58 - "MinecraftWorld"
Cohesion: 0.09
Nodes (15): MinecraftWorld, datetime, Start the world's processes if they are ours to start. Returns once they are…, Stop the processes ``start`` launched. Never raises. It does not log her out:…, Take her out of the world, even when she is set to stay online. Called by her…, The scene as it is after an action, for the summary the rail shows., Keep what an observation says was heard, for her next look., The carried lines that are still fresh; the carried list is emptied. (+7 more)

### Community 59 - "TestUserCRUD"
Cohesion: 0.20
Nodes (3): Test user create / read / update operations., COALESCE(?, col) keeps old value when new value is None., TestUserCRUD

### Community 60 - "WorkingMemoryItem"
Cohesion: 0.24
Nodes (4): Working memory system for Jenbina — short-term buffer of current thoughts., An item currently in working memory., WorkingMemoryItem, TestWorkingMemoryItem

### Community 61 - "JenbinaHost"
Cohesion: 0.14
Nodes (8): JenbinaHost, datetime, timedelta, Stop the heart, save her and release the lease. With ``patience`` (seconds) it…, Start a real world's own processes; a described world has none., Log her out of a real world; a described world has nothing to leave. It waits…, Log her out if that was asked for while the mind lock was held., Consume a pending request; True when the beat should run now.

### Community 62 - "File Structure"
Cohesion: 0.12
Nodes (15): File Structure, Global Constraints, Minecraft Inhabitants Implementation Plan, Review Focus, Task 10: Live check and documents, Task 1: Try Mindcraft on this machine, Task 2: Bridge hearing, Task 3: Bridge sees players (+7 more)

### Community 63 - ".launcher"
Cohesion: 0.07
Nodes (9): FakeProcess, InhabitantsCase, LauncherCase, A world that is up, with Mindcraft set up beside it., TestEnsureReady, TestInhabitants, TestInhabitantsWatch, TestStart (+1 more)

### Community 64 - "simulation.py"
Cohesion: 0.17
Nodes (11): portrait_caption_html(), The name strip under the rail portrait., _css_token(), _get_image_path(), get_jenbina_image_for_action(), _portrait_path(), Portrait and state renderers for Jenbina's UI., Lower-case ``name`` reduced to [a-z0-9_] so it is safe inside a class attribute. (+3 more)

### Community 65 - "build.py"
Cohesion: 0.19
Nodes (15): check(), _file_matches(), main(), _pixels(), png_bytes(), Path, Pillow compositor and build CLI for the pixel sprites. Run ``python -m…, Every output image, keyed by path relative to ``assets/sprites``. (+7 more)

### Community 66 - "_run_one_iteration"
Cohesion: 0.18
Nodes (13): skip, fixture, Page, Over 5 iterations, Jenbina should not repeat the exact same action every single…, After running an iteration, need bars should be visible in the UI., Navigate to the Streamlit app and wait for it to be ready., Run a single simulation iteration and return observed data. Reloads the page…, Run multiple iterations and verify the simulation feedback loop produces… (+5 more)

### Community 67 - "Inhabitants: someone to talk to in her Minecraft world"
Cohesion: 0.17
Nodes (12): Anti-goals, Approaches, Code changes, Goals, How it works today, Inhabitants: someone to talk to in her Minecraft world, Intent, Left to the builder (+4 more)

### Community 68 - "package.json"
Cohesion: 0.08
Nodes (24): canvas, dependencies, mineflayer, mineflayer-collectblock, mineflayer-pathfinder, vec3, description, engines (+16 more)

### Community 69 - "FirebaseAuth"
Cohesion: 0.14
Nodes (8): FirebaseAuth, Firebase authentication wrapper using pyrebase4., Build config dict from environment variables., Sign in with email and password. Returns Pyrebase user dict., Create a new account. Returns Pyrebase user dict., Retrieve account info from a Firebase ID token., Placeholder — Google OAuth handled by streamlit-google-auth. In the Streamlit…, Wraps Pyrebase auth for email/password and OAuth sign-in. Usage:: config = {…

### Community 70 - "Conversation"
Cohesion: 0.15
Nodes (9): Conversation, Message, Represents a conversation with a specific outsider, Add a new message to the conversation, Get the most recent messages from the conversation, Get all messages of a specific type, Get conversation history with a specific outsider, Get all conversations (+1 more)

### Community 71 - "simulation_runner.py"
Cohesion: 0.07
Nodes (27): history_context(), ``(recent_actions, world_context)`` read from the records the runners append to…, BeatAbandoned, _check_proactive_triggers(), credit_completed_plan(), _detect_location_from_action(), get_person_dict(), _print_json() (+19 more)

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
Cohesion: 0.07
Nodes (42): Do what she chose and report what really happened. Never raises. ``waiting`` is…, A short exchange with another inhabitant, inside this one beat. Every call to…, _article(), available_actions(), best_food(), build_world_state(), celsius(), _craft_label() (+34 more)

### Community 76 - "test_simulation.py"
Cohesion: 0.20
Nodes (9): fixture, Page, Playwright E2E test — run a single simulation iteration on the home screen and…, Navigate to the Streamlit app and wait for it to be ready., Run one iteration via the UI and check that each simulation stage renders non-…, Sanity check — the home screen loads with the timeline and heartbeat card., Click 'Step once' and verify the rail and the timeline fill in., sim_page() (+1 more)

### Community 77 - "File Structure"
Cohesion: 0.13
Nodes (14): File Structure, Global Constraints, Pixel Art UI Implementation Plan, Review Focus, Task 10: Visual verification and e2e, Task 1: Palette and compositor, Task 2: Body, hair, faces and the emotion states, Task 3: Props, effects and the action states (+6 more)

### Community 78 - "WeatherData"
Cohesion: 0.12
Nodes (9): TimeData, WeatherData, Tests for core/environment/environment_simulator.py., Tests for the WeatherData dataclass., Tests for the TimeData dataclass., Tests for EnvironmentSimulator., TestEnvironmentSimulator, TestTimeData (+1 more)

### Community 79 - "test_social_interaction_tracker.py"
Cohesion: 0.22
Nodes (6): infer_emotional_tone(), Social interaction tracker for Jenbina. Records each social interaction (chat,…, Return a simple emotional-tone label from message text. This is a *stateless*…, Tests for the SocialInteractionTracker system., Test the intended usage: infer tone separately, pass only tone., TestInferEmotionalTone

### Community 80 - "Design"
Cohesion: 0.17
Nodes (11): 1. Sprite system, 2. Device shell and visual language, 3. Code changes, 4. Error handling, 5. Testing, Design, Goal, Out of scope (+3 more)

### Community 81 - "Person"
Cohesion: 0.03
Nodes (39): Person Management Submodule This submodule handles the AI's person…, Conversation, Message, Person, Any, datetime, Represents a single message in a conversation, Decay needs, emotions, lessons and goals by elapsed real time. (+31 more)

### Community 82 - "test_working_memory.py"
Cohesion: 0.12
Nodes (7): Tests for the working memory system., Needs can be plain floats (no level info) — defaults to level 1., Simulate multiple cycles and verify working memory evolves., TestFormatting, TestIntegration, TestSimpleNeeds, TestStats

### Community 83 - "test_simulation_runner.py"
Cohesion: 0.14
Nodes (5): HeadlessFixture, TestHeadlessParity, TestHeadlessProactive, TestPersonDict, TestSleepGate

### Community 84 - "Jenbina's Minecraft world"
Cohesion: 0.17
Nodes (12): Checking it by hand, Company, Jenbina's Minecraft world, Requirements, Run, Set up, once, Settings, The world's rules (+4 more)

### Community 85 - "TestOwnership"
Cohesion: 0.08
Nodes (3): TestBeats, TestOwnership, TestUnreadableState

### Community 86 - "test_minecraft_world.py"
Cohesion: 0.10
Nodes (17): build_scene(), place_label(), ``Home`` near her home position, otherwise the biome in plain words., Her own clock, split the way the Palo Alto world splits it., ``heard`` is what other players said since she last looked; ``can_talk`` is…, time_of_day(), get_world_state_summary(), Any (+9 more)

### Community 87 - "test_timeline.py"
Cohesion: 0.11
Nodes (31): format_duration(), lessons_text(), make_action(), make_gap(), make_goal(), make_mood(), make_plan(), make_sleep() (+23 more)

### Community 88 - "Emotion"
Cohesion: 0.18
Nodes (6): Emotion, datetime, Decay intensity toward base_intensity over time., Spike (or reduce) this emotion's intensity., Decay all emotions toward their baselines based on elapsed time., Represents a single emotion with intensity that decays toward a baseline.

### Community 89 - "The design"
Cohesion: 0.20
Nodes (10): Cost, Hearing, Her voice, Remembering, Seeing, Settings, Starting and stopping them, Talking (+2 more)

### Community 90 - ".record_social_action"
Cohesion: 0.25
Nodes (4): Record a chat-based interaction. Only the tone is stored — no message content…, Record a simulated social action (e.g. 'talk to neighbor'). The…, Generate a simple automatic sentiment string., Try to extract a person/entity name from a simulated action string. The action…

### Community 91 - "Minecraft world: Jenbina lives in a real place"
Cohesion: 0.22
Nodes (9): Anti-goals, Approaches, Goals, How it works today, Intent, Left to the builder, Minecraft world: Jenbina lives in a real place, Non-goals (+1 more)

### Community 92 - "HybridMemorySystem"
Cohesion: 0.10
Nodes (13): HybridMemorySystem, OpenAI embeddings client, built lazily so an API key is only needed once…, Initialize ChromaDB for semantic memory storage, Initialize Neo4j for relationship tracking, Initialize SQLite for chronological/time-series data, Store a memory event across all three databases Args: event: MemoryEvent object…, Generate a unique event ID, Store event in ChromaDB for semantic search (+5 more)

### Community 93 - "SocialInteraction"
Cohesion: 0.29
Nodes (4): Any, A single recorded social interaction. Only stores *who* Jenbina talked to,…, SocialInteraction, TestSocialInteraction

### Community 94 - "MaslowNeedsSystem"
Cohesion: 0.04
Nodes (53): Jenbina AGI System - Core Module This is the main core module for the Jenbina…, Needs Management Submodule This submodule handles all aspects of the AI's needs…, analyze_maslow_progress(), create_maslow_action_executor(), create_maslow_decision_chain(), create_maslow_goal_setter(), Create an action executor that can satisfy needs based on actions taken Args:…, Create a goal-setting system based on current needs and growth stage Args:… (+45 more)

### Community 95 - "env_line_html"
Cohesion: 0.33
Nodes (3): env_line_html(), ``Jenbina's House · Night · Clear skies, 15°C``; the bare home name when there…, TestTimelineAndRail

### Community 96 - "Review Focus"
Cohesion: 0.12
Nodes (15): Global Constraints, Review Focus, Task 10: The headless runner records the same events, Task 11: The home screen, and removal of the Chat page and dead renderers, Task 12: E2E tests, docs and the knowledge graph, Task 1: Events table in UserDatabase, Task 2: Event vocabulary, title builders and EventLog, Task 3: Recording helpers shared by both runners (+7 more)

### Community 97 - "EventLog"
Cohesion: 0.15
Nodes (8): EventLog, make_move(), Persists events through ``UserDatabase`` when it has a user, otherwise keeps…, Store ``event`` and return it. Never raises: a storage failure is printed and…, The most recent ``limit`` events, oldest first., A move, only when the location actually changed., record_move(), TestEventLog

### Community 98 - "bridge.js"
Cohesion: 0.11
Nodes (28): act(), { ACTIONS, stopMoving }, BRIDGE_PORT, BridgeError, { cleanLine, sayAndListen }, { createHearing }, { createSession }, hearing (+20 more)

### Community 99 - "generate_first_greeting"
Cohesion: 0.11
Nodes (13): generate_first_greeting(), Generate a personalized first greeting for a new user., TestGenerateFirstGreeting, Tests for generate_first_greeting., LLM response is returned for a new user with no dossier., Prompt for user without dossier mentions meeting for the first time., LLM response is returned for a new user with existing dossier., Prompt for user with dossier includes their data. (+5 more)

### Community 100 - "saved_state"
Cohesion: 0.44
Nodes (4): choose_user_to_adopt(), Choose the most experienced readable state, breaking ties by user id. Accounts…, saved_state(), TestChooseUser

### Community 101 - "make_needs"
Cohesion: 0.39
Nodes (3): make_needs(), Create needs dict with level info., TestFocusCalculation

### Community 104 - "render_needs_bars"
Cohesion: 0.12
Nodes (19): Streamlit session_state Persistence, Redraw mood, place, doing/goal lines, needs bars and emotion chips., Render Maslow needs as thin bars; a need below 30% is marked critical., Render the strongest emotions (above 15, at most four) as text chips; the…, Render a badge with Jenbina's dominant mood, styled positive or negative., render_emotion_chips(), render_mood_indicator(), render_needs_bars() (+11 more)

### Community 105 - "match_action_key"
Cohesion: 0.36
Nodes (3): match_action_key(), The need-satisfaction action key for a chosen action, or ``None``. Keywords…, TestActionKeywordMatch

### Community 106 - "Step"
Cohesion: 0.24
Nodes (8): decide(), effective_interval(), Choose one action without mutating the situation or consulting the clock., Step, asleep(), awake(), TestAsleep, TestAwake

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

### Community 111 - "Design"
Cohesion: 0.10
Nodes (19): 1. One owner, 2. One record, 3. The rhythm, 4. Sleep, 5. Lost time, 6. Chat, 7. Many people, one Jenbina, 8. The home screen (+11 more)

### Community 112 - "is_admin"
Cohesion: 0.19
Nodes (12): Jenbina — Admin Panel. Access restricted to: - Local requests (localhost /…, _hostname(), is_admin(), is_local_request(), The shared admin access check for the Admin page and heartbeat card., ``localhost`` from ``localhost:8501`` or ``http://localhost:8501``., Whether the request names this machine as its host. The Host and Origin headers…, Return True if the current visitor is allowed to see the admin panel. With… (+4 more)

### Community 113 - "FakeBridge"
Cohesion: 0.06
Nodes (7): FakeBridge, ProviderCase, Records every call; answers with whatever the test sets., Her world starts when she does and stops when she does., TestHostStartsAndStopsTheWorld, TestObserve, TestWorldWithALauncher

### Community 114 - "chat.py"
Cohesion: 0.12
Nodes (20): analyze_emotion_impact(), Analyze a situation and return emotion adjustments. Args: llm: Language model…, ChatTurn, check_return_greeting(), _get_user_db_and_id(), _get_user_display_name(), handle_user_input(), datetime (+12 more)

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

### Community 119 - "inject_pixel_css"
Cohesion: 0.15
Nodes (10): inject_pixel_css(), Inject the theme. Call once per page, right after ``st.set_page_config``.…, display_jenbina_image(), Show the painterly portrait for the state named by ``image_path``, unaltered in…, patch, TestChatHandlerAvatars, TestInjectCss, TestNavIcon (+2 more)

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
Nodes (47): _latest_world(), main(), Jenbina's home screen: a private conversation beside her shared live state., World and chosen action from the host's most recent moment. The world summary…, NotHostingError, RuntimeError, She is not (or no longer) living in this process., Jenbina — Console Log page. (+39 more)

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

### Community 136 - "TestMaslowNeed"
Cohesion: 0.11
Nodes (10): Test that satisfaction doesn't exceed 100 for regular needs, Test that self-actualization needs can grow beyond 100, Test critical status detection, Test low status detection, Test priority score calculation, Test individual MaslowNeed functionality, Test need initialization with correct values, Test need satisfaction decay over time (+2 more)

### Community 138 - ".get_daily_activity_suggestion"
Cohesion: 0.40
Nodes (4): any, datetime, Get locations that are currently open, Get a suggested activity based on current time and mood

### Community 139 - "art.py"
Cohesion: 0.33
Nodes (4): _frame(), FrameSpec, Pixel art for Jenbina, as palette-key strings. Every layer is ``(x, y, rows)``…, Palette for the pixel art. One character per color in the art strings. This…

### Community 140 - "test_privacy.py"
Cohesion: 0.35
Nodes (4): CapturingLLM, Private conversation content must stay out of another person's prompts., TestNothingCrossesBetweenPeople, two_people()

### Community 141 - "make_owner_id"
Cohesion: 0.24
Nodes (7): make_owner_id(), owner_is_dead(), _pid_namespace(), Identify the local PID namespace where the platform exposes it., Identify this host process and this particular attempt to host her., Only a missing PID in this machine's namespace proves an owner is dead., TestOwnerIdentity

### Community 143 - "build_timeline"
Cohesion: 0.13
Nodes (10): make_thought(), build_timeline(), first_sentence(), Render the rows in order; an empty list shows the empty-state marker., ``(first sentence, remainder)``; the whole text and ``""`` when it has no…, Merge chat messages and life events by time, apply the filter, keep the newest…, render_timeline(), TestBuildTimeline (+2 more)

### Community 144 - "test_pixel_ui.py"
Cohesion: 0.08
Nodes (28): _data_uri(), delta_badge_html(), dialog_html(), icon_html(), marker_html(), nav_icon_css(), The UI theme: the page CSS and the HTML helpers for timeline rows, markers, the…, The satisfaction badge ``83% → 85% (+1.7%)`` with data attributes for tests. (+20 more)

### Community 145 - "session.test.js"
Cohesion: 0.16
Nodes (9): createSession(), join(), start(), sessionEnded(), assert, { createSession }, fakeWorld(), world (+1 more)

### Community 148 - "fix_llm_json"
Cohesion: 0.19
Nodes (8): fix_llm_json(), Any, BaseLLM, Attempts to fix and parse JSON from LLM output that may be malformed. Args:…, patch, Tests for core/fix_llm_json.py — JSON repair utility., Tests for fix_llm_json function., TestFixLlmJson

### Community 151 - "hunt.test.js"
Cohesion: 0.20
Nodes (6): ACTIONS, { ACTIONS }, assert, { EventEmitter }, test, { Vec3 }

### Community 154 - "TestBasicNeedsBackwardCompatibility"
Cohesion: 0.13
Nodes (8): Test backward compatibility with BasicNeeds, Test BasicNeeds initialization, Test the needs property mapping, Test updating basic needs, Test satisfying basic needs, Test critical and low need detection, Test adding and removing needs, TestBasicNeedsBackwardCompatibility

### Community 155 - "render_sheet"
Cohesion: 0.43
Nodes (3): The 96x48 two-frame sheet for ``state``; unknown state raises KeyError., render_sheet(), TestEmotionSheets

### Community 156 - "TestHostLeavesTheWorld"
Cohesion: 0.15
Nodes (3): She is never left standing in a running world while asleep or stopped., True when another thread could take her mind right now., TestHostLeavesTheWorld

### Community 159 - "run.test.js"
Cohesion: 0.29
Nodes (6): assert, deps(), { DIED, runRoutine }, { EventEmitter }, options(), test

### Community 161 - ".waiting"
Cohesion: 0.21
Nodes (4): BaseCallbackHandler, _MindLockRelease, For the beat's own waits that are not a single LLM call on its thread, such as…, Lets go of the mind lock while a beat only waits for an LLM. A moment of her…

### Community 162 - "Any"
Cohesion: 0.18
Nodes (7): Any, datetime, Retrieve memories based on semantic similarity, Get all relationships and interactions for a person, Get memories within a time range, Get needs satisfaction history over time, Get statistics about the memory system

### Community 165 - "host.py"
Cohesion: 0.09
Nodes (25): SQLite user database for authentication and conversation persistence., adopt_existing(), AdoptionReport, _experience_count(), _import_partner(), datetime, Person, Adopt one existing mind and retain each account's own relationship with her. (+17 more)

### Community 166 - "run_chain_tests.py"
Cohesion: 0.09
Nodes (15): main(), Main function to run tests, Run all chain tests and return results, Run a specific test by name, run_chain_tests(), run_specific_test(), Test chains with realistic scenarios, Test chains in a stressful situation (+7 more)

### Community 167 - "MinecraftBridge"
Cohesion: 0.11
Nodes (10): MinecraftBridge, Any, Log her in if needed and return the observation., Log her out. Never raises: leaving must not break a beat., Run one bounded routine and return its outcome., Whisper one line to another player and wait for what they say back. Returns…, HTTPError, TestSay (+2 more)

### Community 169 - "test_sprites.py"
Cohesion: 0.13
Nodes (9): One 8x8 icon; unknown name raises KeyError., render_icon(), all_layers(), Tests for the pixel sprite pipeline (core.ui.sprites)., TestArtLayers, TestIcons, TestPalette, TestPortraits (+1 more)

### Community 170 - "SimpleEmbeddings"
Cohesion: 0.33
Nodes (4): Simple hash-based embeddings for when OpenAI is not available, Generate a simple hash-based embedding, Embed multiple documents, SimpleEmbeddings

### Community 174 - ".fresh"
Cohesion: 0.21
Nodes (3): Restore valid fields independently; old or malformed fields default., TestSituation, TestSavedWorldMemory

### Community 175 - "compose"
Cohesion: 0.36
Nodes (3): compose(), Draw ``layers`` in order onto a transparent RGBA canvas. A ``"."`` pixel leaves…, TestCompose

### Community 176 - "streamlit_server"
Cohesion: 0.28
Nodes (8): _free_port(), fixture, Shared fixtures for Playwright E2E tests., Return an available TCP port on localhost., Block until Streamlit is accepting connections., Launch Streamlit for the test session and tear it down afterwards. Yields the…, streamlit_server(), _wait_for_server()

### Community 177 - "build_env"
Cohesion: 0.25
Nodes (4): build_env(), A real Person with mock-LLM subsystems, a mock meta-cognitive system, and a…, TestHeadlessRunnerEvents, TestPlanCompletionEvents

### Community 183 - "world_from_env"
Cohesion: 0.29
Nodes (5): ``JENBINA_MINECRAFT_TALKS_PER_DAY``: a whole number of 0 or more, else the…, The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world., _talks_per_day(), world_from_env(), TestWorldFromEnv

### Community 190 - "within.test.js"
Cohesion: 0.40
Nodes (3): assert, test, { within }

## Ambiguous Edges - Review These
- `research_user()` → `query_llm_knowledge() (planned function)`  [AMBIGUOUS]
  docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md · relation: calls

## Knowledge Gaps
- **242 isolated node(s):** `{ goals }`, `{ Vec3 }`, `{ DIRECTIONS, bestTool }`, `{
  ANIMALS, CRAFT_WHITELIST, FOODS, PLAIN_NAME, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
}`, `FILLERS` (+237 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `research_user()` and `query_llm_knowledge() (planned function)`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **Why does `Person` connect `Person` to `InnerMonologueSystem`, `_make_mock_llm`, `choose_outreach_target`, `CLAUDE.md Project Instructions`, `MetaCognitiveSystem`, `.init_planning_system`, `SocialCognitionSystem`, `rail.py`, `test_privacy.py`, `InsightSystem`, `.voice`, `TestPerson`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `test_pixel_ui.py`, `SelfNarrativeSystem`, `memory/__init__.py`, `world_state.py`, `GoalSystem`, `PlanningSystem`, `TestMemoryIntegration`, `host.py`, `_invoke_and_parse`, `run_chain_tests.py`, `WorkingMemorySystem`, `MemoryIntegration`, `Goal`, `build_env`, `WorldState`, `SocialInteractionTracker`, `test_social_interaction_tracker.py`, `test_simulation_runner.py`, `TestOwnership`, `test_minecraft_world.py`, `MaslowNeedsSystem`, `saved_state`, `render_needs_bars`, `FakeBridge`, `chat.py`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **Why does `GoalSystem` connect `GoalSystem` to `PlanningSystem`, `CLAUDE.md Project Instructions`, `make_goal`, `Goal`, `LearningSystem`, `Person`, `Deep Emotional Mirror Implementation Plan`, `Plan`, `generate_return_greeting`, `.from_dict`, `make_mock_llm`, `MaslowNeedsSystem`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Jenbina README` connect `CLAUDE.md Project Instructions` to `InnerMonologueSystem`, `GoalSystem`, `MetaCognitiveSystem`, `EnvironmentSimulator`, `SocialCognitionSystem`, `InsightSystem`, `LearningSystem`, `Deep Emotional Mirror Implementation Plan`, `Person`, `SelfNarrativeSystem`, `EmotionSystem`, `WorldState`, `shared_init.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GoalSystem` (e.g. with `MaslowNeedsSystem` and `Jenbina README`) actually correct?**
  _`GoalSystem` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `WorkingMemorySystem` (e.g. with `Experience` and `MaslowNeedsSystem`) actually correct?**
  _`WorkingMemorySystem` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Person` (e.g. with `run_simulation()` and `adopt_existing()`) actually correct?**
  _`Person` has 40 INFERRED edges - model-reasoned connections that need verification._