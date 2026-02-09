#!/usr/bin/env python3
"""
Unit tests for the learning system.
Tests Experience, Lesson, and LearningSystem (recording, reinforcement,
decay, serialization, formatting, and LLM-based lesson extraction).
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.learning.learning_system import (
    Experience,
    Lesson,
    LearningSystem,
    LESSON_EXTRACTION_PROMPT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_experience(
    action="eat food",
    reasoning="hungry",
    needs_before=None,
    needs_after=None,
    emotions_before=None,
    emotions_after=None,
    world_context=None,
    satisfaction_before=50.0,
    satisfaction_after=60.0,
) -> dict:
    """Return kwargs dict suitable for LearningSystem.record_experience()."""
    return dict(
        action_taken=action,
        action_reasoning=reasoning,
        needs_before=needs_before or {"hunger": 30.0, "sleep": 70.0},
        needs_after=needs_after or {"hunger": 60.0, "sleep": 68.0},
        emotions_before=emotions_before or {"joy": 40.0, "sadness": 20.0},
        emotions_after=emotions_after or {"joy": 55.0, "sadness": 15.0},
        world_context=world_context or {"time_of_day": "morning", "weather": "sunny"},
        overall_satisfaction_before=satisfaction_before,
        overall_satisfaction_after=satisfaction_after,
    )


def make_mock_llm(response_text='[{"description":"test","category":"action_outcome","condition":"always","recommended_action":"do nothing"}]'):
    """Create a mock LLM that returns a fixed response."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_text
    mock_llm.invoke.return_value = mock_response
    return mock_llm


# ===================================================================
# Experience tests
# ===================================================================

class TestExperience(unittest.TestCase):
    """Test Experience dataclass"""

    def setUp(self):
        self.experience = Experience(
            action_taken="eat food",
            action_reasoning="hunger is low",
            needs_before={"hunger": 30.0, "sleep": 70.0},
            needs_after={"hunger": 60.0, "sleep": 68.0},
            needs_delta={"hunger": 30.0, "sleep": -2.0},
            emotions_before={"joy": 40.0},
            emotions_after={"joy": 55.0},
            emotions_delta={"joy": 15.0},
            world_context={"time_of_day": "morning"},
            overall_satisfaction_before=50.0,
            overall_satisfaction_after=65.0,
        )

    def test_initialization(self):
        """Test experience stores all fields"""
        self.assertEqual(self.experience.action_taken, "eat food")
        self.assertEqual(self.experience.action_reasoning, "hunger is low")
        self.assertEqual(self.experience.needs_before["hunger"], 30.0)
        self.assertEqual(self.experience.needs_after["hunger"], 60.0)
        self.assertEqual(self.experience.needs_delta["hunger"], 30.0)
        self.assertEqual(self.experience.overall_satisfaction_before, 50.0)
        self.assertEqual(self.experience.overall_satisfaction_after, 65.0)

    def test_to_dict(self):
        """Test serialization to dict"""
        d = self.experience.to_dict()
        self.assertEqual(d["action_taken"], "eat food")
        self.assertEqual(d["needs_delta"]["hunger"], 30.0)
        self.assertIn("timestamp", d)

    def test_from_dict_roundtrip(self):
        """Test that from_dict(to_dict()) preserves data"""
        d = self.experience.to_dict()
        restored = Experience.from_dict(d)

        self.assertEqual(restored.action_taken, self.experience.action_taken)
        self.assertEqual(restored.needs_before, self.experience.needs_before)
        self.assertEqual(restored.needs_after, self.experience.needs_after)
        self.assertEqual(restored.needs_delta, self.experience.needs_delta)
        self.assertEqual(restored.emotions_delta, self.experience.emotions_delta)
        self.assertAlmostEqual(
            restored.overall_satisfaction_before,
            self.experience.overall_satisfaction_before,
        )

    def test_timestamp_auto_set(self):
        """Test that timestamp is auto-set"""
        before = time.time()
        exp = Experience(
            action_taken="x", action_reasoning="y",
            needs_before={}, needs_after={}, needs_delta={},
            emotions_before={}, emotions_after={}, emotions_delta={},
        )
        after = time.time()
        self.assertGreaterEqual(exp.timestamp, before)
        self.assertLessEqual(exp.timestamp, after)

    def test_default_world_context(self):
        """Test that world_context defaults to empty dict"""
        exp = Experience(
            action_taken="x", action_reasoning="y",
            needs_before={}, needs_after={}, needs_delta={},
            emotions_before={}, emotions_after={}, emotions_delta={},
        )
        self.assertEqual(exp.world_context, {})


