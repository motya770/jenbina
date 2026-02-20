"""Tests for core/connect.py — LLM provider connections."""

import os
import unittest
from unittest.mock import patch, MagicMock

from core.connect import (
    get_llm,
    get_json_llm,
    get_local_llm,
    get_sambanova_llm,
    get_recommended_llm,
    RECOMMENDED_CONFIGS,
)


class TestGetLlm(unittest.TestCase):
    """Tests for get_llm factory function."""

    @patch("core.connect.ChatOpenAI")
    def test_openai_provider(self, mock_chat):
        mock_chat.return_value = MagicMock()
        result = get_llm(provider="openai", temperature=0.5)
        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-5-nano")
        self.assertEqual(call_kwargs.kwargs["temperature"], 0.5)

    @patch("core.connect.ChatOpenAI")
    def test_openai_advanced_provider(self, mock_chat):
        mock_chat.return_value = MagicMock()
        result = get_llm(provider="openai-advanced", temperature=0)
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-5.2")

    @patch("core.connect.ChatOpenAI")
    def test_openai_with_max_tokens(self, mock_chat):
        mock_chat.return_value = MagicMock()
        get_llm(provider="openai", max_tokens=100)
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["max_tokens"], 100)

    @patch("core.connect.ChatOpenAI")
    def test_openai_without_max_tokens(self, mock_chat):
        mock_chat.return_value = MagicMock()
        get_llm(provider="openai")
        call_kwargs = mock_chat.call_args
        self.assertNotIn("max_tokens", call_kwargs.kwargs)

    @patch("core.connect.ChatOpenAI")
    def test_openai_advanced_with_max_tokens(self, mock_chat):
        mock_chat.return_value = MagicMock()
        get_llm(provider="openai-advanced", max_tokens=200)
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["max_tokens"], 200)

    @patch("core.connect.ChatOllama")
    def test_ollama_provider(self, mock_ollama):
        mock_ollama.return_value = MagicMock()
        get_llm(provider="ollama", temperature=0.7)
        mock_ollama.assert_called_once_with(
            model="llama3.2:3b-instruct-fp16", temperature=0.7
        )

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_llm(provider="unknown")
        self.assertIn("unknown", str(ctx.exception).lower())


class TestGetJsonLlm(unittest.TestCase):
    """Tests for get_json_llm factory function."""

    @patch("core.connect.ChatOpenAI")
    def test_openai_json_mode(self, mock_chat):
        mock_chat.return_value = MagicMock()
        get_json_llm(provider="openai", temperature=0)
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-5-nano")
        self.assertEqual(
            call_kwargs.kwargs["model_kwargs"],
            {"response_format": {"type": "json_object"}},
        )

    @patch("core.connect.ChatOpenAI")
    def test_openai_advanced_json_mode(self, mock_chat):
        mock_chat.return_value = MagicMock()
        get_json_llm(provider="openai-advanced")
        call_kwargs = mock_chat.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-5.2")

    @patch("core.connect.ChatOllama")
    def test_ollama_json_mode(self, mock_ollama):
        mock_ollama.return_value = MagicMock()
        get_json_llm(provider="ollama", temperature=0)
        mock_ollama.assert_called_once_with(
            model="llama3.2:3b-instruct-fp16", temperature=0, format="json"
        )

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            get_json_llm(provider="bad_provider")


class TestLegacyFunctions(unittest.TestCase):
    """Tests for backwards-compatibility functions."""

    @patch("core.connect.ChatOllama")
    def test_get_local_llm(self, mock_ollama):
        mock_ollama.return_value = MagicMock()
        get_local_llm()
        mock_ollama.assert_called_once()

    @patch("core.connect.get_llm")
    def test_get_sambanova_llm_calls_get_llm(self, mock_get_llm):
        get_sambanova_llm()
        mock_get_llm.assert_called_once_with(provider="sambanova")


class TestGetRecommendedLlm(unittest.TestCase):
    """Tests for get_recommended_llm."""

    def test_recommended_configs_has_expected_keys(self):
        for key in ("development", "production", "meta_cognition", "offline"):
            self.assertIn(key, RECOMMENDED_CONFIGS)

    @patch("core.connect.get_llm")
    def test_development_use_case(self, mock_get_llm):
        mock_get_llm.return_value = MagicMock()
        get_recommended_llm(use_case="development", temperature=0)
        mock_get_llm.assert_called_once_with(provider="openai", temperature=0)

    @patch("core.connect.get_llm")
    def test_meta_cognition_use_case(self, mock_get_llm):
        mock_get_llm.return_value = MagicMock()
        get_recommended_llm(use_case="meta_cognition")
        mock_get_llm.assert_called_once_with(provider="openai-advanced", temperature=0)

    @patch("core.connect.get_llm")
    def test_unknown_use_case_defaults_to_openai(self, mock_get_llm):
        mock_get_llm.return_value = MagicMock()
        get_recommended_llm(use_case="nonexistent")
        mock_get_llm.assert_called_once_with(provider="openai", temperature=0)


if __name__ == "__main__":
    unittest.main()
