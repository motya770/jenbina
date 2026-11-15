"""Storage for the single being, independent of accounts and Streamlit."""

import os
import re
import socket
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from core.auth.user_db import UserDatabase
from core.heartbeat.store import BeingStore, make_owner_id, owner_is_dead
from core.timeline import EventLog, LifeEventLog, make_wake


T0 = datetime(2026, 11, 15, 12, 0, 0)
STALE = timedelta(seconds=120)


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = os.path.join(self.tmp.name, "users.db")
        self.store = BeingStore(self.db_path)


class TestLease(StoreTestCase):
    def test_first_owner_acquires_and_second_is_refused(self):
        first = self.store.acquire_lease("hostA:1:aa", T0, STALE)
        self.assertTrue(first.acquired)
        self.assertEqual(first.holder, "hostA:1:aa")
        self.assertIsNone(first.previous_renewed_at)
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            second = self.store.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=30), STALE)
        self.assertFalse(second.acquired)
        self.assertEqual(second.holder, "hostA:1:aa")
        self.assertEqual(second.previous_renewed_at, T0)

    def test_stale_lease_is_taken_over(self):
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            second = self.store.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=121), STALE)
        self.assertTrue(second.acquired)
        self.assertEqual(second.holder, "hostB:2:bb")
        self.assertEqual(second.previous_renewed_at, T0)
        self.assertFalse(self.store.renew_lease("hostA:1:aa", T0 + timedelta(seconds=122)))

    def test_dead_holder_on_this_machine_is_taken_over_at_once(self):
        machine = make_owner_id().rsplit(":", 2)[0]
        dead_owner = f"{machine}:999999999:aa"
        self.store.acquire_lease(dead_owner, T0, STALE)
        self.assertTrue(owner_is_dead(dead_owner))
        self.assertFalse(owner_is_dead(f"{machine}:{os.getpid()}:bb"))
        self.assertFalse(owner_is_dead("some-other-host:999999999:cc"))
        owner = make_owner_id()
        lease = self.store.acquire_lease(owner, T0 + timedelta(seconds=1), STALE)
        self.assertTrue(lease.acquired)
        self.assertEqual(lease.holder, owner)
        self.assertEqual(lease.previous_renewed_at, T0)

    def test_release_lets_the_next_owner_in(self):
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        self.store.release_lease("hostA:1:aa")
        lease = self.store.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=1), STALE)
        self.assertTrue(lease.acquired)
        self.assertEqual(lease.holder, "hostB:2:bb")
        self.assertEqual(lease.previous_renewed_at, T0)

    def test_current_owner_can_reacquire_and_renew(self):
        self.assertFalse(self.store.renew_lease("hostA:1:aa", T0))
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        lease = self.store.acquire_lease("hostA:1:aa", T0 + timedelta(seconds=1), STALE)
        self.assertTrue(lease.acquired)
        self.assertEqual(lease.previous_renewed_at, T0)
        renewed = T0 + timedelta(seconds=100)
        self.assertTrue(self.store.renew_lease("hostA:1:aa", renewed))
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            refused = self.store.acquire_lease("hostB:2:bb", renewed + STALE, STALE)
        self.assertFalse(refused.acquired)
        self.assertEqual(refused.previous_renewed_at, renewed)

    def test_another_store_cannot_release_or_renew_the_owner(self):
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        other = BeingStore(self.db_path)
        other.release_lease("hostB:2:bb")
        self.assertFalse(other.renew_lease("hostB:2:bb", T0 + timedelta(seconds=1)))
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            lease = other.acquire_lease("hostB:2:bb", T0 + timedelta(seconds=2), STALE)
        self.assertFalse(lease.acquired)
        self.assertEqual(lease.holder, "hostA:1:aa")
        self.assertEqual(lease.previous_renewed_at, T0)


