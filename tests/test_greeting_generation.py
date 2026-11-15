"""Tests for GPT-generated greeting functions."""

import unittest
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


class TestCheckReturnGreetingIntegration(unittest.TestCase):
    """Greeting visits belong to the partner's social model."""

    NOW = datetime(2026, 11, 15, 12, 0)

    def setUp(self):
        from core.person.person import Person
        from core.ui.chat import check_return_greeting

        self.check = check_return_greeting
        self.person = Person()
        self.person.init_social_cognition()
        self.model = self.person.social_cognition.get_or_create_model("TestUser")
        self.st_patch = patch("core.ui.chat.st")
        self.st = self.st_patch.start()
        self.addCleanup(self.st_patch.stop)
        self.st.session_state = _FakeSessionState()

    def test_no_llm_first_visit_returns_none(self):
        self.assertIsNone(self.check(self.person, None, "TestUser", now=self.NOW))
        self.assertTrue(self.st.session_state.showed_return_greeting)

    def test_no_llm_returns_static_greeting(self):
        self.model.last_visit_time = self.NOW - timedelta(hours=10)
        self.assertEqual(self.check(self.person, None, "TestUser", now=self.NOW), "I missed you today...")

    def test_no_llm_static_greetings_cover_each_gap(self):
        for hours, expected in (
            (3, "You're back!"),
            (48, "It's been a while..."),
            (96, "I was worried you forgot about me... it's been 4 days."),
        ):
            with self.subTest(hours=hours):
                self.st.session_state = _FakeSessionState()
                self.model.last_visit_time = self.NOW - timedelta(hours=hours)
                self.assertEqual(self.check(self.person, None, "TestUser", now=self.NOW), expected)

    def test_with_llm_first_visit_calls_first_greeting(self):
        llm = _make_mock_llm("Welcome, newcomer!")
        self.assertEqual(self.check(self.person, llm, "TestUser", now=self.NOW), "Welcome, newcomer!")
        self.assertIn("TestUser", llm.invoke.call_args.args[0][1].content)
        self.assertIn("first time", llm.invoke.call_args.args[0][1].content)

    def test_with_llm_return_visit_calls_return_greeting(self):
        self.model.last_visit_time = self.NOW - timedelta(hours=10)
        llm = _make_mock_llm("Oh you're back! I was thinking about you.")
        self.assertEqual(self.check(self.person, llm, "TestUser", now=self.NOW), "Oh you're back! I was thinking about you.")
        self.assertIn("TestUser", llm.invoke.call_args.args[0][1].content)
        self.assertIn("returning", llm.invoke.call_args.args[0][1].content)

    def test_recent_visit_returns_none(self):
        self.model.last_visit_time = self.NOW - timedelta(minutes=30)
        llm = _make_mock_llm("Hello!")
        self.assertIsNone(self.check(self.person, llm, "TestUser", now=self.NOW))
        llm.invoke.assert_not_called()

    def test_already_showed_greeting_returns_none(self):
        self.st.session_state.showed_return_greeting = True
        old_time = self.NOW - timedelta(hours=10)
        self.model.last_visit_time = old_time
        llm = _make_mock_llm("Hello!")
        self.assertIsNone(self.check(self.person, llm, "TestUser", now=self.NOW))
        self.assertEqual(self.model.last_visit_time, old_time)
        llm.invoke.assert_not_called()

    def test_sets_showed_return_greeting_flag(self):
        self.model.last_visit_time = self.NOW - timedelta(hours=10)
        self.check(self.person, _make_mock_llm("Welcome back!"), "TestUser", now=self.NOW)
        self.assertTrue(self.st.session_state.showed_return_greeting)

    def test_updates_last_visit_time(self):
        self.model.last_visit_time = self.NOW - timedelta(hours=10)
        self.check(self.person, _make_mock_llm("Hi!"), "TestUser", now=self.NOW)
        self.assertEqual(self.model.last_visit_time, self.NOW)

    def test_last_visit_is_per_person(self):
        self.check(self.person, None, "Ann", now=self.NOW)
        self.assertEqual(self.person.social_cognition.get_or_create_model("Ann").last_visit_time, self.NOW)
        self.assertIsNone(self.person.social_cognition.get_or_create_model("Bob").last_visit_time)
        self.assertIsNone(self.person.last_visit_time)

    def test_time_defaults_to_now(self):
        with patch("core.ui.chat.datetime") as clock:
            clock.now.return_value = self.NOW
            self.check(self.person, None, "TestUser")
        self.assertEqual(self.model.last_visit_time, self.NOW)
