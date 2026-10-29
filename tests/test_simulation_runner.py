#!/usr/bin/env python3
"""Tests for the simulation runners with every chain mocked: the Streamlit
runner (core.ui.simulation) drives the status rail and records events; the
headless runner (core.simulation_runner) records the same events."""

import json
import os
import sys
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.person.person import Person
from core.timeline import EventLog
from core.ui.rail import NullRail
from tests.test_greeting_generation import _FakeSessionState

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


def _session():
    return _FakeSessionState(simulation_history=[], jenbina_location="Jenbina's House", _proactive_llm=MagicMock())


class TestUiRunnerEvents(unittest.TestCase):
    def test_iteration_records_events_and_drives_rail(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        rail = MagicMock()
        log = EventLog()
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"):
            st.session_state = _session()
            result = sim.run_single_iteration(person, MagicMock(), meta, 0, rail=rail, event_log=log)
        kinds = [e.kind for e in log.recent()]
        self.assertEqual(kinds[:2], ["thought", "move"])
        self.assertIn("action", kinds)
        self.assertIn("mood", kinds)
        action = next(e for e in log.recent() if e.kind == "action")
        self.assertEqual(action.detail["location"], "Jenbina's House")
        self.assertEqual(action.detail["lessons"], ["go out"])
        self.assertEqual(st.session_state["jenbina_location"], "Coupa Cafe")
        self.assertIn("satisfaction_delta", result)
        self.assertTrue(any("completed in" in c.args[0] for c in rail.stage.call_args_list))
        self.assertEqual(rail.live_row.call_count, 2)
        st.success.assert_not_called()
        st.expander.assert_not_called()
        st.columns.assert_not_called()

    def test_iteration_survives_event_log_failure(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        db = MagicMock()
        db.store_event.side_effect = RuntimeError("disk")
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"):
            st.session_state = _session()
            result = sim.run_single_iteration(person, MagicMock(), meta, 0, rail=NullRail(), event_log=EventLog(db, 1))
        self.assertIn("action_decision", result)

    def test_loop_records_delta_and_history(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        with ExitStack() as stack:
            stack.enter_context(patches)
            st = stack.enter_context(patch("core.ui.simulation.st"))
            stack.enter_context(patch("core.ui.simulation.send_proactive_message"))
            stack.enter_context(patch("core.ui.simulation.time.sleep"))
            st.session_state = _session()
            results = sim.run_simulation_loop(person, MagicMock(), meta, 2, 0, rail=NullRail(), event_log=EventLog())
        self.assertEqual(len(st.session_state["simulation_history"]), 2)
        self.assertIn("satisfaction_delta", results[0])
        st.progress.assert_not_called()
        # What the chat reads afterwards: the latest world, decision and state analysis
        self.assertEqual(st.session_state["world_description"], WORLD_JSON)
        self.assertEqual(st.session_state["action_decision"]["chosen_action"], ACTION["chosen_action"])
        self.assertEqual(st.session_state["state_response"], {"ok": True})


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

    def test_ui_runner_records_plan_finished_once_and_goal_advanced(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        _plan_fixture(person)
        log = EventLog()
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"):
            st.session_state = _session()
            sim.run_single_iteration(person, MagicMock(), meta, 0, rail=NullRail(), event_log=log)
        self._assert_events(log)

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
        import core.ui.simulation as sim
        for module in (hr, sim):
            needs = module.get_person_dict(Person())["maslow_needs"]["individual_needs"]
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

    def test_ui_runner_applies_the_shared_matcher(self):
        import core.ui.simulation as sim
        person, meta, patches = build_env(sim)
        person.maslow_needs.needs["sleep"].satisfaction = 10.0
        with patches, patch("core.ui.simulation.st") as st, patch("core.ui.simulation.send_proactive_message"), \
                patch("core.ui.simulation.match_action_key", return_value="sleep"):
            st.session_state = _session()
            sim.run_single_iteration(person, MagicMock(), meta, 0, rail=NullRail(), event_log=EventLog())
        self.assertGreater(person.maslow_needs.needs["sleep"].satisfaction, 60.0)

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


class TestHeadlessProactiveContext(unittest.TestCase):
    def test_proactive_message_gets_recent_actions_and_world_from_history(self):
        import core.simulation_runner as hr
        person, meta, patches = build_env(hr)
        context = {"simulation_history": [dict(RECORD)], "jenbina_location": "Jenbina's House",
                   "debug_iterations": [], "event_log": EventLog(), "display_name": "Matt"}
        triggers = {"low_social": {"need": "love", "satisfaction": 20}}
        with patches, patch("core.simulation_runner._check_proactive_triggers", return_value=triggers), \
                patch("core.simulation_runner.generate_proactive_message", return_value="Still there?") as gen, \
                patch("core.simulation_runner.get_llm", return_value=MagicMock()):
            hr.run_single_iteration_headless(person, MagicMock(), meta, 0, context)
        gen.assert_called_once()
        self.assertEqual(gen.call_args.kwargs["recent_actions"], ["Walk to Coupa Cafe"])
        self.assertEqual(gen.call_args.kwargs["world_context"], "Jenbina's House, evening, Clear skies")
        self.assertEqual(person.conversations["Matt"].messages[-1].content, "Still there?")


if __name__ == "__main__":
    unittest.main()