class TestOwnerIdentity(unittest.TestCase):
    def test_owner_id_contains_local_host_pid_and_unique_nonce(self):
        with patch("core.heartbeat.store._pid_namespace", return_value="pid:[123]"):
            first, second = make_owner_id(), make_owner_id()
        prefix = f"{socket.gethostname()}|pid:[123]:{os.getpid()}:"
        self.assertRegex(first, re.escape(prefix) + r"[0-9a-f]{8}$")
        self.assertNotEqual(first, second)

    def test_permission_error_means_the_owner_is_alive(self):
        machine = make_owner_id().rsplit(":", 2)[0]
        with patch("core.heartbeat.store.os.kill", side_effect=PermissionError):
            self.assertFalse(owner_is_dead(f"{machine}:123:aa"))

    def test_other_pid_namespace_is_never_assumed_dead(self):
        with patch("core.heartbeat.store._pid_namespace", return_value="pid:[1]"):
            mine = make_owner_id()
        with patch("core.heartbeat.store._pid_namespace", return_value="pid:[2]"), \
                patch("core.heartbeat.store.os.kill", side_effect=ProcessLookupError) as kill:
            self.assertFalse(owner_is_dead(mine.rsplit(":", 2)[0] + ":999999999:aa"))
        kill.assert_not_called()

    def test_pid_namespace_reads_the_link_and_defaults_when_unavailable(self):
        from core.heartbeat.store import _pid_namespace

        with patch("core.heartbeat.store.os.readlink", return_value="pid:[123]") as readlink:
            self.assertEqual(_pid_namespace(), "pid:[123]")
        readlink.assert_called_once_with("/proc/self/ns/pid")
        with patch("core.heartbeat.store.os.readlink", side_effect=FileNotFoundError):
            self.assertEqual(_pid_namespace(), "")

    def test_unknown_and_malformed_owners_are_not_assumed_dead(self):
        with patch("core.heartbeat.store.os.kill") as kill:
            for owner in ("", "broken", "remote:123:aa", f"{socket.gethostname()}:bad:aa",
                          f"{socket.gethostname()}:0:aa", f"{socket.gethostname()}:-1:aa"):
                with self.subTest(owner=owner):
                    self.assertFalse(owner_is_dead(owner))
        kill.assert_not_called()


