"""Tests for core/cognition/meta_cognition.py — MetaCognitiveSystem."""

import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from core.cognition.meta_cognition import (
    CognitiveProcess,
    MetaCognitiveInsight,
    MetaCognitiveSystem,
)


def _make_mock_llm(response_content: str = "{}"):
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content=response_content)
    return mock


class TestCognitiveProcess(unittest.TestCase):
    """Tests for the CognitiveProcess dataclass."""

    def test_creation(self):
        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={"need": "hunger"},
            output_data={"action": "eat"},
            reasoning_chain=["hungry", "find food", "eat"],
            confidence=0.8,
        )
        self.assertEqual(proc.process_type, "decision")
        self.assertEqual(proc.confidence, 0.8)
        self.assertIsNone(proc.meta_reflection)

    def test_optional_fields(self):
        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="reasoning",
            input_data={},
            output_data={},
            reasoning_chain=[],
            confidence=0.5,
            success_metrics={"accuracy": 0.9},
            meta_reflection="Was too hasty",
        )
        self.assertEqual(proc.success_metrics["accuracy"], 0.9)
        self.assertEqual(proc.meta_reflection, "Was too hasty")


class TestMetaCognitiveInsight(unittest.TestCase):
    """Tests for the MetaCognitiveInsight dataclass."""

    def test_creation(self):
        insight = MetaCognitiveInsight(
            insight_type="bias_detected",
            description="Anchoring to first option",
            confidence=0.7,
            suggested_improvement="Consider multiple options",
        )
        self.assertEqual(insight.insight_type, "bias_detected")
        self.assertIsNotNone(insight.created_at)