# ===================================================================
# Lesson tests
# ===================================================================

class TestLesson(unittest.TestCase):
    """Test Lesson dataclass"""

    def setUp(self):
        self.lesson = Lesson(
            description="Eating when hungry improves satisfaction",
            category="action_outcome",
            condition="hunger below 40%",
            recommended_action="eat food",
            confidence=0.5,
        )

    def test_initialization(self):
        """Test lesson stores all fields"""
        self.assertEqual(self.lesson.description, "Eating when hungry improves satisfaction")
        self.assertEqual(self.lesson.category, "action_outcome")
        self.assertEqual(self.lesson.condition, "hunger below 40%")
        self.assertEqual(self.lesson.recommended_action, "eat food")
        self.assertEqual(self.lesson.confidence, 0.5)
        self.assertEqual(self.lesson.times_confirmed, 0)
        self.assertEqual(self.lesson.times_contradicted, 0)

    def test_reinforce(self):
        """Test that reinforce increases confidence and confirm count"""
        initial_confidence = self.lesson.confidence
        self.lesson.reinforce()

        self.assertEqual(self.lesson.times_confirmed, 1)
        self.assertAlmostEqual(self.lesson.confidence, initial_confidence + 0.1)

    def test_reinforce_caps_at_one(self):
        """Test that confidence doesn't exceed 1.0"""
        self.lesson.confidence = 0.95
        self.lesson.reinforce()
        self.assertEqual(self.lesson.confidence, 1.0)

    def test_contradict(self):
        """Test that contradict decreases confidence"""
        initial_confidence = self.lesson.confidence
        self.lesson.contradict()

        self.assertEqual(self.lesson.times_contradicted, 1)
        self.assertAlmostEqual(self.lesson.confidence, initial_confidence - 0.15)

    def test_contradict_floors_at_zero(self):
        """Test that confidence doesn't go below 0.0"""
        self.lesson.confidence = 0.1
        self.lesson.contradict()
        self.assertEqual(self.lesson.confidence, 0.0)

    def test_decay(self):
        """Test that decay reduces confidence over time"""
        initial = self.lesson.confidence
        self.lesson.decay(hours=2.0)
        # 0.01 * 2 = 0.02 reduction
        self.assertAlmostEqual(self.lesson.confidence, initial - 0.02)

    def test_decay_floors_at_zero(self):
        """Test decay doesn't go below 0"""
        self.lesson.confidence = 0.01
        self.lesson.decay(hours=10.0)
        self.assertEqual(self.lesson.confidence, 0.0)

    def test_is_active(self):
        """Test active threshold at 0.15"""
        self.lesson.confidence = 0.20
        self.assertTrue(self.lesson.is_active())

        self.lesson.confidence = 0.15
        self.assertFalse(self.lesson.is_active())

        self.lesson.confidence = 0.10
        self.assertFalse(self.lesson.is_active())

    def test_to_dict(self):
        """Test serialization"""
        d = self.lesson.to_dict()
        self.assertEqual(d["description"], self.lesson.description)
        self.assertEqual(d["category"], self.lesson.category)
        self.assertEqual(d["confidence"], self.lesson.confidence)
        self.assertIn("last_confirmed", d)

    def test_from_dict_roundtrip(self):
        """Test from_dict(to_dict()) preserves data"""
        self.lesson.reinforce()
        self.lesson.reinforce()
        self.lesson.contradict()

        d = self.lesson.to_dict()
        restored = Lesson.from_dict(d)

        self.assertEqual(restored.description, self.lesson.description)
        self.assertEqual(restored.confidence, self.lesson.confidence)
        self.assertEqual(restored.times_confirmed, 2)
        self.assertEqual(restored.times_contradicted, 1)

    def test_reinforce_updates_last_confirmed(self):
        """Test that reinforce updates the last_confirmed timestamp"""
        before = self.lesson.last_confirmed
        time.sleep(0.01)  # small delay
        self.lesson.reinforce()
        self.assertGreaterEqual(self.lesson.last_confirmed, before)