class TestStateAndEvents(StoreTestCase):
    def test_save_is_refused_once_the_lease_is_lost(self):
        self.store.acquire_lease("hostA|:1:aa", T0, STALE)
        self.assertTrue(self.store.save_state('{"v": 1}', {}, owner="hostA|:1:aa"))
        with patch("core.heartbeat.store.owner_is_dead", return_value=False):
            lease = self.store.acquire_lease("hostB|:2:bb", T0 + timedelta(seconds=121), STALE)
        self.assertTrue(lease.acquired)
        self.assertFalse(self.store.save_state('{"v": 2}', {"phase": "asleep"}, owner="hostA|:1:aa"))
        self.assertEqual(self.store.load_state(), ('{"v": 1}', {}))
        self.assertTrue(self.store.save_state('{"v": 3}', {}))
        self.assertEqual(self.store.load_state()[0], '{"v": 3}')

    def test_owned_save_requires_an_existing_active_lease(self):
        self.assertFalse(self.store.save_state("{}", {}, owner="hostA|:1:aa"))
        self.assertIsNone(self.store.load_state())
        self.store.acquire_lease("hostA|:1:aa", T0, STALE)
        self.store.release_lease("hostA|:1:aa")
        self.assertFalse(self.store.save_state("{}", {}, owner="hostA|:1:aa"))
        self.assertIsNone(self.store.load_state())

    def test_unreadable_situation_loads_as_empty(self):
        person_json = '{"name": "Jenbina"}'
        self.store.save_state(person_json, {})
        for situation_json in ("{broken", "null", "[]", '"awake"', "42"):
            with self.subTest(situation_json=situation_json):
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("UPDATE being_state SET situation_json = ? WHERE id = 1", (situation_json,))
                self.assertEqual(self.store.load_state(), (person_json, {}))

    def test_state_round_trip_and_none_when_empty(self):
        self.assertIsNone(self.store.load_state())
        person_json = '{"name": "Jenbina"}'
        self.store.save_state(person_json, {"phase": "asleep"})
        self.assertEqual(self.store.load_state(), (person_json, {"phase": "asleep"}))
        self.store.save_state(person_json, {"phase": "awake"})
        self.assertEqual(BeingStore(self.db_path).load_state(), (person_json, {"phase": "awake"}))
        with sqlite3.connect(self.db_path) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM being_state").fetchone()[0], 1)

    def test_default_path_comes_from_user_database(self):
        with patch("core.heartbeat.store.UserDatabase", return_value=MagicMock(db_path=self.db_path)) as db:
            store = BeingStore()
        db.assert_called_once_with()
        store.save_state("{}", {"phase": "awake"})
        self.assertEqual(self.store.load_state(), ("{}", {"phase": "awake"}))

    def test_events_come_back_oldest_first_with_parsed_detail(self):
        last_id = self.store.store_event("wake", "Last", {"reason": "morning"}, T0 + timedelta(minutes=1))
        first_id = self.store.store_event("sleep", "First", {"reason": "night"}, T0)
        tied_id = self.store.store_event("gap", "Same time", created_at=T0 + timedelta(minutes=1))
        rows = self.store.get_events()
        self.assertEqual(rows, [
            {"id": first_id, "kind": "sleep", "title": "First", "detail": {"reason": "night"}, "created_at": T0},
            {"id": last_id, "kind": "wake", "title": "Last", "detail": {"reason": "morning"}, "created_at": T0 + timedelta(minutes=1)},
            {"id": tied_id, "kind": "gap", "title": "Same time", "detail": {}, "created_at": T0 + timedelta(minutes=1)},
        ])
        self.assertEqual(self.store.get_events(2), rows[-2:])
        self.assertEqual(self.store.get_events(0), [])

    def test_event_without_timestamp_uses_host_clock(self):
        before = datetime.now()
        event_id = self.store.store_event("sleep", "Fell asleep")
        after = datetime.now()
        row = self.store.get_events()[0]
        self.assertEqual(row["id"], event_id)
        self.assertLessEqual(before, row["created_at"])
        self.assertLessEqual(row["created_at"], after)

    def test_unreadable_events_follow_user_database_behavior(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT INTO being_events (kind, title, detail_json, created_at) VALUES (?, ?, ?, ?)",
                [("gap", "Bad time", "{}", "not a time"),
                 ("gap", "Bad json", "broken", T0.isoformat()),
                 ("gap", "Not a dict", "[]", T0.isoformat())],
            )
        rows = self.store.get_events()
        self.assertEqual([r["title"] for r in rows], ["Bad json", "Not a dict"])
        self.assertEqual([r["detail"] for r in rows], [{}, {}])

    def test_import_preserves_events_and_leaves_user_rows_untouched(self):
        db = UserDatabase(self.db_path)
        uid = db.create_or_update_user("u1", "alex@example.com", "Alex")["id"]
        db.save_person_state(uid, '{"old": true}')
        db.store_event(uid, "sleep", "Fell asleep", {"reason": "night"}, T0)
        db.store_event(uid, "wake", "Woke", created_at=T0 + timedelta(hours=8))
        source = db.get_events(uid)
        with sqlite3.connect(self.db_path) as conn:
            original_state = conn.execute("SELECT * FROM user_state").fetchall()
            original_events = conn.execute("SELECT * FROM events").fetchall()
        self.assertEqual(self.store.import_events(source), 2)
        self.assertEqual(self.store.import_events([]), 0)
        imported = self.store.get_events()
        self.assertEqual(
            [{k: v for k, v in row.items() if k != "id"} for row in imported],
            [{k: v for k, v in row.items() if k != "id"} for row in source],
        )
        self.store.save_state("{}", {"phase": "awake"})
        self.store.person_key(uid, "Alex")
        self.store.acquire_lease("hostA:1:aa", T0, STALE)
        with sqlite3.connect(self.db_path) as conn:
            self.assertEqual(conn.execute("SELECT * FROM user_state").fetchall(), original_state)
            self.assertEqual(conn.execute("SELECT * FROM events").fetchall(), original_events)

    def test_life_event_log_records_and_reads(self):
        log = LifeEventLog(self.store)
        self.assertIsInstance(log, EventLog)
        self.assertTrue(log.persistent)
        event = make_wake(timedelta(hours=7, minutes=40), "morning")
        self.assertIs(log.record(event), event)
        self.assertIsNotNone(event.id)
        recent = log.recent(10)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].title, "Woke after 7h 40m")
        self.assertEqual(recent[0].kind, "wake")
        self.assertEqual(recent[0].detail, {"reason": "morning", "seconds": 27600})
        self.assertEqual(recent[0].created_at, event.created_at)
        self.assertEqual(recent[0].id, event.id)
        self.assertEqual(log.recent(0), [])
        self.assertIsNone(log.record(None))

    def test_life_event_log_never_raises_on_storage_or_row_failure(self):
        store = MagicMock()
        store.store_event.side_effect = RuntimeError("disk")
        store.get_events.side_effect = RuntimeError("disk")
        log = LifeEventLog(store)
        event = make_wake(timedelta(hours=1), "morning")
        with patch("builtins.print"):
            self.assertIs(log.record(event), event)
            self.assertEqual(log.recent(), [])
            store.get_events.side_effect = None
            store.get_events.return_value = [{"kind": "wake"}]
            self.assertEqual(log.recent(), [])


