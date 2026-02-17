"""Tests for GPT-generated greeting functions."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from core.interaction.chat_handler import (
    generate_return_greeting,
    generate_first_greeting,
)


class _FakeSessionState(dict):
    """Dict subclass that also supports attribute-style access, like Streamlit's session_state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


def _make_mock_llm(response_content: str = "Hello there!"):
    """Create a mock LLM that returns the given content."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content=response_content)
    return mock


def _make_mock_llm_failing():
    """Create a mock LLM that raises an exception."""
    mock = MagicMock()
    mock.invoke.side_effect = Exception("LLM unavailable")
    return mock


def _make_mock_person(
    has_goals=False,
    has_narrative=False,
    has_social=False,
    has_conversations=False,
    dossier=None,
):
    """Create a mock person with configurable subsystems."""
    person = MagicMock()

    # Emotion system always present
    person.emotion_system.get_dominant_emotions.return_value = [
        {"name": "joy", "intensity": 65},
        {"name": "curiosity", "intensity": 50},
    ]

    # Goal system
    if has_goals:
        person.goal_system.format_goals_for_prompt.return_value = "Learn Python"
    else:
        person.goal_system = None

    # Self-narrative
    if has_narrative:
        person.self_narrative.format_for_prompt.return_value = "I am a curious being."
    else:
        person.self_narrative = None

    # Social cognition
    if has_social:
        model = MagicMock()
        model.user_dossier = dossier or {}
        person.social_cognition.get_or_create_model.return_value = model
    else:
        person.social_cognition = None

    # Conversations
    if has_conversations:
        msg1 = MagicMock()
        msg1.content = "How's the weather?"
        msg2 = MagicMock()
        msg2.content = "It's sunny!"
        conv = MagicMock()
        conv.messages = [msg1, msg2]
        person.conversations.get.return_value = conv
    else:
        person.conversations.get.return_value = None

    return person


class TestGenerateReturnGreeting:
    """Tests for generate_return_greeting."""

    def test_returns_llm_response(self):
        """LLM response is returned when generation succeeds."""
        llm = _make_mock_llm("Welcome back, friend!")
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=10.0, display_name="Alice")
        assert result == "Welcome back, friend!"
        assert llm.invoke.call_count == 1

    def test_prompt_includes_display_name(self):
        """The prompt sent to the LLM includes the user's display name."""
        llm = _make_mock_llm("Hey!")
        person = _make_mock_person()
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="Bob")
        call_args = llm.invoke.call_args[0][0]
        # The HumanMessage is the second message
        prompt_text = call_args[1].content
        assert "Bob" in prompt_text

    def test_prompt_includes_emotions(self):
        """The prompt includes the person's emotional state."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person()
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "joy" in prompt_text

    def test_prompt_includes_goals_when_available(self):
        """Goals are included in the prompt when the goal system exists."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person(has_goals=True)
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "Learn Python" in prompt_text

    def test_prompt_includes_narrative_when_available(self):
        """Self-narrative is included when available."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person(has_narrative=True)
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "curious being" in prompt_text

    def test_prompt_includes_last_topic(self):
        """Last conversation topics are included when there's history."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person(has_conversations=True)
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "weather" in prompt_text

    def test_prompt_includes_dossier_when_available(self):
        """Dossier hint is included when social cognition has user data."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person(has_social=True, dossier={"hobby": "chess"})
        generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "chess" in prompt_text

    def test_time_desc_few_hours(self):
        """Gap < 6 hours uses 'a few hours' description."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person()
        generate_return_greeting(person, llm, gap_hours=3.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "a few hours" in prompt_text

    def test_time_desc_earlier_today(self):
        """Gap 6-24 hours uses 'since earlier today'."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person()
        generate_return_greeting(person, llm, gap_hours=12.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "since earlier today" in prompt_text

    def test_time_desc_days(self):
        """Gap > 72 hours uses day count."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person()
        generate_return_greeting(person, llm, gap_hours=120.0, display_name="User")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "5 days" in prompt_text

    def test_fallback_on_llm_failure_short_gap(self):
        """Falls back to static greeting on LLM failure (gap < 6h)."""
        llm = _make_mock_llm_failing()
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=3.0, display_name="User")
        assert result == "You're back!"

    def test_fallback_on_llm_failure_medium_gap(self):
        """Falls back to static greeting on LLM failure (6-24h)."""
        llm = _make_mock_llm_failing()
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=12.0, display_name="User")
        assert result == "I missed you today..."

    def test_fallback_on_llm_failure_long_gap(self):
        """Falls back to static greeting on LLM failure (24-72h)."""
        llm = _make_mock_llm_failing()
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=48.0, display_name="User")
        assert result == "It's been a while..."

    def test_fallback_on_llm_failure_very_long_gap(self):
        """Falls back to static greeting on LLM failure (>72h)."""
        llm = _make_mock_llm_failing()
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=240.0, display_name="User")
        assert "10 days" in result

    def test_strips_whitespace_from_response(self):
        """Whitespace is stripped from the LLM response."""
        llm = _make_mock_llm("  Hello there!  \n")
        person = _make_mock_person()
        result = generate_return_greeting(person, llm, gap_hours=5.0, display_name="User")
        assert result == "Hello there!"