# ===================================================================
# LearningSystem tests
# ===================================================================

class TestLearningSystem(unittest.TestCase):
    """Test LearningSystem without LLM (unit-level)"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)

    def test_initialization(self):
        """Test system initializes with empty state"""
        self.assertEqual(len(self.system.experiences), 0)
        self.assertEqual(len(self.system.lessons), 0)
        self.assertEqual(self.system._experience_count_since_extraction, 0)

    def test_record_experience(self):
        """Test recording a single experience"""
        kwargs = make_experience()
        exp = self.system.record_experience(**kwargs)

        self.assertEqual(len(self.system.experiences), 1)
        self.assertEqual(exp.action_taken, "eat food")
        self.assertIn("hunger", exp.needs_delta)

    def test_record_experience_calculates_deltas(self):
        """Test that deltas are computed correctly"""
        kwargs = make_experience(
            needs_before={"hunger": 30.0, "sleep": 70.0},
            needs_after={"hunger": 55.0, "sleep": 65.0},
        )
        exp = self.system.record_experience(**kwargs)

        self.assertAlmostEqual(exp.needs_delta["hunger"], 25.0)
        self.assertAlmostEqual(exp.needs_delta["sleep"], -5.0)

    def test_record_experience_calculates_emotion_deltas(self):
        """Test emotion delta computation"""
        kwargs = make_experience(
            emotions_before={"joy": 40.0, "fear": 30.0},
            emotions_after={"joy": 60.0, "fear": 10.0},
        )
        exp = self.system.record_experience(**kwargs)

        self.assertAlmostEqual(exp.emotions_delta["joy"], 20.0)
        self.assertAlmostEqual(exp.emotions_delta["fear"], -20.0)

    def test_max_experiences_cap(self):
        """Test that experiences are capped at MAX_EXPERIENCES"""
        self.system.LESSON_EXTRACTION_INTERVAL = 999  # prevent extraction
        for i in range(150):
            self.system.record_experience(**make_experience(action=f"action_{i}"))

        self.assertEqual(len(self.system.experiences), LearningSystem.MAX_EXPERIENCES)
        # Should keep the most recent
        self.assertEqual(self.system.experiences[-1].action_taken, "action_149")

    def test_extraction_triggered_at_interval(self):
        """Test that extract_lessons is called every LESSON_EXTRACTION_INTERVAL experiences"""
        self.system.LESSON_EXTRACTION_INTERVAL = 3

        # Record 2 experiences — no extraction yet
        self.system.record_experience(**make_experience(action="a1"))
        self.system.record_experience(**make_experience(action="a2"))
        self.mock_llm.invoke.assert_not_called()

        # 3rd experience triggers extraction
        self.system.record_experience(**make_experience(action="a3"))
        self.mock_llm.invoke.assert_called_once()

    def test_extraction_counter_resets(self):
        """Test that the counter resets after extraction"""
        self.system.LESSON_EXTRACTION_INTERVAL = 2
        self.system.record_experience(**make_experience(action="a1"))
        self.system.record_experience(**make_experience(action="a2"))

        # Counter should have reset
        self.assertEqual(self.system._experience_count_since_extraction, 0)

    def test_default_world_context(self):
        """Test that world_context defaults to empty dict"""
        exp = self.system.record_experience(
            action_taken="walk",
            action_reasoning="bored",
            needs_before={"hunger": 50.0},
            needs_after={"hunger": 48.0},
            emotions_before={"joy": 30.0},
            emotions_after={"joy": 35.0},
        )
        self.assertEqual(exp.world_context, {})


class TestLearningSystemReinforcement(unittest.TestCase):
    """Test lesson reinforcement and contradiction"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)
        # Manually add a lesson
        self.system.lessons.append(Lesson(
            description="Eating improves mood",
            category="action_outcome",
            condition="hunger below 40%",
            recommended_action="eat food",
            confidence=0.5,
        ))

    def test_reinforce_on_positive_outcome(self):
        """Matching action with positive satisfaction should reinforce"""
        exp = self.system.record_experience(
            **make_experience(
                action="eat food",
                satisfaction_before=50.0,
                satisfaction_after=60.0,
            )
        )
        self.assertEqual(self.system.lessons[0].times_confirmed, 1)
        self.assertAlmostEqual(self.system.lessons[0].confidence, 0.6)

    def test_contradict_on_negative_outcome(self):
        """Matching action with negative satisfaction should contradict"""
        exp = self.system.record_experience(
            **make_experience(
                action="eat food",
                satisfaction_before=60.0,
                satisfaction_after=55.0,
            )
        )
        self.assertEqual(self.system.lessons[0].times_contradicted, 1)
        self.assertAlmostEqual(self.system.lessons[0].confidence, 0.35)

    def test_no_effect_on_unrelated_action(self):
        """Unrelated action should not affect lesson confidence"""
        exp = self.system.record_experience(
            **make_experience(
                action="go for a walk",
                satisfaction_before=50.0,
                satisfaction_after=60.0,
            )
        )
        self.assertEqual(self.system.lessons[0].times_confirmed, 0)
        self.assertEqual(self.system.lessons[0].times_contradicted, 0)
        self.assertAlmostEqual(self.system.lessons[0].confidence, 0.5)

    def test_inactive_lessons_skipped(self):
        """Inactive lessons should not be reinforced or contradicted"""
        self.system.lessons[0].confidence = 0.10  # Below threshold
        exp = self.system.record_experience(
            **make_experience(
                action="eat food",
                satisfaction_before=50.0,
                satisfaction_after=60.0,
            )
        )
        self.assertEqual(self.system.lessons[0].times_confirmed, 0)

    def test_partial_action_match(self):
        """Recommended action substring in action_taken should match"""
        self.system.lessons[0].recommended_action = "eat"
        exp = self.system.record_experience(
            **make_experience(
                action="eat a large meal",
                satisfaction_before=50.0,
                satisfaction_after=70.0,
            )
        )
        self.assertEqual(self.system.lessons[0].times_confirmed, 1)


