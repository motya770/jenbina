import unittest
from datetime import datetime

from core.social.social_cognition import PersonModel, SocialCognitionSystem
from core.person.person import Person


class TestSocialCognitionSystem(unittest.TestCase):
    def test_visit_and_proactive_times_round_trip(self):
        model = PersonModel()
        model.last_visit_time = datetime(2026, 11, 15, 9, 0)
        model.last_proactive_at = datetime(2026, 11, 15, 10, 0)
        data = model.to_dict()
        self.assertEqual(data["last_visit_time"], "2026-11-15T09:00:00")
        self.assertEqual(data["last_proactive_at"], "2026-11-15T10:00:00")
        restored = PersonModel.from_dict(data)
        self.assertEqual(restored.last_visit_time, model.last_visit_time)
        self.assertEqual(restored.last_proactive_at, model.last_proactive_at)
        legacy = PersonModel.from_dict({})
        self.assertIsNone(legacy.last_visit_time)
        self.assertIsNone(legacy.last_proactive_at)
        self.assertIsNone(legacy.to_dict()["last_visit_time"])
        self.assertIsNone(legacy.to_dict()["last_proactive_at"])

    def test_stats_filter_does_not_expose_other_people_or_create_unknown_models(self):
        system = SocialCognitionSystem()
        system.get_or_create_model("Ann").beliefs.append("ANN-SECRET")
        system.get_or_create_model("Bob").beliefs.append("BOB-SECRET")
        self.assertEqual(list(system.get_stats(only="Bob")["entities"]), ["Bob"])
        self.assertEqual(system.get_stats(only="Bob")["entities"]["Bob"]["beliefs"], ["BOB-SECRET"])
        self.assertEqual(system.get_stats(only="Unknown")["entities"], {})
        self.assertEqual(system.get_stats()["tracked_entities"], 2)
        self.assertEqual(set(system.get_stats()["entities"]), {"Ann", "Bob"})

    def test_updates_person_model_from_message(self):
        sys = SocialCognitionSystem()
        sys.observe_entity_message(
            "Alice",
            "I feel sad lately, but I like technology and python. Thank you for listening.",
        )

        model = sys.get_or_create_model("Alice")
        self.assertEqual(model.inferred_emotional_state, "sad")
        self.assertGreater(model.interests.get("technology", 0.0), 0.0)
        self.assertGreater(model.relationship.trust, 50.0)

    def test_conflict_rises_for_hostile_input(self):
        sys = SocialCognitionSystem()
        sys.observe_entity_message("Bob", "You are useless and I hate this")

        model = sys.get_or_create_model("Bob")
        self.assertGreater(model.relationship.conflict, 10.0)
        self.assertLess(model.relationship.trust, 50.0)

    def test_strategy_selection(self):
        sys = SocialCognitionSystem()

        # Sad user -> nice
        sys.observe_entity_message("Cara", "I am sad and stressed")
        self.assertEqual(sys.choose_social_strategy("Cara"), "nice")

        # High conflict -> polite
        for _ in range(5):
            sys.observe_entity_message("Dan", "I hate this, shut up")
        self.assertEqual(sys.choose_social_strategy("Dan"), "polite")

        # High trust/closeness -> assertive
        for _ in range(20):
            sys.observe_entity_message("Eve", "Thank you, I like technology and coding")
            sys.observe_response_effect("Eve", "nice")
        self.assertEqual(sys.choose_social_strategy("Eve", "be direct"), "assertive")

    def test_predict_reaction_shape(self):
        sys = SocialCognitionSystem()
        sys.observe_entity_message("Frank", "Thanks for helping me")
        pred = sys.predict_reaction("Frank", "polite")

        self.assertIn("reaction", pred)
        self.assertIn("valence", pred)
        self.assertIn("confidence", pred)

    def test_round_trip(self):
        sys = SocialCognitionSystem()
        sys.observe_entity_message("Grace", "I love music and I am happy")

        data = sys.to_dict()
        restored = SocialCognitionSystem.from_dict(data)
        model = restored.get_or_create_model("Grace")
        self.assertTrue(model.beliefs)
        self.assertIn("music", model.beliefs[0].lower())


class TestPersonSocialSerialization(unittest.TestCase):
    def test_person_social_state_survives_serialize(self):
        person = Person("Jenbina")
        person.init_social_cognition()
        person.social_cognition.observe_entity_message("User", "I feel anxious about work")

        raw = person.serialize()
        restored = Person.deserialize(raw, llm=None)

        self.assertIsNotNone(restored.social_cognition)
        model = restored.social_cognition.get_or_create_model("User")
        self.assertEqual(model.inferred_emotional_state, "anxious")


if __name__ == "__main__":
    unittest.main()
