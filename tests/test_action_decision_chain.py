"""Tests for core/cognition/action_decision_chain.py."""

import json
import unittest
from unittest.mock import MagicMock, patch

from core.cognition.action_decision_chain import (
    _invoke_and_parse,
    create_action_decision_chain,
    ASSESS_PROMPT,
    DELIBERATE_PROMPT,
    DECIDE_PROMPT,
)


def _make_mock_llm(response_content: str = "{}"):
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content=response_content)
    return mock


class TestPromptTemplates(unittest.TestCase):
    """Tests for the prompt template definitions."""

    def test_assess_prompt_has_required_variables(self):
        expected_vars = {
            "hunger_satisfaction", "sleep_satisfaction", "safety_satisfaction",
            "overall_satisfaction", "emotional_state", "world_state_info",
            "current_plan_step", "learned_lessons", "current_goals",
            "working_memory", "inner_monologue", "self_narrative",
            "curiosity_context", "recent_actions",
        }
        self.assertEqual(set(ASSESS_PROMPT.input_variables), expected_vars)

    def test_deliberate_prompt_has_required_variables(self):
        expected = {"assessment", "actions", "descriptions"}
        self.assertEqual(set(DELIBERATE_PROMPT.input_variables), expected)

    def test_decide_prompt_has_required_variables(self):
        expected = {"assessment", "deliberation"}
        self.assertEqual(set(DECIDE_PROMPT.input_variables), expected)


class TestInvokeAndParse(unittest.TestCase):
    """Tests for the _invoke_and_parse helper."""

    def test_parses_valid_json_from_llm(self):
        llm = _make_mock_llm('{"key": "value"}')
        result = _invoke_and_parse(llm, "prompt text")
        self.assertEqual(result, {"key": "value"})

    @patch("core.cognition.action_decision_chain.fix_llm_json")
    def test_calls_fix_llm_json(self, mock_fix):
        llm = _make_mock_llm("broken json")
        mock_fix.return_value = {"fixed": True}
        result = _invoke_and_parse(llm, "prompt text")
        mock_fix.assert_called_once()
        self.assertEqual(result, {"fixed": True})

    @patch("core.cognition.action_decision_chain.fix_llm_json")
    def test_handles_string_response_from_fix(self, mock_fix):
        llm = _make_mock_llm("raw text")
        mock_fix.return_value = '{"parsed": true}'
        result = _invoke_and_parse(llm, "prompt text")
        self.assertEqual(result, {"parsed": True})

    def test_handles_response_without_content_attr(self):
        llm = MagicMock()
        # Return something without .content — will fall through to str()
        llm.invoke.return_value = "plain string response"
        with patch("core.cognition.action_decision_chain.fix_llm_json") as mock_fix:
            mock_fix.return_value = {"result": "ok"}
            result = _invoke_and_parse(llm, "prompt")
            self.assertEqual(result, {"result": "ok"})


class TestCreateActionDecisionChain(unittest.TestCase):
    """Tests for create_action_decision_chain."""

    def test_returns_callable(self):
        llm = _make_mock_llm()
        chain_fn = create_action_decision_chain(llm)
        self.assertTrue(callable(chain_fn))


if __name__ == "__main__":
    unittest.main()