class TestLearningSystemDecay(unittest.TestCase):
    """Test lesson decay and pruning"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)
        self.system.lessons = [
            Lesson("L1", "action_outcome", "c1", "a1", confidence=0.5),
            Lesson("L2", "emotional_pattern", "c2", "a2", confidence=0.20),
            Lesson("L3", "environmental", "c3", "a3", confidence=0.16),
        ]

    def test_decay_reduces_confidence(self):
        """All lessons should lose confidence"""
        self.system.decay_all_lessons(hours=1.0)
        # Each loses 0.01 * 1 = 0.01
        self.assertAlmostEqual(self.system.lessons[0].confidence, 0.49)

    def test_decay_prunes_inactive(self):
        """Lessons at or below threshold are removed"""
        # L3 at 0.16, after 1 hour decay (0.01) → 0.15 → not active
        self.system.decay_all_lessons(hours=1.0)
        active_names = [l.description for l in self.system.lessons]
        self.assertIn("L1", active_names)
        self.assertIn("L2", active_names)
        self.assertNotIn("L3", active_names)

    def test_heavy_decay_prunes_multiple(self):
        """Heavy decay should prune all low-confidence lessons"""
        self.system.decay_all_lessons(hours=20.0)
        # L1: 0.5 - 0.2 = 0.3 → active
        # L2: 0.2 - 0.2 = 0.0 → pruned
        # L3: already pruned
        self.assertEqual(len(self.system.lessons), 1)
        self.assertEqual(self.system.lessons[0].description, "L1")

    def test_zero_hours_no_change(self):
        """Zero hours decay should not change anything"""
        before = [l.confidence for l in self.system.lessons]
        self.system.decay_all_lessons(hours=0.0)
        after = [l.confidence for l in self.system.lessons]
        self.assertEqual(before, after)


class TestLearningSystemFormatting(unittest.TestCase):
    """Test format_lessons_for_prompt"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)

    def test_empty_lessons(self):
        """No lessons should return default message"""
        result = self.system.format_lessons_for_prompt()
        self.assertEqual(result, "No lessons learned yet.")

    def test_active_lessons_formatted(self):
        """Active lessons should appear in formatted text"""
        self.system.lessons = [
            Lesson("Eating helps", "action_outcome", "hungry", "eat", confidence=0.8),
            Lesson("Sleep heals", "action_outcome", "tired", "sleep", confidence=0.6),
        ]
        result = self.system.format_lessons_for_prompt()

        self.assertIn("Eating helps", result)
        self.assertIn("Sleep heals", result)
        self.assertIn("action_outcome", result)

    def test_sorted_by_confidence(self):
        """Lessons should be sorted by confidence descending"""
        self.system.lessons = [
            Lesson("Low conf", "action_outcome", "c", "a", confidence=0.3),
            Lesson("High conf", "action_outcome", "c", "a", confidence=0.9),
            Lesson("Mid conf", "action_outcome", "c", "a", confidence=0.6),
        ]
        result = self.system.format_lessons_for_prompt()
        lines = result.strip().split("\n")

        self.assertIn("High conf", lines[0])
        self.assertIn("Mid conf", lines[1])
        self.assertIn("Low conf", lines[2])

    def test_inactive_lessons_excluded(self):
        """Inactive lessons should not appear"""
        self.system.lessons = [
            Lesson("Active", "action_outcome", "c", "a", confidence=0.5),
            Lesson("Inactive", "action_outcome", "c", "a", confidence=0.10),
        ]
        result = self.system.format_lessons_for_prompt()

        self.assertIn("Active", result)
        self.assertNotIn("Inactive", result)

    def test_max_ten_lessons(self):
        """Should show at most 10 lessons"""
        self.system.lessons = [
            Lesson(f"Lesson {i}", "action_outcome", "c", "a", confidence=0.5)
            for i in range(15)
        ]
        result = self.system.format_lessons_for_prompt()
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 10)


