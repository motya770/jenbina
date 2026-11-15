#!/usr/bin/env python3
"""Tests for the single headless simulation runner with every chain mocked."""

import json
import os
import sys
import unittest
from contextlib import ExitStack
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.person.person import Person
from core.heartbeat.rhythm import RhythmConfig
from core.timeline import EventLog

WORLD_JSON = json.dumps({"list_of_descriptions": [], "list_of_actions": ["Walk to Coupa Cafe"]})
ACTION = {"chosen_action": "Walk to Coupa Cafe for coffee", "reasoning": "social", "lessons_applied": ["go out"]}


def build_env(module):
    """A real Person with mock-LLM subsystems, a mock meta-cognitive system,
    and a context manager patching every chain factory in ``module``."""
    person = Person()
    person.update_all_needs()
    person.init_learning_system(MagicMock())
    person.init_goal_system(MagicMock())
    person.init_planning_system(MagicMock())
    person.init_social_cognition()
    person.init_self_narrative()
    person.init_curiosity_system()
    person.init_social_interaction_tracker()
    person.goal_system.should_generate = lambda: False
    thought = SimpleNamespace(content="Quiet tonight. Maybe text someone.", mode="deliberation")
    person.inner_monologue = SimpleNamespace(
        think=lambda **k: None,
        format_for_prompt=lambda: "[Inner voice — deliberation] Quiet tonight. Maybe text someone.",
        get_current_thought=lambda: thought,
    )
    meta = MagicMock()
    meta.get_meta_cognitive_stats.return_value = {
        "total_processes": 0, "total_insights": 0, "cognitive_biases": {}, "recent_insights": [],
    }
    patches = patch.multiple(
        module,
        create_basic_needs_chain=lambda llm, needs: {"action": "rest", "reasoning": "r"},
        create_world_description_system=lambda llm: (lambda person, world, recent_actions="": WORLD_JSON),
        create_meta_cognitive_action_chain=lambda **k: dict(ACTION),
        create_asimov_check_system=lambda llm: (lambda resp: {"compliant": True}),
        create_state_analysis_system=lambda llm, **k: {"ok": True},
        analyze_emotion_impact=lambda **k: {"joy": 8},
    )
    return person, meta, patches






class TestHeadlessRunnerEvents(unittest.TestCase):
    def test_headless_iteration_records_same_events(self):
        import core.simulation_runner as hr
        person, meta, patches = build_env(hr)
        log = EventLog()
        context = {"simulation_history": [], "jenbina_location": "Jenbina's House", "debug_iterations": [], "event_log": log}
        with patches, patch("core.simulation_runner.generate_proactive_message", return_value=None), \
                patch("core.simulation_runner.get_llm", return_value=MagicMock()):
            result = hr.run_single_iteration_headless(person, MagicMock(), meta, 0, context)
        kinds = [e.kind for e in log.recent()]
        self.assertEqual(kinds[:2], ["thought", "move"])
        self.assertIn("action", kinds)
        self.assertIn("mood", kinds)
        self.assertEqual(context["jenbina_location"], "Coupa Cafe")
        self.assertIn("satisfaction_delta", result)


def _plan_fixture(person):
    """Two plans: one finished earlier, one whose last step completes this
    iteration; a goal behind each."""
    from core.goals.goal_system import Goal
    from core.planning.planning_system import Plan, PlanStep
    old = Plan("old goal", 0, [PlanStep("done step", "", "", status="completed")], status="completed")
    new = Plan("new goal", 1, [PlanStep("call a friend", "", "", status="active")], status="active")
    person.planning_system.plans = [old, new]
    person.goal_system.goals = [Goal("old goal", "short_term", [], []), Goal("new goal", "short_term", [], [])]

    def finish_step(experience):
        new.steps[0].status = "completed"
        new.status = "completed"
        return "step_completed"

    person.planning_system.evaluate_step = finish_step
    person.planning_system.check_for_replan = lambda **k: None
    person.goal_system.update_progress = lambda experience: []