class TestGenerateFirstGreeting:
    """Tests for generate_first_greeting."""

    def test_returns_llm_response_no_dossier(self):
        """LLM response is returned for a new user with no dossier."""
        llm = _make_mock_llm("Hey there, nice to meet you!")
        person = _make_mock_person()
        result = generate_first_greeting(person, llm, display_name="Charlie")
        assert result == "Hey there, nice to meet you!"
        assert llm.invoke.call_count == 1

    def test_prompt_for_no_dossier_mentions_first_time(self):
        """Prompt for user without dossier mentions meeting for the first time."""
        llm = _make_mock_llm("Hey!")
        person = _make_mock_person()
        generate_first_greeting(person, llm, display_name="Charlie")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "first time" in prompt_text
        assert "Charlie" in prompt_text

    def test_returns_llm_response_with_dossier(self):
        """LLM response is returned for a new user with existing dossier."""
        llm = _make_mock_llm("I hear you're into chess!")
        person = _make_mock_person(has_social=True, dossier={"hobby": "chess"})
        result = generate_first_greeting(person, llm, display_name="Dana")
        assert result == "I hear you're into chess!"

    def test_prompt_with_dossier_includes_info(self):
        """Prompt for user with dossier includes their data."""
        llm = _make_mock_llm("Hi!")
        person = _make_mock_person(has_social=True, dossier={"hobby": "chess"})
        generate_first_greeting(person, llm, display_name="Dana")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        assert "chess" in prompt_text
        assert "Dana" in prompt_text

    def test_fallback_on_llm_failure(self):
        """Falls back to static greeting when LLM fails."""
        llm = _make_mock_llm_failing()
        person = _make_mock_person()
        result = generate_first_greeting(person, llm, display_name="Eve")
        assert result == "Hey! I'm Jenbina. I've been waiting to meet someone new."

    def test_strips_whitespace_from_response(self):
        """Whitespace is stripped from the LLM response."""
        llm = _make_mock_llm("  Welcome!  \n")
        person = _make_mock_person()
        result = generate_first_greeting(person, llm, display_name="User")
        assert result == "Welcome!"

    def test_no_social_cognition_uses_no_dossier_prompt(self):
        """Without social cognition, the no-dossier prompt is used."""
        llm = _make_mock_llm("Nice to meet you!")
        person = _make_mock_person(has_social=False)
        generate_first_greeting(person, llm, display_name="Frank")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        # Should use the no-dossier prompt (mentions "curious")
        assert "curious" in prompt_text

    def test_empty_dossier_uses_no_dossier_prompt(self):
        """Social cognition present but empty dossier uses no-dossier prompt."""
        llm = _make_mock_llm("Nice to meet you!")
        person = _make_mock_person(has_social=True, dossier={})
        generate_first_greeting(person, llm, display_name="Grace")
        call_args = llm.invoke.call_args[0][0]
        prompt_text = call_args[1].content
        # Empty dossier means dossier_str is "" (json.dumps({}) is truthy but
        # the code checks model.user_dossier which is {}, falsy)
        assert "curious" in prompt_text