class TestLearningSystemExtraction(unittest.TestCase):
    """Test LLM-based lesson extraction"""

    def test_extract_lessons_from_llm_response(self):
        """Test that valid LLM JSON response creates lessons"""
        llm_response = json.dumps([
            {
                "description": "Walking improves mood",
                "category": "action_outcome",
                "condition": "sadness above 50%",
                "recommended_action": "go for a walk",
            },
            {
                "description": "Rain increases sadness",
                "category": "environmental",
                "condition": "rainy weather",
                "recommended_action": "stay indoors",
            },
        ])
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)

        # Create some experiences to pass to extract
        experiences = [
            Experience(
                action_taken="walk", action_reasoning="bored",
                needs_before={"hunger": 50}, needs_after={"hunger": 48},
                needs_delta={"hunger": -2},
                emotions_before={"joy": 30}, emotions_after={"joy": 50},
                emotions_delta={"joy": 20},
                overall_satisfaction_before=50, overall_satisfaction_after=60,
            )
        ]
        system.extract_lessons(experiences)

        self.assertEqual(len(system.lessons), 2)
        self.assertEqual(system.lessons[0].description, "Walking improves mood")
        self.assertEqual(system.lessons[1].category, "environmental")

    def test_extract_lessons_max_three(self):
        """Should extract at most 3 lessons"""
        llm_response = json.dumps([
            {"description": f"Lesson {i}", "category": "action_outcome",
             "condition": "c", "recommended_action": "a"}
            for i in range(5)
        ])
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)
        system.extract_lessons([])

        self.assertEqual(len(system.lessons), 3)

    def test_extract_lessons_handles_dict_wrapper(self):
        """Should unwrap dict with 'lessons' key"""
        llm_response = json.dumps({
            "lessons": [
                {"description": "Test", "category": "action_outcome",
                 "condition": "c", "recommended_action": "a"}
            ]
        })
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)
        system.extract_lessons([])

        self.assertEqual(len(system.lessons), 1)

    def test_extract_lessons_handles_single_dict(self):
        """Should handle a single lesson dict (not wrapped in array)"""
        llm_response = json.dumps({
            "description": "Single lesson",
            "category": "action_outcome",
            "condition": "c",
            "recommended_action": "a",
        })
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)
        system.extract_lessons([])

        self.assertEqual(len(system.lessons), 1)
        self.assertEqual(system.lessons[0].description, "Single lesson")

    def test_extract_lessons_skips_invalid_items(self):
        """Items without 'description' should be skipped"""
        llm_response = json.dumps([
            {"category": "action_outcome"},  # no description
            {"description": "Valid", "category": "action_outcome",
             "condition": "c", "recommended_action": "a"},
        ])
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)
        system.extract_lessons([])

        self.assertEqual(len(system.lessons), 1)
        self.assertEqual(system.lessons[0].description, "Valid")

    def test_extract_lessons_survives_llm_error(self):
        """LLM errors should not crash the system"""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API error")
        system = LearningSystem(mock_llm)

        # Should not raise
        system.extract_lessons([])
        self.assertEqual(len(system.lessons), 0)


