"""Build and adopt the single being using real state and temporary SQLite files."""

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from core.auth.user_db import UserDatabase
from core.heartbeat.adoption import adopt_existing, choose_user_to_adopt
from core.heartbeat.being import BeingStateError, build_person
from core.heartbeat.rhythm import Situation
from core.person.person import Person


NOW = datetime(2026, 11, 15, 12, 0)
VISIT = NOW - timedelta(days=1)


def saved_state(user_id, experiences=0, display_name="User", message="hello", *,
                first_impression=False, dossier=None):
    person = Person()
    llm = MagicMock()
    llm.invoke.return_value.content = '{"lessons": []}'
    person.init_learning_system(llm)
    for index in range(experiences):
        person.learning_system.record_experience(
            action_taken=f"Action {user_id}-{index}", action_reasoning="A saved experience",
            needs_before={"hunger": 40.0}, needs_after={"hunger": 50.0},
            emotions_before={"joy": 20.0}, emotions_after={"joy": 25.0},
        )
    person.init_social_cognition()
    model = person.social_cognition.get_or_create_model(display_name)
    model.user_dossier = dossier or {}
    model.beliefs = [f"Belief of user {user_id}"]
    person.receive_message(display_name, message)
    person.send_message(display_name, f"reply to {message}", "greeting")
    conversation = person.conversations[display_name]
    conversation.last_interaction = VISIT
    for item in conversation.messages:
        item.timestamp = VISIT
    person.last_visit_time = VISIT
    person.init_insight_system(llm)
    raw = json.loads(person.serialize())
    # These fields reproduce the per-account format before Task 3.
    raw["insight_system"] = {"first_impression_delivered": first_impression}
    return {"user_id": user_id, "person_state_json": json.dumps(raw)}


class TestChooseUser(unittest.TestCase):
    def test_most_experiences_wins_ties_to_lowest_id(self):
        states = [saved_state(3, 9), saved_state(1, 4), saved_state(2, 9)]
        self.assertEqual(choose_user_to_adopt(states), 2)
        self.assertEqual(choose_user_to_adopt(states, prefer_user_id=1), 1)
        self.assertIsNone(choose_user_to_adopt([]))

    def test_a_test_account_is_never_chosen_over_a_real_one(self):
        states = [saved_state(1, 4), saved_state(2, 30)]
        self.assertEqual(choose_user_to_adopt(states, test_user_ids=frozenset({2})), 1)
        self.assertEqual(choose_user_to_adopt(states, prefer_user_id=2, test_user_ids=frozenset({2})), 2)
        # With nobody else to adopt (a fresh test database) the test account will do.
        self.assertEqual(choose_user_to_adopt(states[1:], test_user_ids=frozenset({2})), 2)

    def test_unreadable_states_are_never_chosen(self):
        for broken in ("{broken", "null", "[]"):
            with self.subTest(broken=broken):
                states = [{"user_id": 1, "person_state_json": broken}, saved_state(2)]
                self.assertEqual(choose_user_to_adopt(states), 2)
                self.assertIsNone(choose_user_to_adopt(states[:1]))

    def test_preferred_user_must_have_a_readable_state(self):
        states = [saved_state(1, 4), {"user_id": 2, "person_state_json": "{broken"}]
        for user_id in (2, 8):
            with self.subTest(user_id=user_id), self.assertRaises(ValueError):
                choose_user_to_adopt(states, prefer_user_id=user_id)

    def test_old_state_without_learning_is_a_zero_experience_candidate(self):
        self.assertEqual(choose_user_to_adopt([
            {"user_id": 1, "person_state_json": Person().serialize()}, saved_state(2),
        ]), 1)


