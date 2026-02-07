#!/usr/bin/env python3
"""
Unit tests for the emotion system
Tests emotion decay, triggering, clamping, serialization, and EmotionSystem behavior
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from core.emotions.emotion_system import Emotion, EmotionSystem


class TestEmotion(unittest.TestCase):
    """Test individual Emotion functionality"""

    def setUp(self):
        self.emotion = Emotion(
            name="joy",
            intensity=50.0,
            decay_rate=10.0,
            base_intensity=30.0,
        )

    def test_initialization(self):
        self.assertEqual(self.emotion.name, "joy")
        self.assertEqual(self.emotion.intensity, 50.0)
        self.assertEqual(self.emotion.decay_rate, 10.0)
        self.assertEqual(self.emotion.base_intensity, 30.0)

    def test_decay_toward_baseline_from_above(self):
        """Intensity above baseline should decay downward"""
        self.emotion.update(hours_passed=1.0)
        # decay_rate=10 * 1 hour = 10 reduction, 50 -> 40
        self.assertEqual(self.emotion.intensity, 40.0)

    def test_decay_toward_baseline_from_below(self):
        """Intensity below baseline should rise toward it"""
        self.emotion.intensity = 10.0
        self.emotion.update(hours_passed=1.0)
        # decay_rate=10 * 1 hour = 10 increase, 10 -> 20
        self.assertEqual(self.emotion.intensity, 20.0)

    def test_decay_does_not_overshoot_baseline_from_above(self):
        """Decay should not go below baseline when coming from above"""
        self.emotion.intensity = 35.0  # 5 above baseline of 30
        self.emotion.update(hours_passed=1.0)  # would decay 10, but clamped
        self.assertEqual(self.emotion.intensity, 30.0)

    def test_decay_does_not_overshoot_baseline_from_below(self):
        """Recovery should not go above baseline when coming from below"""
        self.emotion.intensity = 25.0  # 5 below baseline of 30
        self.emotion.update(hours_passed=1.0)  # would rise 10, but clamped
        self.assertEqual(self.emotion.intensity, 30.0)

    def test_decay_zero_hours(self):
        """No time passed should leave intensity unchanged"""
        original = self.emotion.intensity
        self.emotion.update(hours_passed=0)
        self.assertEqual(self.emotion.intensity, original)

    def test_decay_negative_hours(self):
        """Negative hours should leave intensity unchanged"""
        original = self.emotion.intensity
        self.emotion.update(hours_passed=-1.0)
        self.assertEqual(self.emotion.intensity, original)

    def test_at_baseline_no_change(self):
        """At baseline, decay should have no effect"""
        self.emotion.intensity = 30.0
        self.emotion.update(hours_passed=2.0)
        self.assertEqual(self.emotion.intensity, 30.0)

    def test_trigger_positive(self):
        """Triggering should increase intensity"""
        self.emotion.trigger(20.0)
        self.assertEqual(self.emotion.intensity, 70.0)

    def test_trigger_negative(self):
        """Negative trigger should decrease intensity"""
        self.emotion.trigger(-20.0)
        self.assertEqual(self.emotion.intensity, 30.0)

    def test_trigger_clamps_at_100(self):
        """Triggering should not exceed 100"""
        self.emotion.trigger(60.0)
        self.assertEqual(self.emotion.intensity, 100.0)

    def test_trigger_clamps_at_0(self):
        """Triggering should not go below 0"""
        self.emotion.trigger(-60.0)
        self.assertEqual(self.emotion.intensity, 0.0)

    def test_trigger_updates_last_triggered(self):
        """Triggering should update last_triggered timestamp"""
        before = self.emotion.last_triggered
        self.emotion.trigger(5.0)
        self.assertGreaterEqual(self.emotion.last_triggered, before)


class TestEmotionSystem(unittest.TestCase):
    """Test EmotionSystem functionality"""

    def setUp(self):
        self.system = EmotionSystem()

    def test_default_initialization(self):
        """Should initialize with 8 Plutchik emotions"""
        self.assertEqual(len(self.system.emotions), 8)
        expected = {"joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"}
        self.assertEqual(set(self.system.emotions.keys()), expected)

    def test_default_baselines(self):
        """Check Jenbina's character baselines"""
        self.assertEqual(self.system.emotions["joy"].base_intensity, 35.0)
        self.assertEqual(self.system.emotions["trust"].base_intensity, 40.0)
        self.assertEqual(self.system.emotions["anger"].base_intensity, 5.0)
        self.assertEqual(self.system.emotions["anticipation"].base_intensity, 30.0)

    def test_initial_intensities_equal_baselines(self):
        """Initially, intensity should equal base_intensity"""
        for emotion in self.system.emotions.values():
            self.assertEqual(emotion.intensity, emotion.base_intensity)

    def test_trigger_emotion(self):
        """Should spike the named emotion"""
        self.system.trigger_emotion("joy", 20)
        self.assertEqual(self.system.emotions["joy"].intensity, 55.0)

    def test_trigger_unknown_emotion(self):
        """Triggering unknown emotion should be a no-op"""
        self.system.trigger_emotion("nostalgia", 10)
        self.assertEqual(len(self.system.emotions), 8)

    def test_apply_adjustments(self):
        """Should apply multiple adjustments at once"""
        self.system.apply_adjustments({"joy": 15, "fear": -10})
        self.assertEqual(self.system.emotions["joy"].intensity, 50.0)
        self.assertEqual(self.system.emotions["fear"].intensity, 5.0)

    def test_get_dominant_emotions(self):
        """Should return top-k emotions by intensity"""
        dominant = self.system.get_dominant_emotions(top_k=3)
        self.assertEqual(len(dominant), 3)
        # Intensities should be in descending order
        intensities = [d["intensity"] for d in dominant]
        self.assertEqual(intensities, sorted(intensities, reverse=True))

    def test_get_dominant_emotions_default_top(self):
        """Trust (40) should be the top emotion by default"""
        dominant = self.system.get_dominant_emotions(1)
        self.assertEqual(dominant[0]["name"], "trust")
        self.assertEqual(dominant[0]["intensity"], 40.0)

    def test_get_emotional_state_summary(self):
        """Should return a dict with emotions and dominant_emotions"""
        summary = self.system.get_emotional_state_summary()
        self.assertIn("emotions", summary)
        self.assertIn("dominant_emotions", summary)
        self.assertEqual(len(summary["emotions"]), 8)
        self.assertEqual(len(summary["dominant_emotions"]), 3)

    def test_update_all_decays(self):
        """After spiking an emotion, update_all should decay it"""
        self.system.trigger_emotion("joy", 30)
        self.assertEqual(self.system.emotions["joy"].intensity, 65.0)
        # Manually set last_update to 1 hour ago
        self.system.last_update = datetime.now() - timedelta(hours=1)
        self.system.update_all()
        # joy decay_rate=5, 1 hour: 65 - 5 = 60
        self.assertAlmostEqual(self.system.emotions["joy"].intensity, 60.0, delta=0.5)

    def test_serialization_roundtrip(self):
        """to_dict -> from_dict should preserve state"""
        self.system.trigger_emotion("anger", 25)
        self.system.trigger_emotion("joy", -10)

        data = self.system.to_dict()
        restored = EmotionSystem.from_dict(data)

        self.assertEqual(len(restored.emotions), len(self.system.emotions))
        for name in self.system.emotions:
            self.assertAlmostEqual(
                restored.emotions[name].intensity,
                self.system.emotions[name].intensity,
                places=2,
            )
            self.assertEqual(
                restored.emotions[name].base_intensity,
                self.system.emotions[name].base_intensity,
            )
            self.assertEqual(
                restored.emotions[name].decay_rate,
                self.system.emotions[name].decay_rate,
            )

    def test_str_representation(self):
        """__str__ should return a readable string"""
        s = str(self.system)
        self.assertIn("EmotionSystem", s)
        self.assertIn("trust", s)

    def test_from_dict_empty(self):
        """from_dict with empty data should produce system with no emotions"""
        restored = EmotionSystem.from_dict({})
        self.assertEqual(len(restored.emotions), 0)


if __name__ == "__main__":
    unittest.main()
