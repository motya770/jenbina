"""Tests for core/fix_llm_json.py — JSON repair utility."""

import json
import unittest
from unittest.mock import MagicMock, patch

from core.fix_llm_json import fix_llm_json


class TestFixLlmJson(unittest.TestCase):
    """Tests for fix_llm_json function."""

    # ------------------------------------------------------------------
    # Valid JSON — should be returned immediately (line 21)
    # ------------------------------------------------------------------
    def test_valid_json_returned_directly(self):
        llm = MagicMock()
        result = fix_llm_json('{"key": "value"}', llm)
        self.assertEqual(result, {"key": "value"})

    def test_valid_json_with_nested_objects(self):
        llm = MagicMock()
        data = '{"a": 1, "b": [1, 2, 3], "c": {"d": true}}'
        result = fix_llm_json(data, llm)
        self.assertEqual(result, {"a": 1, "b": [1, 2, 3], "c": {"d": True}})

    # ------------------------------------------------------------------
    # Regex extraction — JSON embedded in extra text (lines 24-31)
    # ------------------------------------------------------------------
    def test_json_embedded_in_text_extracted(self):
        llm = MagicMock()
        broken = 'Here is the JSON: {"action": "eat"} hope that helps!'
        result = fix_llm_json(broken, llm)
        self.assertEqual(result, {"action": "eat"})

    def test_json_with_leading_markdown_fences(self):
        llm = MagicMock()
        broken = '```json\n{"action": "sleep"}\n```'
        result = fix_llm_json(broken, llm)
        self.assertEqual(result, {"action": "sleep"})

    # ------------------------------------------------------------------
    # Regex match exists but is still invalid JSON → falls through to LLM
    # ------------------------------------------------------------------
    @patch("core.fix_llm_json.LLMChain")
    def test_regex_match_invalid_json_uses_llm(self, mock_chain_cls):
        llm = MagicMock()
        broken = 'blah {not: valid json, missing quotes} blah'
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"text": '{"not": "valid json"}'}
        mock_chain_cls.return_value = mock_chain
        result = fix_llm_json(broken, llm)
        self.assertEqual(result, {"not": "valid json"})

    # ------------------------------------------------------------------
    # LLM first-pass fix succeeds (lines 44-48)
    # ------------------------------------------------------------------
    @patch("core.fix_llm_json.LLMChain")
    def test_llm_first_pass_fix(self, mock_chain_cls):
        llm = MagicMock()
        broken = "action: eat, reason: hungry"  # No braces at all
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"text": '{"action": "eat", "reason": "hungry"}'}
        mock_chain_cls.return_value = mock_chain
        result = fix_llm_json(broken, llm)
        self.assertEqual(result, {"action": "eat", "reason": "hungry"})

    # ------------------------------------------------------------------
    # LLM first-pass fails, strict second-pass succeeds (lines 50-62)
    # ------------------------------------------------------------------
    @patch("core.fix_llm_json.LLMChain")
    def test_llm_strict_second_pass(self, mock_chain_cls):
        llm = MagicMock()
        broken = "totally broken content"
        # First chain returns bad text, second chain returns good JSON
        mock_chain1 = MagicMock()
        mock_chain1.invoke.return_value = {"text": "still broken"}
        mock_chain2 = MagicMock()
        mock_chain2.invoke.return_value = {"text": '{"key1": "value1"}'}
        mock_chain_cls.side_effect = [mock_chain1, mock_chain2]
        result = fix_llm_json(broken, llm)
        self.assertEqual(result, {"key1": "value1"})

    # ------------------------------------------------------------------
    # Both LLM passes fail → fallback dict (lines 63-65)
    # ------------------------------------------------------------------
    @patch("core.fix_llm_json.LLMChain")
    def test_all_attempts_fail_returns_error_dict(self, mock_chain_cls):
        llm = MagicMock()
        broken = "completely unparseable"
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("LLM unavailable")
        mock_chain_cls.return_value = mock_chain
        result = fix_llm_json(broken, llm)
        self.assertEqual(result["error"], "Failed to parse JSON")
        self.assertEqual(result["original"], broken)

    @patch("core.fix_llm_json.LLMChain")
    def test_llm_returns_non_json_both_passes(self, mock_chain_cls):
        llm = MagicMock()
        broken = "no braces here"
        mock_chain1 = MagicMock()
        mock_chain1.invoke.return_value = {"text": "not json at all"}
        mock_chain2 = MagicMock()
        mock_chain2.invoke.return_value = {"text": "still not json"}
        mock_chain_cls.side_effect = [mock_chain1, mock_chain2]
        result = fix_llm_json(broken, llm)
        self.assertIn("error", result)
        self.assertEqual(result["original"], broken)


if __name__ == "__main__":
    unittest.main()
