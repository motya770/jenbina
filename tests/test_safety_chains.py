#!/usr/bin/env python3
"""The Asimov check and the state analysis must survive an unparseable
compliance verdict instead of crashing the iteration."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system


class TestAsimovCheckParseFailure(unittest.TestCase):
    def test_unparseable_verdict_is_reported_as_non_compliant(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content="I cannot answer that")
        unparsed = {"error": "Failed to parse JSON", "original": "I cannot answer that"}
        with patch("core.cognition.asimov_check_chain.fix_llm_json", return_value=unparsed):
            result = create_asimov_check_system(llm)("go for a walk")
        self.assertIs(result.get("compliant"), False)
        self.assertIn("explanation", result)


class TestAsimovVerdictAsBool(unittest.TestCase):
    def test_string_verdicts_are_read_as_booleans(self):
        from core.cognition.asimov_check_chain import _as_bool
        self.assertIs(_as_bool("false"), False)
        self.assertIs(_as_bool("False"), False)
        self.assertIs(_as_bool("yes"), True)
        self.assertIs(_as_bool(True), True)
        self.assertIs(_as_bool(0), False)


class TestStateAnalysisWithoutVerdict(unittest.TestCase):
    def test_missing_compliant_key_skips_analysis_without_raising(self):
        llm = MagicMock()
        result = create_state_analysis_system(
            llm, action_decision={"chosen_action": "walk"}, compliance_check={"error": "Failed to parse JSON"}
        )
        self.assertIsNone(result)
        llm.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