class TestPlanCompletionEvents(unittest.TestCase):
    def _assert_events(self, log):
        finished = [e.title for e in log.recent() if e.title.startswith("Plan finished")]
        self.assertEqual(finished, ["Plan finished: new goal"])
        self.assertIn("Plan step done: call a friend", [e.title for e in log.recent()])
        titles = [e.title for e in log.recent()]
        self.assertIn("Goal advanced: new goal → 30%", titles)
        self.assertNotIn("Goal advanced: old goal → 30%", titles)  # finished long ago: not credited again


    def test_headless_runner_records_plan_finished_once_and_goal_advanced(self):
        import core.simulation_runner as hr
        person, meta, patches = build_env(hr)
        _plan_fixture(person)
        log = EventLog()
        context = {"simulation_history": [], "jenbina_location": "Jenbina's House", "debug_iterations": [], "event_log": log}
        with patches, patch("core.simulation_runner.generate_proactive_message", return_value=None), \
                patch("core.simulation_runner.get_llm", return_value=MagicMock()):
            hr.run_single_iteration_headless(person, MagicMock(), meta, 0, context)
        self._assert_events(log)



RECORD = {
    "action_decision": {"chosen_action": "Walk to Coupa Cafe"},
    "world_summary": {
        "location": {"name": "Jenbina's House"},
        "time": {"time_of_day": "evening"},
        "weather": {"description": "Clear skies"},
    },
}


class TestPersonDict(unittest.TestCase):
    def test_person_dict_reports_the_real_esteem_and_growth_needs(self):
        import core.simulation_runner as hr
        needs = hr.get_person_dict(Person())["maslow_needs"]["individual_needs"]
        self.assertEqual(set(needs), {"hunger", "sleep", "security", "love", "self_esteem", "personal_growth"})


class TestActionKeywordMatch(unittest.TestCase):
    def test_keyword_must_be_a_whole_word(self):
        from core.simulation_runner import match_action_key
        self.assertEqual(match_action_key("Visit the Italian restaurant on University Avenue"), "socialize")
        self.assertIsNone(match_action_key("Teach chess at the library"))

    def test_inflections_and_stems_still_match(self):
        from core.simulation_runner import match_action_key
        self.assertEqual(match_action_key("Resting on the couch"), "rest")
        self.assertEqual(match_action_key("Go exploring the Baylands trails"), "learn_new_things")
        self.assertEqual(match_action_key("Meditation by the window"), "explore_meaning")

    def test_doubled_consonants_drop_e_and_agent_nouns_match(self):
        from core.simulation_runner import match_action_key
        self.assertEqual(match_action_key("Sitting by the bay"), "rest")
        self.assertEqual(match_action_key("Chatting with Matt"), "socialize")
        self.assertEqual(match_action_key("Planning the week"), "establish_routine")
        self.assertEqual(match_action_key("Stop at the visitor center"), "socialize")
        self.assertEqual(match_action_key("Join the readers club"), "learn_new_things")
        self.assertEqual(match_action_key("Exercising in the courtyard"), "maintain_health")
        self.assertEqual(match_action_key("Writing a poem"), "be_creative")
        self.assertEqual(match_action_key("Check the safety of the back door"), "find_safety")
        self.assertEqual(match_action_key("Look for something meaningful"), "explore_meaning")

    def test_whole_word_guard_survives_the_inflection_rules(self):
        from core.simulation_runner import match_action_key
        self.assertIsNone(match_action_key("Tour the construction site"))   # "sit" + e is not sitting
        self.assertIsNone(match_action_key("Plant seeds in the pot"))        # "plan" + t is not planning
        self.assertIsNone(match_action_key("Get ready for the day"))         # "read" + y is not reading


    def test_headless_runner_applies_the_shared_matcher(self):
        import core.simulation_runner as hr
        person, meta, patches = build_env(hr)
        person.maslow_needs.needs["sleep"].satisfaction = 10.0
        context = {"simulation_history": [], "jenbina_location": "Jenbina's House", "debug_iterations": [], "event_log": EventLog()}
        with patches, patch("core.simulation_runner.generate_proactive_message", return_value=None), \
                patch("core.simulation_runner.get_llm", return_value=MagicMock()), \
                patch("core.simulation_runner.match_action_key", return_value="sleep"):
            hr.run_single_iteration_headless(person, MagicMock(), meta, 0, context)
        self.assertGreater(person.maslow_needs.needs["sleep"].satisfaction, 60.0)


