import unittest

from core.identity.self_narrative import SelfNarrativeSystem
from core.learning.learning_system import Experience, Lesson
from core.person.person import Person


class TestSelfNarrativeSystem(unittest.TestCase):
    def _exp(self, action="learn coding", before=50.0, after=58.0, reasoning="to improve"):
        return Experience(
            action_taken=action,
            action_reasoning=reasoning,
            needs_before={"hunger": 50.0},
            needs_after={"hunger": 55.0},
            needs_delta={"hunger": 5.0},
            emotions_before={"joy": 20.0},
            emotions_after={"joy": 30.0},
            emotions_delta={"joy": 10.0},
            overall_satisfaction_before=before,
            overall_satisfaction_after=after,
        )

    def test_updates_values_and_story(self):
        s = SelfNarrativeSystem()
        exp = self._exp(action="learn python and build project", before=50, after=62)
        s.integrate_experience(exp, [])

        self.assertGreater(s.values["growth"], 0.2)
        self.assertIn("Recently my path", s.life_story)
        self.assertTrue(s.self_concept)

    def test_identity_crisis_on_contradiction(self):
        s = SelfNarrativeSystem()

        # First reinforce stability as dominant value
        for _ in range(8):
            s.integrate_experience(self._exp(action="sleep and keep routine", before=50, after=55), [])

        # Contradict with risky behavior and negative outcome
        s.integrate_experience(
            self._exp(action="gamble in chaos", before=55, after=45, reasoning="impulsive"),
            [],
        )

        self.assertGreater(s.identity_crisis_level, 0.0)
        self.assertLess(s.identity_coherence, 1.0)

    def test_lesson_driven_values(self):
        s = SelfNarrativeSystem()
        exp = self._exp()
        lessons = [
            Lesson(
                description="Helping others improves emotional outcomes",
                category="emotional_pattern",
                condition="when someone is sad",
                recommended_action="offer support",
                confidence=0.9,
            )
        ]
        s.integrate_experience(exp, lessons)
        self.assertGreater(s.values["compassion"], 0.2)

    def test_round_trip(self):
        s = SelfNarrativeSystem()
        s.integrate_experience(self._exp(action="talk to friend", before=50, after=56), [])

        d = s.to_dict()
        s2 = SelfNarrativeSystem.from_dict(d)
        self.assertEqual(len(s2.events), len(s.events))
        self.assertEqual(s2.life_story, s.life_story)


class TestPersonSelfNarrativeSerialization(unittest.TestCase):
    def test_person_serialization_includes_self_narrative(self):
        p = Person("Jenbina")
        p.init_self_narrative()
        exp = Experience(
            action_taken="learn",
            action_reasoning="grow",
            needs_before={"hunger": 50.0},
            needs_after={"hunger": 50.0},
            needs_delta={"hunger": 0.0},
            emotions_before={"joy": 20.0},
            emotions_after={"joy": 25.0},
            emotions_delta={"joy": 5.0},
            overall_satisfaction_before=50.0,
            overall_satisfaction_after=55.0,
        )
        p.self_narrative.integrate_experience(exp, [])

        raw = p.serialize()
        restored = Person.deserialize(raw, llm=None)
        self.assertIsNotNone(restored.self_narrative)
        self.assertGreater(restored.self_narrative.get_stats()["total_events"], 0)


if __name__ == "__main__":
    unittest.main()
