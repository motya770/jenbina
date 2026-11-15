"""Private conversation content must stay out of another person's prompts."""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from core.interaction.chat_handler import (
    generate_first_greeting,
    generate_proactive_message,
    generate_return_greeting,
    handle_chat_interaction,
)
from core.person.person import Person


SECRETS = ["ANN-MESSAGE-TEXT", "ANN-BELIEF", "ANN-DOSSIER-FACT"]


def two_people():
    person = Person()
    person.init_social_cognition()
    person.init_self_narrative()
    person.init_curiosity_system()
    person.init_social_interaction_tracker()
    person.receive_message("Ann", "ANN-MESSAGE-TEXT")
    person.send_message("Ann", "reply to ANN-MESSAGE-TEXT")
    ann = person.social_cognition.get_or_create_model("Ann")
    ann.beliefs.append("ANN-BELIEF")
    ann.user_dossier = {"job": "ANN-DOSSIER-FACT"}
    person.social_interaction_tracker.record_chat("Ann", "warm")
    person.receive_message("Bob", "hello from Bob")
    person.social_cognition.get_or_create_model("Bob").user_dossier = {"job": "baker"}
    return person


class CapturingLLM:
    def __init__(self):
        self.prompts = []
        self.calls = []

    def invoke(self, messages):
        contents = [message.content for message in messages]
        self.calls.append(contents)
        self.prompts.extend(contents)
        return SimpleNamespace(content="ok")


class TestNothingCrossesBetweenPeople(unittest.TestCase):
    def assert_clean(self, llm):
        sent = "\n".join(llm.prompts)
        self.assertTrue(sent)
        for secret in SECRETS:
            self.assertNotIn(secret, sent)

    def chat_with_bob(self, person, llm):
        return handle_chat_interaction(
            st=MagicMock(), llm=llm, needs_response={}, world_description="{}",
            action_decision={}, user_input="what did you do today?",
            person_state=person.get_current_state(partner="Bob"),
            conversation_context="Bob: hello from Bob", memory_manager=None,
            user_id=2, person=person, conversation_partner_name="Bob",
        )

    def test_chat_reply_and_insight_prompts(self):
        person = two_people()
        llm = CapturingLLM()
        person.init_insight_system(llm)
        result = self.chat_with_bob(person, llm)
        self.assertEqual(result["insight"], "ok")
        self.assertEqual(len(llm.calls), 2)
        self.assertIn("baker", "\n".join(llm.calls[0]))
        self.assertFalse(person.insight_system.should_generate_first_impression(
            {"job": "baker"}, person_key="Bob",
        ))
        self.assert_clean(llm)
        self.assertIn("Ann", "\n".join(llm.prompts))

    def test_second_message_subtle_insight_prompt(self):
        person = two_people()
        llm = CapturingLLM()
        person.init_insight_system(llm)
        person.insight_system.generate_first_impression(
            {"job": "baker"}, "hello from Bob", person_key="Bob",
        )
        llm.prompts.clear()
        llm.calls.clear()
        person.send_message("Bob", "hi Bob")
        person.receive_message("Bob", "what did you do today?")
        result = self.chat_with_bob(person, llm)
        self.assertEqual(result["insight"], "ok")
        self.assertEqual(len(llm.calls), 2)
        insight_prompt = "\n".join(llm.calls[0])
        self.assertIn("Recent conversation:", insight_prompt)
        self.assertIn("hello from Bob", insight_prompt)
        self.assertIn("baker", insight_prompt)
        self.assert_clean(llm)
        self.assertIn("Ann", "\n".join(llm.prompts))

    def test_greeting_prompts(self):
        for generate in (
            lambda p, llm: generate_return_greeting(p, llm, 30.0, "Bob"),
            lambda p, llm: generate_first_greeting(p, llm, "Bob"),
        ):
            with self.subTest(generate=generate):
                llm = CapturingLLM()
                self.assertEqual(generate(two_people(), llm), "ok")
                self.assertEqual(len(llm.calls), 1)
                self.assertIn("baker", "\n".join(llm.prompts))
                self.assert_clean(llm)

    def test_proactive_prompt(self):
        llm = CapturingLLM()
        result = generate_proactive_message(
            two_people(), llm,
            {"low_social": {"need": "friendship", "satisfaction": 20}},
            display_name="Bob",
        )
        self.assertEqual(result, "ok")
        self.assertEqual(len(llm.calls), 1)
        self.assert_clean(llm)
        self.assertIn("Ann", "\n".join(llm.prompts))

    def test_unfiltered_state_would_leak(self):
        person = two_people()
        self.assertIn("ANN-BELIEF", json.dumps(person.social_cognition.get_stats(), default=str))
        self.assertIn("ANN-DOSSIER-FACT", json.dumps(person.social_cognition.get_stats(), default=str))
        self.assertIn("ANN-MESSAGE-TEXT", person.conversations["Ann"].messages[0].content)