class HeadlessFixture(unittest.TestCase):
    def setUp(self):
        import core.simulation_runner as hr
        self.runner = hr
        self.person, self.meta, patches = build_env(hr)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patches)
        self.now = datetime(2026, 11, 15, 12, 0)
        self.person.suspend_until(self.now)
        self.stack.enter_context(patch.object(
            self.person, "update_all_needs",
            side_effect=lambda: Person.update_all_needs(self.person, now=self.now),
        ))
        clock = self.stack.enter_context(patch("core.simulation_runner.datetime"))
        clock.now.return_value = self.now
        self.world_summary = json.loads(json.dumps(RECORD["world_summary"]))
        self.world_summary["weather"]["temperature"] = 18.0
        self.stack.enter_context(patch("core.simulation_runner.create_comprehensive_world_state"))
        self.stack.enter_context(patch(
            "core.simulation_runner.get_world_state_summary", return_value=self.world_summary,
        ))
        self.action = self.stack.enter_context(patch(
            "core.simulation_runner.create_meta_cognitive_action_chain", return_value=dict(ACTION),
        ))
        self.check_triggers = self.stack.enter_context(patch(
            "core.simulation_runner._check_proactive_triggers",
            return_value={"low_social": {"need": "friendship", "satisfaction": 20}},
        ))
        self.generate = self.stack.enter_context(patch(
            "core.simulation_runner.generate_proactive_message", return_value="Still there?",
        ))
        self.get_llm = self.stack.enter_context(patch("core.simulation_runner.get_llm"))
        self.person.inner_monologue.think = MagicMock()
        self.context = {
            "simulation_history": [], "jenbina_location": "Jenbina's House",
            "debug_iterations": [], "event_log": EventLog(),
        }

    def run_iteration(self):
        return self.runner.run_single_iteration_headless(
            self.person, MagicMock(), self.meta, 0, self.context,
        )


class TestHeadlessParity(HeadlessFixture):
    def test_social_action_is_recorded_in_the_tracker(self):
        self.action.return_value = {"chosen_action": "Chat with the neighbor"}
        for emotion, tone in (
            ("joy", "warm"), ("sadness", "melancholic"), ("anger", "tense"),
            ("fear", "tense"), ("trust", "warm"), ("anticipation", "warm"),
            ("surprise", "neutral"),
        ):
            with self.subTest(emotion=emotion), patch.object(
                self.person.emotion_system, "get_dominant_emotions",
                return_value=[{"name": emotion, "intensity": 70}],
            ):
                result = self.run_iteration()
                interaction = self.person.social_interaction_tracker.interactions[-1]
                self.assertEqual(result["matched_action"], "socialize")
                self.assertEqual(interaction.interaction_type, "simulated_social")
                self.assertEqual(interaction.emotional_tone, tone)

    def test_social_day_reaches_the_monologue(self):
        self.person.social_interaction_tracker.record_chat("Ann", "warm")
        self.run_iteration()
        world_context = self.person.inner_monologue.think.call_args.kwargs["world_context_str"]
        self.assertIn("\nSocial interactions today", world_context)
        self.assertIn("Ann", world_context)
        self.assertIn("warm", world_context)

    def test_status_sink_gets_five_stages_and_may_fail(self):
        sink = MagicMock()
        self.context["status"] = sink
        stages = [
            call("sensing the world…"), call("thinking…"), call("deciding…"),
            call("reflecting…"), call("learning…"),
        ]
        self.run_iteration()
        self.assertEqual(sink.stage.call_args_list, stages)
        sink.reset_mock()
        sink.stage.side_effect = RuntimeError("display unavailable")
        self.assertIn("action_decision", self.run_iteration())
        self.assertEqual(sink.stage.call_args_list, stages)

    def test_debug_entry_includes_curiosity_and_social_interaction_stats(self):
        self.run_iteration()
        debug = self.context["debug_iterations"][-1]
        self.assertEqual(debug["curiosity_stats"], self.person.curiosity_system.get_stats())
        self.assertEqual(
            debug["social_interaction_stats"], self.person.social_interaction_tracker.get_stats(),
        )

    def test_optional_subsystems_and_an_unmatched_action_are_supported(self):
        self.person.social_interaction_tracker = None
        self.person.curiosity_system = None
        self.action.return_value = {"chosen_action": "Watch clouds"}
        result = self.run_iteration()
        self.assertIsNone(result["matched_action"])
        self.assertFalse(result["fell_asleep"])
        debug = self.context["debug_iterations"][-1]
        self.assertIsNone(debug["curiosity_stats"])
        self.assertIsNone(debug["social_interaction_stats"])