class TestBuildPerson(unittest.TestCase):
    def setUp(self):
        self.llm = MagicMock()
        self.json_llm = MagicMock()
        self.insight_llm = MagicMock()

    def assert_initialized(self, person):
        for name in (
            "maslow_needs", "emotion_system", "working_memory", "learning_system",
            "goal_system", "planning_system", "inner_monologue", "social_cognition",
            "self_narrative", "curiosity_system", "social_interaction_tracker", "insight_system",
        ):
            with self.subTest(subsystem=name):
                self.assertIsNotNone(getattr(person, name))
        for llm in (self.llm, self.json_llm, self.insight_llm):
            llm.invoke.assert_not_called()

    def test_new_person_initializes_every_system_and_decay_clock(self):
        person = build_person(None, self.llm, self.json_llm, self.insight_llm)
        self.assert_initialized(person)
        self.assertIsNotNone(person.last_decay_at)
        self.assertIs(person.learning_system.llm, self.json_llm)
        self.assertIs(person.goal_system.llm, self.json_llm)
        self.assertIs(person.planning_system.llm, self.json_llm)
        self.assertIs(person.inner_monologue.llm, self.llm)
        self.assertIs(person.insight_system.llm, self.insight_llm)

    def test_old_person_gets_missing_systems_without_resetting_existing_state(self):
        original = Person(name="Existing Jenbina")
        original.maslow_needs.needs["hunger"].satisfaction = 42.0
        original.last_decay_at = VISIT
        original.working_memory.add_note("Keep my memory")
        person = build_person(original.serialize(), self.llm, self.json_llm, self.insight_llm)
        self.assert_initialized(person)
        self.assertEqual(person.name, "Existing Jenbina")
        self.assertEqual(person.maslow_needs.get_need_satisfaction("hunger"), 42.0)
        self.assertEqual(person.last_decay_at, VISIT)
        self.assertIn("Keep my memory", person.working_memory.format_for_prompt())

    def test_restored_insights_keep_person_state_on_the_plain_insight_llm(self):
        raw = json.loads(saved_state(1, 4)["person_state_json"])
        raw["insight_system"]["people"] = {
            "Ann": {"first_impression_delivered": True, "day": "2026-11-15", "count": 3},
        }
        raw["insight_system"]["first_impression_delivered"] = True
        person = build_person(json.dumps(raw), self.llm, self.json_llm, self.insight_llm)
        self.assert_initialized(person)
        self.assertEqual(len(person.learning_system.experiences), 4)
        self.assertIs(person.insight_system.llm, self.insight_llm)
        self.assertTrue(person.insight_system.legacy_first_impression_delivered)
        self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, "Ann"))
        self.assertFalse(person.insight_system.should_generate_insight(5, "Ann", NOW.date()))

    def test_build_person_refuses_unreadable_state(self):
        for broken in ("{broken", "null", "[]", "{}", ""):
            with self.subTest(broken=broken), self.assertRaises(BeingStateError) as raised:
                build_person(broken, None, None, None)
            self.assertIsNotNone(raised.exception.__cause__)