class TestMetaCognitiveSystem(unittest.TestCase):
    """Tests for MetaCognitiveSystem."""

    def setUp(self):
        self.llm = _make_mock_llm()
        self.system = MetaCognitiveSystem(self.llm)

    def test_initialization(self):
        self.assertEqual(len(self.system.cognitive_history), 0)
        self.assertEqual(len(self.system.insights), 0)
        self.assertIn("confirmation_bias", self.system.cognitive_biases)
        self.assertEqual(self.system.cognitive_biases["confirmation_bias"], 0.0)

    def test_monitor_cognitive_process(self):
        proc = self.system.monitor_cognitive_process(
            process_type="decision",
            input_data={"need": "hunger"},
            output_data={"action": "eat"},
            reasoning_chain=["hungry", "should eat"],
            confidence=0.85,
        )
        self.assertIsInstance(proc, CognitiveProcess)
        self.assertEqual(len(self.system.cognitive_history), 1)
        self.assertEqual(proc.confidence, 0.85)

    def test_reflect_on_process_success(self):
        reflection_json = json.dumps({
            "insight_type": "good_reasoning",
            "description": "Sound decision process",
            "confidence": 0.9,
            "suggested_improvement": "None needed",
            "bias_detected": "confirmation_bias",
            "reasoning_quality": "excellent",
        })
        self.llm = _make_mock_llm(reflection_json)
        self.system = MetaCognitiveSystem(self.llm)

        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={"need": "hunger"},
            output_data={"action": "eat"},
            reasoning_chain=["hungry", "find food"],
            confidence=0.8,
        )

        insight = self.system.reflect_on_process(proc)
        self.assertIsNotNone(insight)
        self.assertIsInstance(insight, MetaCognitiveInsight)
        self.assertEqual(insight.insight_type, "good_reasoning")
        self.assertEqual(len(self.system.insights), 1)
        # confirmation_bias should be incremented
        self.assertAlmostEqual(self.system.cognitive_biases["confirmation_bias"], 0.1)

    def test_reflect_on_process_with_list_bias(self):
        reflection_json = json.dumps({
            "insight_type": "bias_detected",
            "description": "Multiple biases found",
            "confidence": 0.7,
            "suggested_improvement": "Slow down",
            "bias_detected": ["confirmation_bias", "anchoring_bias"],
        })
        self.llm = _make_mock_llm(reflection_json)
        self.system = MetaCognitiveSystem(self.llm)

        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={},
            output_data={},
            reasoning_chain=["step1"],
            confidence=0.5,
        )

        insight = self.system.reflect_on_process(proc)
        self.assertIsNotNone(insight)
        self.assertAlmostEqual(self.system.cognitive_biases["confirmation_bias"], 0.1)
        self.assertAlmostEqual(self.system.cognitive_biases["anchoring_bias"], 0.1)

    def test_reflect_on_process_unknown_bias_ignored(self):
        reflection_json = json.dumps({
            "insight_type": "bias_detected",
            "description": "Unknown bias",
            "confidence": 0.6,
            "suggested_improvement": "Be careful",
            "bias_detected": "nonexistent_bias",
        })
        self.llm = _make_mock_llm(reflection_json)
        self.system = MetaCognitiveSystem(self.llm)

        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={},
            output_data={},
            reasoning_chain=[],
            confidence=0.5,
        )

        insight = self.system.reflect_on_process(proc)
        self.assertIsNotNone(insight)
        # All biases should remain at 0
        for v in self.system.cognitive_biases.values():
            self.assertEqual(v, 0.0)

    def test_reflect_on_process_json_with_extra_text(self):
        response_text = 'Here is my analysis:\n{"insight_type": "strategy_improvement", "description": "Could improve", "confidence": 0.8, "suggested_improvement": "Try harder"}\nEnd.'
        self.llm = _make_mock_llm(response_text)
        self.system = MetaCognitiveSystem(self.llm)

        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="reasoning",
            input_data={},
            output_data={},
            reasoning_chain=["thought"],
            confidence=0.7,
        )

        insight = self.system.reflect_on_process(proc)
        self.assertIsNotNone(insight)
        self.assertEqual(insight.insight_type, "strategy_improvement")

    def test_reflect_on_process_llm_failure_returns_none(self):
        self.llm.invoke.side_effect = Exception("LLM unavailable")
        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={},
            output_data={},
            reasoning_chain=[],
            confidence=0.5,
        )
        insight = self.system.reflect_on_process(proc)
        self.assertIsNone(insight)

    def test_reflect_on_process_with_non_string_reasoning_items(self):
        reflection_json = json.dumps({
            "insight_type": "good_reasoning",
            "description": "OK",
            "confidence": 0.8,
            "suggested_improvement": "None",
        })
        self.llm = _make_mock_llm(reflection_json)
        self.system = MetaCognitiveSystem(self.llm)

        proc = CognitiveProcess(
            timestamp=datetime.now(),
            process_type="decision",
            input_data={},
            output_data={},
            reasoning_chain=["string step", 42, ["nested", "list"]],
            confidence=0.6,
        )
        insight = self.system.reflect_on_process(proc)
        self.assertIsNotNone(insight)

    def test_analyze_cognitive_patterns_insufficient_data(self):
        result = self.system.analyze_cognitive_patterns()
        self.assertIn("message", result)
        self.assertIn("Not enough data", result["message"])

    def test_analyze_cognitive_patterns_with_data(self):
        pattern_json = json.dumps({
            "recurring_biases": ["confirmation_bias"],
            "successful_patterns": ["careful analysis"],
            "confidence_issues": "none",
            "improvement_areas": ["speed"],
            "overall_cognitive_health": "good",
        })
        self.llm = _make_mock_llm(pattern_json)
        self.system = MetaCognitiveSystem(self.llm)

        # Add 3+ processes
        for i in range(4):
            self.system.monitor_cognitive_process(
                process_type="decision",
                input_data={"i": i},
                output_data={"action": f"act_{i}"},
                reasoning_chain=[f"step {i}"],
                confidence=0.7 + i * 0.05,
            )

        result = self.system.analyze_cognitive_patterns()
        self.assertIn("recurring_biases", result)

    def test_analyze_cognitive_patterns_llm_failure(self):
        self.llm.invoke.side_effect = Exception("fail")
        for i in range(3):
            self.system.monitor_cognitive_process(
                process_type="test", input_data={}, output_data={},
                reasoning_chain=[], confidence=0.5,
            )
        result = self.system.analyze_cognitive_patterns()
        self.assertIn("error", result)

    def test_suggest_thinking_strategy_success(self):
        strategy_json = json.dumps({
            "strategies": ["slow down", "seek counter-evidence"],
            "bias_mitigation": "awareness",
            "reasoning_approach": "systematic",
            "confidence_calibration": "moderate",
        })
        self.llm = _make_mock_llm(strategy_json)
        self.system = MetaCognitiveSystem(self.llm)

        result = self.system.suggest_thinking_strategy({"scenario": "complex decision"})
        self.assertIn("strategies", result)

    def test_suggest_thinking_strategy_failure(self):
        self.llm.invoke.side_effect = Exception("fail")
        result = self.system.suggest_thinking_strategy({"scenario": "test"})
        self.assertIn("error", result)

    def test_get_meta_cognitive_stats(self):
        self.system.monitor_cognitive_process(
            process_type="decision",
            input_data={},
            output_data={},
            reasoning_chain=[],
            confidence=0.8,
        )
        stats = self.system.get_meta_cognitive_stats()
        self.assertEqual(stats["total_processes"], 1)
        self.assertEqual(stats["total_insights"], 0)
        self.assertIn("cognitive_biases", stats)


if __name__ == "__main__":
    unittest.main()
