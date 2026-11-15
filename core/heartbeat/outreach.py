"""Choose one recent conversation partner for a proactive message."""

from datetime import datetime, timedelta


def choose_outreach_target(person, people: dict[int, str], now: datetime) -> tuple[int, str] | None:
    """Prefer closeness, then the newest message, after recency and cooldown checks."""
    social_cognition = getattr(person, "social_cognition", None)
    if social_cognition is None:
        return None

    recent_since = now - timedelta(days=7)
    cooldown_since = now - timedelta(hours=6)
    target = None
    best_rank = None
    for user_id, person_key in people.items():
        conversation = person.conversations.get(person_key)
        if conversation is None or not conversation.messages:
            continue
        latest_message_at = max(message.timestamp for message in conversation.messages)
        if latest_message_at < recent_since:
            continue

        model = social_cognition.get_or_create_model(person_key)
        if model.last_proactive_at is not None and model.last_proactive_at >= cooldown_since:
            continue
        rank = (model.relationship.closeness, latest_message_at)
        if best_rank is None or rank > best_rank:
            target = (user_id, person_key)
            best_rank = rank

    return target