class TestSleepGate(HeadlessFixture):
    def setUp(self):
        super().setUp()
        self.action.return_value = {"chosen_action": "Go to bed and sleep"}
        self.world_summary["time"]["time_of_day"] = "night"
        self.person.maslow_needs.needs["sleep"].satisfaction = 60.0
        self.context["sleep_config"] = RhythmConfig()

    def test_sleep_at_night_is_not_an_instant_refill(self):
        health_before = self.person.maslow_needs.get_need_satisfaction("health")
        result = self.run_iteration()
        self.assertTrue(result["fell_asleep"])
        self.assertEqual(result["matched_action"], "sleep")
        self.assertLessEqual(self.person.maslow_needs.get_need_satisfaction("sleep"), 60.0)
        self.assertLessEqual(self.person.maslow_needs.get_need_satisfaction("health"), health_before)

    def test_daytime_sleep_is_a_nap_as_before(self):
        self.world_summary["time"]["time_of_day"] = "afternoon"
        result = self.run_iteration()
        self.assertFalse(result["fell_asleep"])
        self.assertEqual(result["matched_action"], "sleep")
        self.assertGreater(self.person.maslow_needs.get_need_satisfaction("sleep"), 60.0)

    def test_without_sleep_config_nothing_changes(self):
        del self.context["sleep_config"]
        result = self.run_iteration()
        self.assertFalse(result["fell_asleep"])
        self.assertGreater(self.person.maslow_needs.get_need_satisfaction("sleep"), 60.0)

    def test_low_sleep_need_during_the_day_uses_the_pre_action_value(self):
        self.world_summary["time"]["time_of_day"] = "afternoon"
        self.person.maslow_needs.needs["sleep"].satisfaction = 29.9
        result = self.run_iteration()
        self.assertTrue(result["fell_asleep"])
        self.assertLessEqual(self.person.maslow_needs.get_need_satisfaction("sleep"), 29.9)

    def test_disabling_sleep_keeps_the_instant_action_effect(self):
        self.context["sleep_config"] = RhythmConfig(sleep_enabled=False)
        result = self.run_iteration()
        self.assertFalse(result["fell_asleep"])
        self.assertGreater(self.person.maslow_needs.get_need_satisfaction("sleep"), 60.0)


class TestHeadlessProactive(HeadlessFixture):
    def test_message_goes_to_the_target_with_proactive_type(self):
        user_db = MagicMock()
        self.context.update(proactive_target=(7, "Ann"), user_db=user_db, user_id=9, display_name="Bob")
        result = self.run_iteration()
        self.check_triggers.assert_called_once_with(self.person, "Ann")
        self.assertEqual(self.generate.call_args.kwargs["display_name"], "Ann")
        message = self.person.conversations["Ann"].messages[-1]
        self.assertEqual((message.content, message.message_type), ("Still there?", "proactive"))
        self.assertNotIn("Bob", self.person.conversations)
        user_db.store_message.assert_called_once_with(7, "Jenbina", "Still there?", "proactive_message")
        self.assertEqual(self.person.social_cognition.get_or_create_model("Ann").last_proactive_at, self.now)
        self.assertEqual(result["proactive_sent_to"], "Ann")

    def test_no_target_means_no_proactive_check(self):
        self.context.update(display_name="Bob", user_id=9, user_db=MagicMock())
        result = self.run_iteration()
        self.check_triggers.assert_not_called()
        self.generate.assert_not_called()
        self.get_llm.assert_not_called()
        self.context["user_db"].store_message.assert_not_called()
        self.assertIsNone(result["proactive_sent_to"])

    def test_no_trigger_means_no_message(self):
        self.context["proactive_target"] = (7, "Ann")
        self.check_triggers.return_value = None
        result = self.run_iteration()
        self.generate.assert_not_called()
        self.get_llm.assert_not_called()
        self.assertIsNone(result["proactive_sent_to"])

    def test_empty_message_does_not_start_a_cooldown(self):
        self.context["proactive_target"] = (7, "Ann")
        self.generate.return_value = None
        result = self.run_iteration()
        self.assertIsNone(self.person.social_cognition.get_or_create_model("Ann").last_proactive_at)
        self.assertNotIn("Ann", self.person.conversations)
        self.assertIsNone(result["proactive_sent_to"])

    def test_proactive_message_gets_recent_actions_and_world_from_history(self):
        self.context.update(simulation_history=[dict(RECORD)], proactive_target=(7, "Ann"))
        self.run_iteration()
        self.generate.assert_called_once()
        self.assertEqual(self.generate.call_args.kwargs["recent_actions"], ["Walk to Coupa Cafe"])
        self.assertEqual(self.generate.call_args.kwargs["world_context"], "Jenbina's House, evening, Clear skies")
        self.assertEqual(self.person.conversations["Ann"].messages[-1].content, "Still there?")


if __name__ == "__main__":
    unittest.main()
