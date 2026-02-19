"""Tests for the SocialInteractionTracker system."""

import time
import unittest

from core.social.social_interaction_tracker import (
    SocialInteractionTracker,
    SocialInteraction,
    infer_emotional_tone,
)
from core.person.person import Person


class TestInferEmotionalTone(unittest.TestCase):
    def test_positive_message(self):
        self.assertEqual(infer_emotional_tone("Thank you so much, that was great!"), "warm")

    def test_negative_message(self):
        self.assertEqual(infer_emotional_tone("I am angry and frustrated"), "tense")

    def test_neutral_message(self):
        self.assertEqual(infer_emotional_tone("The weather is cloudy today"), "neutral")

    def test_mixed_leans_positive(self):
        # 2 positive (happy, great) vs 1 negative (worried)
        self.assertEqual(
            infer_emotional_tone("I'm happy and great but a bit worried"), "warm"
        )


class TestSocialInteraction(unittest.TestCase):
    def test_to_dict_round_trip(self):
        interaction = SocialInteraction(
            person_name="Alice",
            interaction_type="chat",
            emotional_tone="warm",
            sentiment="I felt good about talking to Alice",
            timestamp=1000.0,
        )
        data = interaction.to_dict()
        restored = SocialInteraction.from_dict(data)
        self.assertEqual(restored.person_name, "Alice")
        self.assertEqual(restored.interaction_type, "chat")
        self.assertEqual(restored.emotional_tone, "warm")
        self.assertEqual(restored.sentiment, "I felt good about talking to Alice")
        self.assertEqual(restored.timestamp, 1000.0)

    def test_from_dict_defaults(self):
        restored = SocialInteraction.from_dict({})
        self.assertEqual(restored.person_name, "unknown")
        self.assertEqual(restored.interaction_type, "chat")
        self.assertEqual(restored.emotional_tone, "neutral")


class TestSocialInteractionTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = SocialInteractionTracker()

    def test_record_chat(self):
        interaction = self.tracker.record_chat("Alice", "Thank you for your help!")
        self.assertEqual(interaction.person_name, "Alice")
        self.assertEqual(interaction.interaction_type, "chat")
        self.assertEqual(interaction.emotional_tone, "warm")
        self.assertEqual(len(self.tracker.interactions), 1)

    def test_record_chat_explicit_tone(self):
        interaction = self.tracker.record_chat(
            "Bob", "Hello", emotional_tone="tense", sentiment="Felt uneasy"
        )
        self.assertEqual(interaction.emotional_tone, "tense")
        self.assertEqual(interaction.sentiment, "Felt uneasy")

    def test_record_social_action(self):
        interaction = self.tracker.record_social_action(
            "Talk to neighbor about the weather", emotional_tone="warm"
        )
        self.assertEqual(interaction.person_name, "a neighbor")
        self.assertEqual(interaction.interaction_type, "simulated_social")
        self.assertEqual(interaction.emotional_tone, "warm")

    def test_record_social_action_extracts_person(self):
        interaction = self.tracker.record_social_action("Chat with barista at cafe")
        self.assertEqual(interaction.person_name, "a barista")

    def test_record_social_action_fallback(self):
        interaction = self.tracker.record_social_action("Go outside and enjoy the sun")
        self.assertEqual(interaction.person_name, "someone")

    def test_people_met_count(self):
        self.tracker.record_chat("Alice", "Hi")
        self.tracker.record_chat("Bob", "Hey")
        self.tracker.record_chat("Alice", "How are you?")
        self.assertEqual(self.tracker.people_met_count(), 2)

    def test_get_unique_people_today(self):
        self.tracker.record_chat("Alice", "Hi")
        self.tracker.record_chat("Bob", "Hey")
        self.tracker.record_chat("Charlie", "Hello")
        people = self.tracker.get_unique_people_today()
        self.assertEqual(people, ["Alice", "Bob", "Charlie"])

    def test_describe_day_no_interactions(self):
        result = self.tracker.describe_day()
        self.assertEqual(result, "I didn't really talk to anyone today.")

    def test_describe_day_one_person(self):
        self.tracker.record_chat("Alice", "Thank you for being so kind!")
        result = self.tracker.describe_day()
        self.assertIn("1 person", result)
        self.assertIn("Alice", result)

    def test_describe_day_multiple_people(self):
        self.tracker.record_chat("Alice", "Hi there!")
        self.tracker.record_chat("Bob", "Hey Bob, I'm feeling angry")
        self.tracker.record_chat("Charlie", "Hello")
        result = self.tracker.describe_day()
        self.assertIn("3 people", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Charlie", result)

    def test_describe_day_long_conversation(self):
        for i in range(5):
            self.tracker.record_chat("Alice", f"Message {i}")
        result = self.tracker.describe_day()
        self.assertIn("long conversation", result)

    def test_format_for_prompt_empty(self):
        result = self.tracker.format_for_prompt()
        self.assertIn("none so far", result)

    def test_format_for_prompt_with_interactions(self):
        self.tracker.record_chat("Alice", "Thanks!")
        self.tracker.record_chat("Bob", "Hello")
        result = self.tracker.format_for_prompt()
        self.assertIn("met 2 people", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_get_stats(self):
        self.tracker.record_chat("Alice", "Hi")
        self.tracker.record_chat("Bob", "Hey")
        stats = self.tracker.get_stats()
        self.assertEqual(stats["total_interactions"], 2)
        self.assertEqual(stats["people_met_today"], 2)
        self.assertEqual(len(stats["unique_people_today"]), 2)
        self.assertEqual(len(stats["recent_interactions"]), 2)

    def test_serialization_round_trip(self):
        self.tracker.record_chat("Alice", "Thank you!")
        self.tracker.record_social_action("Talk to neighbor")
        data = self.tracker.to_dict()
        restored = SocialInteractionTracker.from_dict(data)
        self.assertEqual(len(restored.interactions), 2)
        self.assertEqual(restored.interactions[0].person_name, "Alice")
        self.assertEqual(restored.interactions[1].interaction_type, "simulated_social")

    def test_from_dict_empty(self):
        restored = SocialInteractionTracker.from_dict({})
        self.assertEqual(len(restored.interactions), 0)

    def test_from_dict_none(self):
        restored = SocialInteractionTracker.from_dict(None)
        self.assertEqual(len(restored.interactions), 0)

    def test_max_history_limit(self):
        for i in range(250):
            self.tracker.record_chat(f"Person{i}", f"Message {i}")
        self.assertLessEqual(len(self.tracker.interactions), SocialInteractionTracker.MAX_HISTORY)

    def test_get_today_interactions_filters_old(self):
        # Record an interaction with a very old timestamp
        old_interaction = SocialInteraction(
            person_name="OldFriend",
            interaction_type="chat",
            emotional_tone="neutral",
            sentiment="",
            timestamp=1000.0,  # very old
        )
        self.tracker.interactions.append(old_interaction)
        self.tracker.record_chat("NewFriend", "Hi!")
        # Today's interactions should only include NewFriend
        today = self.tracker.get_today_interactions()
        names = [i.person_name for i in today]
        self.assertNotIn("OldFriend", names)
        self.assertIn("NewFriend", names)


class TestPersonSocialInteractionTracker(unittest.TestCase):
    def test_person_init_tracker(self):
        person = Person("Jenbina")
        person.init_social_interaction_tracker()
        self.assertIsNotNone(person.social_interaction_tracker)

    def test_person_describe_day_no_tracker(self):
        person = Person("Jenbina")
        result = person.describe_day()
        self.assertEqual(result, "I didn't really talk to anyone today.")

    def test_person_describe_day_with_tracker(self):
        person = Person("Jenbina")
        person.init_social_interaction_tracker()
        person.social_interaction_tracker.record_chat("Alice", "Hey!")
        result = person.describe_day()
        self.assertIn("1 person", result)
        self.assertIn("Alice", result)

    def test_person_serialize_with_tracker(self):
        person = Person("Jenbina")
        person.init_social_interaction_tracker()
        person.social_interaction_tracker.record_chat("Alice", "Thank you!")

        raw = person.serialize()
        restored = Person.deserialize(raw, llm=None)
        self.assertIsNotNone(restored.social_interaction_tracker)
        self.assertEqual(len(restored.social_interaction_tracker.interactions), 1)
        self.assertEqual(
            restored.social_interaction_tracker.interactions[0].person_name, "Alice"
        )

    def test_person_serialize_without_tracker(self):
        person = Person("Jenbina")
        raw = person.serialize()
        restored = Person.deserialize(raw, llm=None)
        self.assertIsNone(restored.social_interaction_tracker)

    def test_get_current_state_includes_tracker(self):
        person = Person("Jenbina")
        person.init_social_interaction_tracker()
        person.social_interaction_tracker.record_chat("Alice", "Hi")
        state = person.get_current_state()
        self.assertIn("social_interactions", state)
        self.assertEqual(state["social_interactions"]["people_met_today"], 1)


if __name__ == "__main__":
    unittest.main()
