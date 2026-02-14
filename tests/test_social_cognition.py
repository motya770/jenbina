import unittest

from core.social.social_cognition import SocialCognitionSystem
from core.person.person import Person


class TestSocialCognitionSystem(unittest.TestCase):
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