class TestAdoption(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db_path = os.path.join(self.temp.name, "users.db")
        self.user_db = UserDatabase(self.db_path)
        # Imported here to keep all storage on this temporary path.
        from core.heartbeat.store import BeingStore
        self.store = BeingStore(self.db_path)
        for user_id, name in ((1, "Ann"), (2, "Bob"), (3, "Ann")):
            user = self.user_db.create_or_update_user(
                firebase_uid=f"user-{user_id}", email=f"user-{user_id}@example.test",
                display_name=name,
            )
            self.assertEqual(user["id"], user_id)
        self.llm, self.json_llm, self.insight_llm = MagicMock(), MagicMock(), MagicMock()

    def save(self, row):
        self.user_db.save_person_state(row["user_id"], row["person_state_json"])

    def populate(self):
        self.save(saved_state(1, 4, "Ann", "ann-hello", dossier={"job": "ANN-JOB"}))
        self.save(saved_state(2, 9, "Bob", "bob-hello", first_impression=True))
        self.save(saved_state(3, 2, "Ann", "other-ann-hello", first_impression=True,
                              dossier={"job": "OTHER-ANN-JOB"}))
        self.user_db.store_event(2, "action", "Bob's Jenbina read", {"action": "Read"}, VISIT)
        self.user_db.store_event(2, "mood", "Content", {"emotion": "joy"}, NOW)
        self.user_db.store_event(1, "action", "Do not copy this life", created_at=VISIT)

    def adopt(self, **kwargs):
        return adopt_existing(self.store, self.user_db, self.llm, self.json_llm,
                              self.insight_llm, NOW, **kwargs)

    def test_adoption_keeps_her_and_imports_everyone_elses_history(self):
        self.populate()
        with self.assertLogs("jenbina.heartbeat", level="INFO") as logged:
            person, situation, report = self.adopt()
        self.assertEqual((report.adopted_user_id, report.experiences,
                          report.imported_user_ids, report.events_copied), (2, 9, [1, 3], 2))
        self.assertEqual(len(person.learning_system.experiences), 9)
        self.assertTrue(all(item.action_taken.startswith("Action 2-")
                            for item in person.learning_system.experiences))
        self.assertEqual(person.conversations["Bob"].messages[0].content, "bob-hello")
        self.assertEqual(person.conversations["Ann"].messages[0].content, "ann-hello")
        self.assertEqual(person.social_cognition.models["Ann"].user_dossier, {"job": "ANN-JOB"})
        self.assertEqual(person.social_cognition.models["Bob"].last_visit_time, VISIT)
        self.assertEqual(person.social_cognition.models["Ann"].last_visit_time, VISIT)
        self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, "Bob"))
        self.assertTrue(person.insight_system.should_generate_first_impression({"x": 1}, "Ann"))
        self.assertIs(person.insight_system.llm, self.insight_llm)
        self.assertEqual(situation, Situation.fresh(NOW))
        source_events = self.user_db.get_events(2)
        self.assertEqual(
            [(e["kind"], e["title"], e["detail"], e["created_at"]) for e in self.store.get_events()],
            [(e["kind"], e["title"], e["detail"], e["created_at"]) for e in source_events],
        )
        saved_json, saved_situation = self.store.load_state()
        self.assertEqual(saved_situation, situation.to_dict())
        restored = build_person(saved_json, self.llm, self.json_llm, self.insight_llm)
        self.assertEqual(len(restored.learning_system.experiences), 9)
        self.assertEqual(restored.social_cognition.models["Bob"].last_visit_time, VISIT)
        self.assertFalse(restored.insight_system.should_generate_first_impression({"x": 1}, "Bob"))
        self.assertTrue(any("2" in line for line in logged.output))
        for llm in (self.llm, self.json_llm, self.insight_llm):
            llm.invoke.assert_not_called()

    def test_two_accounts_with_one_name_never_share_a_conversation(self):
        self.populate()
        person, _, _ = self.adopt()
        self.assertEqual(self.store.people(), {1: "Ann", 2: "Bob", 3: "Ann (2)"})
        self.assertEqual(person.conversations["Ann"].messages[0].content, "ann-hello")
        other_key = self.store.people()[3]
        other = person.conversations[other_key]
        self.assertEqual(other.outsider_name, other_key)
        self.assertEqual(other.messages[0].content, "other-ann-hello")
        self.assertEqual(other.messages[0].timestamp, VISIT)
        self.assertEqual(other.last_interaction, VISIT)
        self.assertEqual(other.messages[1].message_type, "greeting")
        self.assertEqual(person.social_cognition.models[other_key].user_dossier,
                         {"job": "OTHER-ANN-JOB"})
        self.assertEqual(person.social_cognition.models[other_key].beliefs, ["Belief of user 3"])
        self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, other_key))
        self.assertTrue(person.insight_system.should_generate_first_impression({"x": 1}, "Ann"))

    def test_adopted_user_registers_first_and_keeps_the_plain_name(self):
        self.populate()
        person, _, report = self.adopt(prefer_user_id=3)
        self.assertEqual(report.adopted_user_id, 3)
        self.assertEqual(self.store.people()[3], "Ann")
        self.assertEqual(self.store.people()[1], "Ann (2)")
        self.assertEqual(person.conversations["Ann"].messages[0].content, "other-ann-hello")
        self.assertEqual(person.conversations["Ann (2)"].messages[0].content, "ann-hello")

    def test_old_rows_are_untouched(self):
        self.populate()
        self.user_db.store_message(1, "Ann", "private SQLite message")
        def rows():
            with sqlite3.connect(self.db_path) as conn:
                return [conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
                        for table in ("user_state", "events", "conversations")]
        before = rows()
        self.adopt()
        self.assertEqual(rows(), before)

    def test_nobody_to_adopt_gives_a_new_person(self):
        person, situation, report = adopt_existing(self.store, self.user_db, None, None, None, NOW)
        self.assertEqual(person.name, "Jenbina")
        self.assertEqual(situation, Situation.fresh(NOW))
        self.assertEqual((report.adopted_user_id, report.experiences,
                          report.imported_user_ids, report.events_copied), (None, 0, [], 0))

    def test_unreadable_other_state_is_skipped(self):
        self.populate()
        self.user_db.save_person_state(1, "{broken")
        person, _, report = self.adopt()
        self.assertEqual(report.imported_user_ids, [3])
        self.assertEqual(person.conversations[self.store.people()[3]].messages[0].content,
                         "other-ann-hello")

    def test_missing_parts_are_skipped_and_other_peoples_models_are_not_imported(self):
        self.populate()
        raw = json.loads(self.user_db.load_person_state(1))
        raw["conversations"]["Foreign"] = raw["conversations"].pop("Ann")
        raw["social_cognition"]["models"]["Foreign"] = raw["social_cognition"]["models"].pop("Ann")
        self.user_db.save_person_state(1, json.dumps(raw))
        person, _, report = self.adopt()
        self.assertEqual(report.imported_user_ids, [1, 3])
        self.assertNotIn("Ann", person.conversations)
        self.assertNotIn("Foreign", person.conversations)
        self.assertNotIn("Foreign", person.social_cognition.models)

    def test_chosen_invalid_person_is_not_replaced_by_a_new_one(self):
        self.user_db.save_person_state(2, '{"learning_system": {"experiences": [1, 2]}}')
        with self.assertRaises(BeingStateError):
            self.adopt()
        self.assertIsNone(self.store.load_state())
        self.assertEqual(self.store.get_events(), [])

    def test_existing_per_person_visits_and_insight_quotas_survive_import(self):
        self.populate()
        for user_id, name in ((2, "Bob"), (3, "Ann")):
            raw = json.loads(self.user_db.load_person_state(user_id))
            raw["last_visit_time"] = None
            raw["social_cognition"]["models"][name]["last_visit_time"] = VISIT.isoformat()
            raw["insight_system"] = {"people": {
                name: {"first_impression_delivered": True, "day": "2026-11-15", "count": 3},
            }}
            self.user_db.save_person_state(user_id, json.dumps(raw))
        person, _, _ = self.adopt()
        for key in ("Bob", "Ann (2)"):
            with self.subTest(key=key):
                self.assertEqual(person.social_cognition.models[key].last_visit_time, VISIT)
                self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, key))
                self.assertFalse(person.insight_system.should_generate_insight(5, key, NOW.date()))

    def add_unnamed_user(self):
        user = self.user_db.create_or_update_user(
            firebase_uid="unnamed", email="unnamed@example.test", display_name=None,
        )
        # Before the heartbeat, the UI used email as the conversation key for such users.
        self.save(saved_state(user["id"], 1, user["email"], "unnamed-hello",
                              first_impression=True, dossier={"job": "UNNAMED-JOB"}))
        return user

    def test_missing_display_name_imports_legacy_email_history_under_a_safe_key(self):
        self.populate()
        user = self.add_unnamed_user()
        person, _, report = self.adopt()
        self.assertEqual(report.imported_user_ids, [1, 3, 4])
        self.assertEqual(self.store.people()[4], "User 4")
        self.assertEqual(person.conversations["User 4"].messages[0].content, "unnamed-hello")
        self.assertEqual(person.social_cognition.models["User 4"].user_dossier,
                         {"job": "UNNAMED-JOB"})
        self.assertNotIn(user["email"], person.conversations)
        self.assertNotIn(user["email"], person.social_cognition.models)

    def test_adopted_legacy_email_key_is_moved_to_the_registered_key(self):
        self.populate()
        user = self.add_unnamed_user()
        person, _, report = self.adopt(prefer_user_id=user["id"])
        self.assertEqual(report.adopted_user_id, 4)
        self.assertEqual(person.conversations["User 4"].outsider_name, "User 4")
        self.assertEqual(person.conversations["User 4"].messages[0].content, "unnamed-hello")
        self.assertEqual(person.social_cognition.models["User 4"].user_dossier,
                         {"job": "UNNAMED-JOB"})
        self.assertFalse(person.insight_system.should_generate_first_impression({"x": 1}, "User 4"))
        self.assertNotIn(user["email"], person.conversations)
        self.assertNotIn(user["email"], person.social_cognition.models)



