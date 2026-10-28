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


if __name__ == "__main__":
    unittest.main()