class TestLearningSystemSerialization(unittest.TestCase):
    """Test to_dict / from_dict serialization"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)
        self.system.LESSON_EXTRACTION_INTERVAL = 999  # prevent extraction

    def test_empty_roundtrip(self):
        """Empty system should serialize and restore"""
        d = self.system.to_dict()
        restored = LearningSystem.from_dict(d, self.mock_llm)

        self.assertEqual(len(restored.experiences), 0)
        self.assertEqual(len(restored.lessons), 0)

    def test_roundtrip_with_data(self):
        """System with experiences and lessons should roundtrip"""
        # Record experiences
        self.system.record_experience(**make_experience(action="eat"))
        self.system.record_experience(**make_experience(action="sleep"))

        # Add lessons manually
        self.system.lessons.append(Lesson(
            "Test lesson", "action_outcome", "c", "a", confidence=0.7,
            times_confirmed=3, times_contradicted=1,
        ))

        # Serialize
        d = self.system.to_dict()

        # Restore
        restored = LearningSystem.from_dict(d, self.mock_llm)

        self.assertEqual(len(restored.experiences), 2)
        self.assertEqual(restored.experiences[0].action_taken, "eat")
        self.assertEqual(len(restored.lessons), 1)
        self.assertEqual(restored.lessons[0].description, "Test lesson")
        self.assertAlmostEqual(restored.lessons[0].confidence, 0.7)
        self.assertEqual(restored.lessons[0].times_confirmed, 3)

    def test_counter_preserved(self):
        """Extraction counter should survive serialization"""
        self.system.record_experience(**make_experience())
        self.system.record_experience(**make_experience())

        d = self.system.to_dict()
        restored = LearningSystem.from_dict(d, self.mock_llm)

        self.assertEqual(
            restored._experience_count_since_extraction,
            self.system._experience_count_since_extraction,
        )


class TestLearningSystemStats(unittest.TestCase):
    """Test get_learning_stats"""

    def setUp(self):
        self.mock_llm = make_mock_llm()
        self.system = LearningSystem(self.mock_llm)
        self.system.LESSON_EXTRACTION_INTERVAL = 999

    def test_empty_stats(self):
        """Empty system should return zero counts"""
        stats = self.system.get_learning_stats()
        self.assertEqual(stats["total_experiences"], 0)
        self.assertEqual(stats["total_lessons"], 0)
        self.assertEqual(stats["active_lessons"], 0)

    def test_stats_with_data(self):
        """Stats should reflect recorded data"""
        self.system.record_experience(**make_experience())
        self.system.record_experience(**make_experience())
        self.system.lessons = [
            Lesson("Active", "action_outcome", "c", "a", confidence=0.5),
            Lesson("Inactive", "action_outcome", "c", "a", confidence=0.1),
        ]

        stats = self.system.get_learning_stats()

        self.assertEqual(stats["total_experiences"], 2)
        self.assertEqual(stats["total_lessons"], 2)
        self.assertEqual(stats["active_lessons"], 1)
        self.assertEqual(len(stats["lessons"]), 1)  # only active
        self.assertLessEqual(len(stats["recent_experiences"]), 5)

    def test_recent_experiences_capped_at_five(self):
        """recent_experiences should show at most 5"""
        for i in range(10):
            self.system.record_experience(**make_experience(action=f"a{i}"))

        stats = self.system.get_learning_stats()
        self.assertEqual(len(stats["recent_experiences"]), 5)


class TestLearningSystemIntegration(unittest.TestCase):
    """Integration tests: full cycle of record → extract → reinforce → decay"""

    def test_full_learning_cycle(self):
        """Test a complete learning cycle across multiple experiences"""
        llm_response = json.dumps([{
            "description": "Eating improves satisfaction",
            "category": "action_outcome",
            "condition": "hunger below 50%",
            "recommended_action": "eat food",
        }])
        mock_llm = make_mock_llm(llm_response)
        system = LearningSystem(mock_llm)
        system.LESSON_EXTRACTION_INTERVAL = 3

        # Record 3 experiences to trigger extraction
        for i in range(3):
            system.record_experience(**make_experience(
                action=f"action_{i}",
                satisfaction_before=40.0 + i,
                satisfaction_after=50.0 + i,
            ))

        # Should have extracted a lesson
        self.assertGreaterEqual(len(system.lessons), 1)

        # Record a matching experience with positive outcome → reinforce
        system.record_experience(**make_experience(
            action="eat food",
            satisfaction_before=40.0,
            satisfaction_after=60.0,
        ))
        eat_lesson = [l for l in system.lessons if "Eating" in l.description][0]
        self.assertGreater(eat_lesson.times_confirmed, 0)

        # Record a matching experience with negative outcome → contradict
        system.record_experience(**make_experience(
            action="eat food",
            satisfaction_before=60.0,
            satisfaction_after=55.0,
        ))
        self.assertGreater(eat_lesson.times_contradicted, 0)

        # Decay lessons
        system.decay_all_lessons(hours=5.0)

        # Lesson should still be active (started at 0.5 + reinforcement - contradiction - decay)
        self.assertTrue(eat_lesson.is_active())

        # Format for prompt
        prompt_text = system.format_lessons_for_prompt()
        self.assertIn("Eating", prompt_text)

        # Stats
        stats = system.get_learning_stats()
        self.assertEqual(stats["total_experiences"], 5)
        self.assertGreater(stats["active_lessons"], 0)


if __name__ == "__main__":
    unittest.main()
