import unittest

from core.cognition.curiosity_system import CuriositySystem
from core.person.person import Person


class TestCuriositySystem(unittest.TestCase):
    def test_novelty_detection(self):
        c = CuriositySystem()
        needs = {"hunger": 80.0, "sleep": 80.0, "security": 80.0}

        c.observe_cycle(needs, {"location": "home", "time_of_day": "morning", "weather": "sunny"}, ["eat", "read"])
        first = c.last_novelty_score
        c.observe_cycle(needs, {"location": "home", "time_of_day": "morning", "weather": "sunny"}, ["eat", "read"])
        second = c.last_novelty_score

        self.assertGreaterEqual(first, second)
        self.assertGreaterEqual(first, 0.5)

    def test_boredom_drives_exploration(self):
        c = CuriositySystem()
        needs = {"hunger": 92.0, "sleep": 91.0, "security": 90.0}
        repeated = ["eat", "eat", "eat", "eat", "eat"]

        c.observe_cycle(
            needs,
            {"location": "home", "time_of_day": "afternoon", "weather": "clear"},
            ["eat", "explore nearby park", "read article"],
            recent_actions=repeated,
        )

        self.assertGreater(c.boredom_level, 0.4)
        self.assertTrue(c.should_explore())
        self.assertTrue(any("wonder" in q.lower() for q in c.open_questions))

    def test_information_seeking_candidates(self):
        c = CuriositySystem()
        c.observe_cycle(
            {"hunger": 75.0, "sleep": 75.0, "security": 75.0},
            {"location": "library", "time_of_day": "evening", "weather": "rain"},
            ["eat", "learn about weather", "ask librarian", "sleep"],
        )

        joined = " ".join(c.suggested_explorations).lower()
        self.assertIn("learn", joined)
        self.assertIn("ask", joined)

    def test_exploration_score(self):
        c = CuriositySystem()
        c.observe_cycle(
            {"hunger": 85.0, "sleep": 85.0, "security": 85.0},
            {"location": "home", "time_of_day": "night", "weather": "clear"},
            ["eat", "explore museum"],
            recent_actions=["eat", "eat", "eat", "eat"],
        )
        self.assertGreater(c.exploration_score("explore museum"), c.exploration_score("eat"))


class TestPersonCuriositySerialization(unittest.TestCase):
    def test_curiosity_persists(self):
        p = Person("Jenbina")
        p.init_curiosity_system()
        p.curiosity_system.observe_cycle(
            {"hunger": 88.0, "sleep": 89.0, "security": 90.0},
            {"location": "park", "time_of_day": "morning", "weather": "fog"},
            ["explore park", "eat"],
            recent_actions=["eat", "eat", "eat", "eat"],
        )

        raw = p.serialize()
        restored = Person.deserialize(raw, llm=None)
        self.assertIsNotNone(restored.curiosity_system)
        stats = restored.curiosity_system.get_stats()
        self.assertIn("curiosity_level", stats)
        self.assertIn("open_questions", stats)


if __name__ == "__main__":
    unittest.main()