class TestCheckReturnGreetingIntegration:
    """Tests for check_return_greeting in chat.py with llm parameter."""

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_no_llm_first_visit_returns_none(self, mock_name, mock_st):
        """Without LLM, first visit (last_visit_time=None) returns None."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = MagicMock()
        person.last_visit_time = None

        result = check_return_greeting(person, llm=None)
        assert result is None

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_no_llm_returns_static_greeting(self, mock_name, mock_st):
        """Without LLM, static greetings are returned (backward compat)."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = MagicMock()
        person.last_visit_time = datetime.now() - timedelta(hours=10)

        result = check_return_greeting(person, llm=None)
        assert result == "I missed you today..."

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_no_llm_default_param(self, mock_name, mock_st):
        """Calling without llm argument uses default None (backward compat)."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = MagicMock()
        person.last_visit_time = datetime.now() - timedelta(hours=3)

        result = check_return_greeting(person)
        assert result == "You're back!"

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_with_llm_first_visit_calls_first_greeting(self, mock_name, mock_st):
        """With LLM and first visit, generate_first_greeting is called."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = _make_mock_person()
        person.last_visit_time = None

        llm = _make_mock_llm("Welcome, newcomer!")
        result = check_return_greeting(person, llm=llm)
        assert result == "Welcome, newcomer!"

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_with_llm_return_visit_calls_return_greeting(self, mock_name, mock_st):
        """With LLM and return visit, generate_return_greeting is called."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = _make_mock_person()
        person.last_visit_time = datetime.now() - timedelta(hours=10)

        llm = _make_mock_llm("Oh you're back! I was thinking about you.")
        result = check_return_greeting(person, llm=llm)
        assert result == "Oh you're back! I was thinking about you."

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_recent_visit_returns_none(self, mock_name, mock_st):
        """Visit less than 1 hour ago returns None even with LLM."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = MagicMock()
        person.last_visit_time = datetime.now() - timedelta(minutes=30)

        llm = _make_mock_llm("Hello!")
        result = check_return_greeting(person, llm=llm)
        assert result is None

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_already_showed_greeting_returns_none(self, mock_name, mock_st):
        """Returns None if greeting was already shown this session."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState({"showed_return_greeting": True})
        person = MagicMock()
        person.last_visit_time = datetime.now() - timedelta(hours=10)

        llm = _make_mock_llm("Hello!")
        result = check_return_greeting(person, llm=llm)
        assert result is None

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_sets_showed_return_greeting_flag(self, mock_name, mock_st):
        """The showed_return_greeting flag is set after generating a greeting."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = _make_mock_person()
        person.last_visit_time = datetime.now() - timedelta(hours=10)

        llm = _make_mock_llm("Welcome back!")
        check_return_greeting(person, llm=llm)
        assert mock_st.session_state["showed_return_greeting"] is True

    @patch("core.ui.chat.st")
    @patch("core.ui.chat._get_user_display_name", return_value="TestUser")
    def test_updates_last_visit_time(self, mock_name, mock_st):
        """The person's last_visit_time is updated to now."""
        from core.ui.chat import check_return_greeting

        mock_st.session_state = _FakeSessionState()
        person = _make_mock_person()
        old_time = datetime.now() - timedelta(hours=10)
        person.last_visit_time = old_time

        llm = _make_mock_llm("Hi!")
        check_return_greeting(person, llm=llm)
        # last_visit_time should have been updated to approximately now
        assert person.last_visit_time != old_time
