"""Adopt one existing mind and retain each account's own relationship with her."""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime

from core.heartbeat.being import build_person
from core.heartbeat.rhythm import Situation
from core.heartbeat.store import BeingStore
from core.person.person import Conversation, Message, Person
from core.social.social_cognition import PersonModel


@dataclass
class AdoptionReport:
    adopted_user_id: int | None
    experiences: int
    imported_user_ids: list[int]
    events_copied: int
    failed_user_ids: list[int] = field(default_factory=list)   # history could not be read; left in the old rows


def _read_state(state_json: str) -> dict | None:
    try:
        data = json.loads(state_json)
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _experience_count(data: dict) -> int:
    learning = data.get("learning_system") or {}
    return len(learning.get("experiences", []))


def choose_user_to_adopt(states: list[dict], prefer_user_id: int | None = None,
                         test_user_ids: frozenset = frozenset()) -> int | None:
    """Choose the most experienced readable state, breaking ties by user id.

    Accounts in ``test_user_ids`` (the end-to-end test login) are chosen only
    when asked for by id or when no other account has a readable state, so a
    busy test run can never become the one Jenbina by accident.
    """
    candidates = {}
    for row in states:
        data = _read_state(row["person_state_json"])
        if data is not None:
            candidates[row["user_id"]] = _experience_count(data)
    if prefer_user_id is not None:
        if prefer_user_id not in candidates:
            raise ValueError(f"User {prefer_user_id} has no readable saved person state.")
        return prefer_user_id
    if not candidates:
        return None
    real = {user_id: n for user_id, n in candidates.items() if user_id not in test_user_ids}
    pool = real or candidates
    return min(pool, key=lambda user_id: (-pool[user_id], user_id))


def _import_partner(person: Person, data: dict, display_name: str, key: str) -> None:
    """Read only this account's conversation, social model and insight state."""
    conversation_data = data.get("conversations", {}).get(display_name)
    if conversation_data is not None:
        conversation = Conversation(outsider_name=key)
        last_interaction = conversation_data.get("last_interaction")
        if last_interaction:
            conversation.last_interaction = datetime.fromisoformat(last_interaction)
        for message in conversation_data.get("messages", []):
            timestamp = message.get("timestamp")
            conversation.messages.append(Message(
                timestamp=datetime.fromisoformat(timestamp) if timestamp else datetime.now(),
                sender=message.get("sender", ""),
                content=message.get("content", ""),
                message_type=message.get("message_type", "text"),
            ))
        person.conversations[key] = conversation

    model_data = data.get("social_cognition", {}).get("models", {}).get(display_name)
    if model_data is not None:
        person.social_cognition.models[key] = PersonModel.from_dict(model_data)
    last_visit = data.get("last_visit_time")
    if last_visit:
        person.social_cognition.get_or_create_model(key).last_visit_time = datetime.fromisoformat(last_visit)

    insight_data = data.get("insight_system", {})
    personal_insights = insight_data.get("people", {}).get(display_name)
    if personal_insights is not None:
        person.insight_system.people[key] = dict(personal_insights)
    if insight_data.get("first_impression_delivered", False):
        state = person.insight_system.people.setdefault(key, {
            "first_impression_delivered": False, "day": "", "count": 0,
        })
        state["first_impression_delivered"] = True


def adopt_existing(store: BeingStore, user_db, llm, llm_json_mode, insight_llm, now: datetime,
                   prefer_user_id: int | None = None) -> tuple[Person, Situation, AdoptionReport]:
    """Move per-account state into the being record, leaving the source rows intact.

    The caller must hold ownership and have checked that no being record exists.
    """
    states = user_db.list_person_states()
    test_user_ids = frozenset(
        user["id"] for user in user_db.get_all_users() if user.get("provider") == "test"
    )
    chosen_id = choose_user_to_adopt(states, prefer_user_id, test_user_ids)
    situation = Situation.fresh(now)
    if chosen_id is None:
        return (build_person(None, llm, llm_json_mode, insight_llm), situation,
                AdoptionReport(None, 0, [], 0))

    chosen = next(row for row in states if row["user_id"] == chosen_id)
    person = build_person(chosen["person_state_json"], llm, llm_json_mode, insight_llm)
    user = user_db.get_user_by_id(chosen_id)
    display_name = user.get("display_name")
    chosen_key = store.person_key(chosen_id, display_name)
    chosen_data = _read_state(chosen["person_state_json"])
    # The old UI fell back to email for unnamed accounts. Use it only to find
    # their saved history; the new registry and prompt-facing keys never do.
    source_name = display_name or user.get("email") or chosen_key
    _import_partner(person, chosen_data, source_name, chosen_key)
    if source_name != chosen_key:
        person.conversations.pop(source_name, None)
        person.social_cognition.models.pop(source_name, None)
        person.insight_system.people.pop(source_name, None)

    imported, failed = [], []
    for row in states:
        user_id = row["user_id"]
        if user_id == chosen_id:
            continue
        data = _read_state(row["person_state_json"])
        if data is None:
            continue
        try:
            user = user_db.get_user_by_id(user_id)
            display_name = user.get("display_name")
            key = store.person_key(user_id, display_name)
            _import_partner(person, data, display_name or user.get("email") or key, key)
        except Exception:
            # One account's unreadable history must not keep her from starting.
            # Its old rows are untouched and can be imported by hand later.
            logging.getLogger("jenbina.heartbeat").exception(
                "Could not import user %s's history with Jenbina; skipped.", user_id)
            failed.append(user_id)
            continue
        imported.append(user_id)

    # Copy her life events last, right before the record that marks the adoption
    # as done, so a failure above cannot leave duplicates behind for a retry.
    events_copied = store.import_events(user_db.get_events(chosen_id, limit=100000))
    report = AdoptionReport(chosen_id, _experience_count(chosen_data), imported, events_copied, failed)
    store.save_state(person.serialize(), situation.to_dict())
    logging.getLogger("jenbina.heartbeat").info("Adopted existing Jenbina: %s", report)
    return person, situation, report