class TestAdoptionSafety(TestAdoption):
    def test_the_end_to_end_test_login_does_not_become_her(self):
        self.user_db.create_or_update_user(firebase_uid="test:e2e@test.local", email="e2e@test.local",
                                           display_name="E2E Test User", provider="test")
        self.save(saved_state(1, 4, "Ann", "ann-hello"))
        self.save(saved_state(4, 30, "E2E Test User", "test-hello"))
        person, _, report = adopt_existing(self.store, self.user_db, self.llm, self.json_llm,
                                           self.insight_llm, NOW)
        self.assertEqual(report.adopted_user_id, 1)
        self.assertEqual(report.imported_user_ids, [4])
        self.assertEqual(person.conversations["E2E Test User"].messages[0].content, "test-hello")

    def test_one_unreadable_history_does_not_block_her_start(self):
        self.populate()
        broken = json.loads(saved_state(1, 4, "Ann", "ann-hello")["person_state_json"])
        broken["conversations"]["Ann"]["last_interaction"] = "not a timestamp"
        self.user_db.save_person_state(1, json.dumps(broken))
        person, _, report = adopt_existing(self.store, self.user_db, self.llm, self.json_llm,
                                           self.insight_llm, NOW)
        self.assertEqual(report.adopted_user_id, 2)
        self.assertEqual(report.failed_user_ids, [1])
        self.assertEqual(report.imported_user_ids, [3])
        self.assertIsNotNone(self.store.load_state())
        self.assertIsNotNone(self.user_db.load_person_state(1))       # still there to import by hand


if __name__ == "__main__":
    unittest.main()