class TestPeople(StoreTestCase):
    def test_key_is_fixed_per_user_whatever_the_name_becomes(self):
        self.assertEqual(self.store.person_key(1, "Alex"), "Alex")
        self.assertEqual(self.store.person_key(1, "Alexander"), "Alex")
        self.assertEqual(self.store.person_key(1, None), "Alex")
        self.assertEqual(BeingStore(self.db_path).people(), {1: "Alex"})

    def test_same_display_name_gets_a_distinct_key(self):
        self.assertEqual(self.store.person_key(1, "Alex"), "Alex")
        self.assertEqual(self.store.person_key(2, "Alex"), "Alex (2)")
        self.assertEqual(self.store.person_key(3, "Alex"), "Alex (3)")
        self.assertEqual(self.store.people(), {1: "Alex", 2: "Alex (2)", 3: "Alex (3)"})

    def test_missing_name_falls_back_to_the_user_id(self):
        self.assertEqual(self.store.person_key(4, "  "), "User 4")
        self.assertEqual(self.store.person_key(5, None), "User 5")
        self.assertEqual(self.store.person_key(6, "  Taylor  "), "Taylor")

    def test_no_email_ever_reaches_a_key(self):
        accounts = [
            {"id": 1, "display_name": "Alex", "email": "private.one@example.com"},
            {"id": 2, "display_name": "Alex", "email": "private.two@example.com"},
            {"id": 3, "display_name": None, "email": "private.three@example.com"},
        ]
        keys = [self.store.person_key(user["id"], user["display_name"]) for user in accounts]
        self.assertEqual(keys, ["Alex", "Alex (2)", "User 3"])
        for user in accounts:
            self.assertNotIn(user["email"].split("@")[0], " ".join(keys))

    def test_known_user_lookup_takes_no_write_lock(self):
        self.store.person_key(1, "Alex")
        blocker = sqlite3.connect(self.db_path)
        blocker.execute("BEGIN IMMEDIATE")
        try:
            self.assertEqual(self.store.person_key(1, "Alexander"), "Alex")
        finally:
            blocker.rollback()
            blocker.close()

    def test_literal_names_cannot_take_another_accounts_key(self):
        self.store.person_key(1, "Alex")
        self.store.person_key(2, "Alex (2)")
        self.store.person_key(4, "Alex (4)")
        self.assertEqual(self.store.person_key(3, "Alex"), "Alex (3)")
        self.assertEqual(self.store.person_key(5, "Alex"), "Alex (5)")
        self.assertEqual(len(set(self.store.people().values())), 5)


if __name__ == "__main__":
    unittest.main()
