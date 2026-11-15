"""Outreach selection uses a fixed clock and no external services."""

import unittest
from datetime import datetime, timedelta

from core.heartbeat.outreach import choose_outreach_target
from core.person.person import Message, Person


NOW = datetime(2026, 11, 15, 12, 0)


class TestOutreachTarget(unittest.TestCase):
    def setUp(self):
        self.person = Person()
        self.person.init_social_cognition()
        for name, closeness, age in (
            ("Ann", 70, timedelta(days=2)),
            ("Bob", 40, timedelta(hours=1)),
            ("Cy", 90, timedelta(days=8)),
        ):
            self.person.add_conversation(name).messages.append(
                Message(NOW - age, "outsider", f"hello from {name}"),
            )
            self.person.social_cognition.get_or_create_model(name).relationship.closeness = closeness

    def test_picks_the_closest_recent_person(self):
        self.assertEqual(
            choose_outreach_target(self.person, {1: "Ann", 2: "Bob", 3: "Cy"}, NOW),
            (1, "Ann"),
        )

    def test_skips_anyone_messaged_proactively_in_the_last_six_hours(self):
        ann = self.person.social_cognition.get_or_create_model("Ann")
        ann.last_proactive_at = NOW - timedelta(hours=5, minutes=59)
        self.assertEqual(choose_outreach_target(self.person, {1: "Ann", 2: "Bob"}, NOW), (2, "Bob"))

    def test_cooldown_requires_more_than_six_hours(self):
        ann = self.person.social_cognition.get_or_create_model("Ann")
        ann.last_proactive_at = NOW - timedelta(hours=6)
        self.assertIsNone(choose_outreach_target(self.person, {1: "Ann"}, NOW))
        ann.last_proactive_at -= timedelta(microseconds=1)
        self.assertEqual(choose_outreach_target(self.person, {1: "Ann"}, NOW), (1, "Ann"))

    def test_nobody_recent_means_nobody(self):
        self.assertIsNone(choose_outreach_target(self.person, {3: "Cy"}, NOW))
        self.assertIsNone(choose_outreach_target(self.person, {}, NOW))

    def test_message_exactly_seven_days_old_is_recent(self):
        message = self.person.conversations["Ann"].messages[0]
        message.timestamp = NOW - timedelta(days=7)
        self.assertEqual(choose_outreach_target(self.person, {1: "Ann"}, NOW), (1, "Ann"))
        message.timestamp -= timedelta(microseconds=1)
        self.assertIsNone(choose_outreach_target(self.person, {1: "Ann"}, NOW))

    def test_equal_closeness_prefers_the_most_recent_message(self):
        self.person.social_cognition.get_or_create_model("Bob").relationship.closeness = 70
        self.assertEqual(choose_outreach_target(self.person, {1: "Ann", 2: "Bob"}, NOW), (2, "Bob"))
        # Imported history need not be sorted: use the newest timestamp, not the last list item.
        self.person.conversations["Ann"].messages.insert(
            0, Message(NOW - timedelta(minutes=10), "person", "a reply"),
        )
        self.assertEqual(choose_outreach_target(self.person, {1: "Ann", 2: "Bob"}, NOW), (1, "Ann"))

    def test_missing_social_cognition_has_no_target(self):
        self.person.social_cognition = None
        self.assertIsNone(choose_outreach_target(self.person, {1: "Ann"}, NOW))

    def test_missing_or_empty_conversation_is_not_a_candidate(self):
        self.person.add_conversation("Dee")
        self.assertIsNone(choose_outreach_target(self.person, {4: "Dee", 5: "Eve"}, NOW))


if __name__ == "__main__":
    unittest.main()
