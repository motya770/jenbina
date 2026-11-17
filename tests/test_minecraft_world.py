#!/usr/bin/env python3
"""Tests for Jenbina's Minecraft world. A fake bridge stands in for the Node
process, so nothing here touches the network or a Minecraft server."""

import io
import json
import os
import sys
import unittest
import urllib.error
from contextlib import ExitStack
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.dirname(__file__))

from core.environment.minecraft import (
    MinecraftBridge, MinecraftWorld, WorldUnavailable, build_scene, resolve_action, world_from_env,
)
from core.environment.minecraft.provider import UNCLEAR_CHOICE
from core.environment.minecraft.scene import HOME_PLACE, celsius, place_label, time_of_day
from core.environment.world_state import get_world_state_summary
from core.heartbeat.rhythm import RhythmConfig, Situation
from core.person.person import Person
from core.timeline import EventLog
from core.timeline.events import make_action
from core.ui.rail import env_line_html
from core.ui.timeline import action_details_text
from test_simulation_runner import ACTION, build_env

NOON = datetime(2026, 11, 17, 12, 0)
MIDNIGHT = datetime(2026, 11, 17, 0, 30)
HOME = [-144, 65, 157]


def observation(**changes):
    base = {
        "position": {"x": -144, "y": 65, "z": 157},
        "biome": "birch_forest", "temperature": 0.6,
        "sky": {"is_day": True, "time_of_day": 2500, "raining": False},
        "health": 20, "food": 20,
        "inventory": {},
        "nearby": {"logs": 0, "stone": False, "water": False, "animals": [], "hostiles": [],
                   "crafting_table": False},
        "craftable": [],
        "sheltered": False,
    }
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = {**base[key], **value}
        else:
            base[key] = value
    return base


def labels(obs, home=HOME, can_sleep=False):
    return build_scene(obs, home, NOON, can_sleep).labels


class FakeBridge:
    """Records every call; answers with whatever the test sets."""

    def __init__(self, obs=None):
        self.observation = obs if obs is not None else observation()
        self.result = {"ok": True, "summary": "Chopped wood from the trees. Gained 4 oak logs.",
                       "died": False}
        self.calls = []
        self.fail_start = False
        self.fail_act = False

    def start_session(self):
        self.calls.append("start")
        if self.fail_start:
            raise WorldUnavailable("server is down")
        return self.observation

    def end_session(self):
        self.calls.append("end")

    def act(self, name, args=None, budget_ms=45000):
        self.calls.append(("act", name, dict(args or {})))
        if self.fail_act:
            raise WorldUnavailable("lost the connection")
        return dict(self.result)


class TestPlaceAndScene(unittest.TestCase):
    def test_place_is_home_near_home_and_the_biome_elsewhere(self):
        self.assertEqual(place_label(observation(), HOME), HOME_PLACE)
        far = observation(position={"x": -100, "y": 65, "z": 157})
        self.assertEqual(place_label(far, HOME), "Birch forest")
        self.assertEqual(place_label(far, None), "Birch forest")
        self.assertEqual(place_label(observation(biome="unknown"), None), "The wild")

    def test_height_does_not_count_toward_distance_from_home(self):
        deep = observation(position={"x": -144, "y": 20, "z": 157})
        self.assertEqual(place_label(deep, HOME), HOME_PLACE)

    def test_scene_describes_body_inventory_and_surroundings(self):
        obs = observation(
            food=14, inventory={"oak_planks": 12, "wooden_pickaxe": 1},
            nearby={"logs": 5, "water": True, "animals": [{"name": "cow", "distance": 9}]},
        )
        text = " ".join(build_scene(obs, HOME, NOON).descriptions)
        self.assertIn("You are at Home.", text)
        self.assertIn("health 20/20, food 14/20", text)
        self.assertIn("12 oak planks", text)
        self.assertIn("1 wooden pickaxe", text)
        self.assertIn("Trees stand close by.", text)
        self.assertIn("A cow is 9 blocks away.", text)

    def test_scene_says_how_far_home_is_and_when_it_is_dark(self):
        obs = observation(position={"x": -104, "y": 65, "z": 157}, sky={"is_day": False})
        text = " ".join(build_scene(obs, HOME, NOON).descriptions)
        self.assertIn("You are in birch forest. Home is 40 blocks away.", text)
        self.assertIn("It is dark here.", text)

    def test_world_state_reads_like_any_other_world(self):
        scene = build_scene(observation(food=15, health=18), HOME, NOON)
        summary = get_world_state_summary(scene.world_state)
        self.assertEqual(summary["location"]["name"], HOME_PLACE)
        self.assertEqual(summary["time"]["time_of_day"], "afternoon")
        self.assertEqual(summary["weather"]["description"], "clear sky")
        self.assertEqual(summary["weather"]["temperature"], 15.0)
        self.assertEqual(scene.body, {"health": 18, "food": 15})

    def test_time_of_day_is_her_own_clock_not_the_minecraft_sky(self):
        night_sky = observation(sky={"is_day": False})
        scene = build_scene(night_sky, HOME, NOON)
        self.assertEqual(scene.world_state.time_data.time_of_day, "afternoon")
        self.assertEqual(scene.world_state.weather_data.description, "dark sky")
        self.assertEqual(time_of_day(MIDNIGHT), "night")

    def test_temperature_is_nominal_and_bounded(self):
        self.assertEqual(celsius({"temperature": 0.8}), 20.0)
        self.assertEqual(celsius({"temperature": 2.0}), 40.0)
        self.assertEqual(celsius({"temperature": -0.7}), -15.0)
        self.assertEqual(celsius({"temperature": None}), 18.0)

    def test_description_data_has_the_shape_the_decision_chain_reads(self):
        scene = build_scene(observation(), HOME, NOON)
        data = scene.description_data()
        self.assertEqual(data["list_of_actions"], scene.labels)
        self.assertEqual(data["list_of_descriptions"], scene.descriptions)


class TestAvailableActions(unittest.TestCase):
    def test_a_bare_world_still_offers_exploring_looking_and_resting(self):
        offered = labels(observation())
        for direction in ("north", "east", "south", "west"):
            self.assertIn(f"Explore to the {direction}", offered)
        self.assertIn("Look around and take in the surroundings", offered)
        self.assertIn("Rest for a while", offered)
        self.assertEqual(len(offered), len(set(offered)))

    def test_eating_needs_food_carried_and_an_empty_enough_stomach(self):
        full = observation(inventory={"beef": 2})
        hungry = observation(inventory={"beef": 2, "cooked_beef": 1}, food=12)
        self.assertNotIn("Eat the beef you are carrying", labels(full))
        self.assertIn("Eat the cooked beef you are carrying", labels(hungry))
        self.assertFalse(any(label.startswith("Eat") for label in labels(observation(food=5))))

    def test_wood_water_and_animals_are_offered_only_when_present(self):
        nothing = labels(observation())
        for label in ("Chop wood from the trees nearby", "Drink from the water nearby"):
            self.assertNotIn(label, nothing)
        offered = labels(observation(nearby={
            "logs": 3, "water": True, "animals": [{"name": "sheep", "distance": 6}]}))
        self.assertIn("Chop wood from the trees nearby", offered)
        self.assertIn("Drink from the water nearby", offered)
        self.assertIn("Hunt the sheep nearby for food", offered)

    def test_at_most_four_crafts_are_offered_best_first(self):
        obs = observation(craftable=["planks", "stick", "crafting_table", "wooden_axe",
                                     "wooden_sword", "stone_pickaxe"])
        crafts = [a for a in build_scene(obs, HOME, NOON).actions if a.name == "craft"]
        self.assertEqual([a.args["item"] for a in crafts],
                         ["stone_pickaxe", "planks", "crafting_table", "stick"])
        self.assertEqual([a.label for a in crafts], [
            "Craft a stone pickaxe", "Turn your logs into planks", "Craft a crafting table", "Craft sticks"])

    def test_mining_needs_a_pickaxe_and_stone(self):
        label = "Mine stone with your pickaxe"
        self.assertNotIn(label, labels(observation(nearby={"stone": True})))
        self.assertNotIn(label, labels(observation(inventory={"wooden_pickaxe": 1})))
        self.assertIn(label, labels(observation(inventory={"wooden_pickaxe": 1}, nearby={"stone": True})))

    def test_walking_home_is_offered_only_far_from_a_known_home(self):
        far = observation(position={"x": -100, "y": 70, "z": 157})
        self.assertNotIn("Walk back home", labels(observation()))
        self.assertNotIn("Walk back home", labels(far, home=None))
        scene = build_scene(far, HOME, NOON)
        action = next(a for a in scene.actions if a.name == "go_home")
        self.assertEqual(action.args, {"x": -144, "y": 65, "z": 157})

    def test_shelter_is_offered_only_when_a_monster_is_near_and_she_is_exposed(self):
        label = "Dig a burrow and shelter in it"
        monster = {"hostiles": [{"name": "zombie", "distance": 10}]}
        self.assertNotIn(label, labels(observation(sky={"is_day": False})))
        self.assertIn(label, labels(observation(nearby=monster)))
        self.assertNotIn(label, labels(observation(nearby=monster, sheltered=True)))

    def test_sleep_is_offered_only_when_the_caller_says_she_can(self):
        label = "Go to sleep for the night"
        self.assertNotIn(label, labels(observation()))
        self.assertIn(label, labels(observation(), can_sleep=True))

    def test_every_action_has_a_need_key_the_executor_knows(self):
        from core.needs.maslow_decision_chain import create_maslow_action_executor
        obs = observation(
            food=10, inventory={"beef": 1, "wooden_pickaxe": 1}, position={"x": -100, "y": 65, "z": 157},
            nearby={"logs": 2, "stone": True, "water": True, "animals": [{"name": "pig", "distance": 4}],
                    "hostiles": [{"name": "zombie", "distance": 9}]},
            craftable=["stick"],
        )
        person = Person()
        executor = create_maslow_action_executor(person.maslow_needs)
        for action in build_scene(obs, HOME, NOON, can_sleep=True).actions:
            with self.subTest(action=action.label):
                self.assertTrue(executor(action.need_key).get("satisfied_needs"))


class TestResolveAction(unittest.TestCase):
    def setUp(self):
        self.actions = build_scene(
            observation(nearby={"logs": 3, "water": True}, craftable=["stick"]), HOME, NOON).actions

    def resolve(self, text):
        action = resolve_action(self.actions, text)
        return action.label if action is not None else None

    def test_exact_label_ignoring_case_and_punctuation(self):
        self.assertEqual(self.resolve("chop wood from the trees nearby."), "Chop wood from the trees nearby")

    def test_label_inside_a_longer_sentence(self):
        self.assertEqual(self.resolve("I will explore to the north, carefully"), "Explore to the north")

    def test_a_shortened_choice_inside_a_label(self):
        self.assertEqual(self.resolve("Drink from the water"), "Drink from the water nearby")

    def test_a_close_paraphrase(self):
        self.assertEqual(self.resolve("Rest for a little while"), "Rest for a while")

    def test_something_the_world_does_not_offer(self):
        self.assertIsNone(self.resolve("Walk to Coupa Cafe for coffee"))
        self.assertIsNone(self.resolve(""))
        self.assertIsNone(self.resolve(None))


class ProviderCase(unittest.TestCase):
    def setUp(self):
        self.bridge = FakeBridge()
        self.now = NOON
        self.world = MinecraftWorld(self.bridge, clock=lambda: self.now)
        self.person = Person()
        self.memory = {}
        self.config = RhythmConfig()


class TestObserve(ProviderCase):
    def test_she_logs_in_looks_and_logs_out(self):
        scene = self.world.observe(self.person, self.memory)
        self.assertEqual(self.bridge.calls, ["start", "end"])
        self.assertEqual(scene.place, HOME_PLACE)

    def test_staying_online_skips_the_logout(self):
        MinecraftWorld(self.bridge, stay_online=True).observe(self.person, self.memory)
        self.assertEqual(self.bridge.calls, ["start"])

    def test_first_observation_becomes_home_and_later_ones_do_not_move_it(self):
        self.world.observe(self.person, self.memory)
        self.assertEqual(self.memory["minecraft"]["home"], HOME)
        self.bridge.observation = observation(position={"x": 5, "y": 70, "z": 5})
        scene = self.world.observe(self.person, self.memory)
        self.assertEqual(self.memory["minecraft"]["home"], HOME)
        self.assertEqual(scene.place, "Birch forest")

    def test_hunger_follows_the_food_bar(self):
        self.bridge.observation = observation(food=5)
        self.world.observe(self.person, self.memory)
        self.assertEqual(self.person.maslow_needs.get_need_satisfaction("hunger"), 25.0)

    def test_an_unreachable_world_raises_and_still_logs_out(self):
        self.bridge.fail_start = True
        with self.assertRaises(WorldUnavailable):
            self.world.observe(self.person, self.memory)
        self.assertEqual(self.bridge.calls, ["start", "end"])
        self.assertEqual(self.memory, {})

    def test_sleep_is_offered_exactly_when_she_would_fall_asleep(self):
        label = "Go to sleep for the night"
        rested = self.person.maslow_needs.needs["sleep"]
        rested.satisfaction = 90.0
        self.assertNotIn(label, self.world.observe(self.person, self.memory, self.config).labels)
        self.assertNotIn(label, self.world.observe(self.person, self.memory, None).labels)
        rested.satisfaction = self.config.low_sleep_need - 1
        self.assertIn(label, self.world.observe(self.person, self.memory, self.config).labels)
        rested.satisfaction = 90.0
        self.now = MIDNIGHT
        self.assertIn(label, self.world.observe(self.person, self.memory, self.config).labels)
        awake = RhythmConfig(sleep_enabled=False)
        self.assertNotIn(label, self.world.observe(self.person, self.memory, awake).labels)


class TestPerform(ProviderCase):
    def setUp(self):
        super().setUp()
        self.bridge.observation = observation(nearby={"logs": 4})
        self.scene = self.world.observe(self.person, self.memory, self.config)
        self.bridge.calls.clear()

    def notes(self):
        return " ".join(note["content"] for note in self.person.working_memory.notes)

    def test_a_successful_action_runs_in_one_short_session(self):
        outcome = self.world.perform(self.scene, "Chop wood from the trees nearby", self.person, self.memory)
        self.assertEqual(self.bridge.calls, ["start", ("act", "gather_wood", {}), "end"])
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.need_key, "work_on_goals")
        self.assertEqual(outcome.summary, "Chopped wood from the trees. Gained 4 oak logs.")
        self.assertIn("Gained 4 oak logs", self.notes())

    def test_action_arguments_reach_the_bridge(self):
        self.world.perform(self.scene, "Explore to the east", self.person, self.memory)
        self.assertIn(("act", "explore", {"direction": "east"}), self.bridge.calls)

    def test_a_failed_action_earns_nothing(self):
        self.bridge.result = {"ok": False, "summary": "Could not reach any wood.", "died": False}
        outcome = self.world.perform(self.scene, "Chop wood from the trees nearby", self.person, self.memory)
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.need_key)
        self.assertIn("Could not reach any wood.", self.notes())

    def test_a_choice_the_world_does_not_offer_is_not_sent(self):
        outcome = self.world.perform(self.scene, "Walk to Coupa Cafe", self.person, self.memory)
        self.assertEqual(self.bridge.calls, [])
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.need_key)
        self.assertEqual(outcome.summary, UNCLEAR_CHOICE)
        self.assertEqual(outcome.place, HOME_PLACE)

    def test_sleep_never_reaches_the_bridge(self):
        self.now = MIDNIGHT
        scene = self.world.observe(self.person, self.memory, self.config)
        self.bridge.calls.clear()
        outcome = self.world.perform(scene, "Go to sleep for the night", self.person, self.memory)
        self.assertEqual(self.bridge.calls, [])
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.need_key, "sleep")

    def test_losing_the_world_mid_action_is_a_failed_outcome_not_an_error(self):
        self.bridge.fail_act = True
        outcome = self.world.perform(self.scene, "Rest for a while", self.person, self.memory)
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.need_key)
        self.assertEqual(self.bridge.calls[-1], "end")

    def test_dying_costs_security_is_counted_and_earns_nothing(self):
        security = self.person.maslow_needs.needs["security"]
        security.satisfaction = 80.0
        self.bridge.result = {"ok": False, "summary": "Died and woke up again at the spawn point.",
                              "died": True, "observation": observation(position={"x": 0, "y": 80, "z": 0})}
        outcome = self.world.perform(self.scene, "Rest for a while", self.person, self.memory)
        self.assertTrue(outcome.died)
        self.assertIsNone(outcome.need_key)
        self.assertEqual(security.satisfaction, 50.0)
        self.assertEqual(self.memory["minecraft"]["deaths"], 1)
        self.assertEqual(outcome.place, "Birch forest")
        self.assertIn("I died in the world", self.notes())

    def test_the_body_and_place_come_from_the_observation_after_the_action(self):
        self.bridge.result = {"ok": True, "summary": "Walked 40 blocks east.", "died": False,
                              "observation": observation(food=8, biome="plains",
                                                         position={"x": -104, "y": 65, "z": 157})}
        outcome = self.world.perform(self.scene, "Explore to the east", self.person, self.memory)
        self.assertEqual(outcome.place, "Plains")
        self.assertEqual(self.person.maslow_needs.get_need_satisfaction("hunger"), 40.0)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class TestBridgeClient(unittest.TestCase):
    def client(self, payload=None, error=None):
        self.requests = []

        def opener(request, timeout):
            self.requests.append((request.get_method(), request.full_url, request.data, timeout))
            if error is not None:
                raise error
            return FakeResponse(json.dumps(payload).encode())

        return MinecraftBridge("http://127.0.0.1:3010/", opener=opener)

    def test_start_session_returns_the_observation(self):
        bridge = self.client({"ok": True, "observation": {"food": 20}})
        self.assertEqual(bridge.start_session(), {"food": 20})
        method, url, _, _ = self.requests[0]
        self.assertEqual((method, url), ("POST", "http://127.0.0.1:3010/session/start"))

    def test_a_session_without_an_observation_is_unavailable(self):
        with self.assertRaises(WorldUnavailable):
            self.client({"ok": True}).start_session()

    def test_act_sends_the_routine_and_waits_past_its_budget(self):
        bridge = self.client({"ok": True, "summary": "Rested for a while."})
        bridge.act("rest", {"a": 1}, budget_ms=20000)
        method, url, data, timeout = self.requests[0]
        self.assertEqual((method, url), ("POST", "http://127.0.0.1:3010/act"))
        self.assertEqual(json.loads(data), {"name": "rest", "args": {"a": 1}, "budget_ms": 20000})
        self.assertEqual(timeout, 50.0)

    def test_a_refusal_carries_the_bridge_message(self):
        refusal = urllib.error.HTTPError(
            "http://x", 409, "Conflict", None,
            io.BytesIO(json.dumps({"message": "She is already in the middle of something."}).encode()))
        with self.assertRaises(WorldUnavailable) as raised:
            self.client(error=refusal).observe()
        self.assertIn("already in the middle of something", str(raised.exception))

    def test_no_bridge_at_all_is_unavailable(self):
        for error in (urllib.error.URLError("connection refused"), TimeoutError("timed out")):
            with self.subTest(error=error), self.assertRaises(WorldUnavailable):
                self.client(error=error).health()

    def test_an_answer_that_is_not_json_is_unavailable(self):
        bridge = MinecraftBridge(opener=lambda request, timeout: FakeResponse(b"<html>"))
        with self.assertRaises(WorldUnavailable):
            bridge.observe()

    def test_ending_a_session_never_raises(self):
        self.client(error=urllib.error.URLError("gone")).end_session()


class TestWorldFromEnv(unittest.TestCase):
    def test_palo_alto_is_the_default(self):
        self.assertIsNone(world_from_env({}))
        self.assertIsNone(world_from_env({"JENBINA_WORLD": "palo_alto"}))

    def test_minecraft_builds_a_world_with_the_configured_bridge(self):
        world = world_from_env({"JENBINA_WORLD": " Minecraft ",
                                "JENBINA_MINECRAFT_BRIDGE_URL": "http://127.0.0.1:4000"})
        self.assertIsInstance(world, MinecraftWorld)
        self.assertEqual(world.bridge.base_url, "http://127.0.0.1:4000")
        self.assertFalse(world.stay_online)

    def test_stay_online_is_opt_in(self):
        world = world_from_env({"JENBINA_WORLD": "minecraft", "JENBINA_MINECRAFT_STAY_ONLINE": "1"})
        self.assertTrue(world.stay_online)
        self.assertEqual(world.bridge.base_url, "http://127.0.0.1:3010")


class TestRunnerInMinecraft(unittest.TestCase):
    """The real runner with every LLM chain mocked and a fake bridge for a world."""

    def setUp(self):
        import core.simulation_runner as runner
        self.runner = runner
        self.person, self.meta, patches = build_env(runner)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patches)
        self.world_chain = self.stack.enter_context(patch.object(runner, "create_world_description_system"))
        self.decide = self.stack.enter_context(patch.object(
            runner, "create_meta_cognitive_action_chain",
            return_value={"chosen_action": "Chop wood from the trees nearby", "reasoning": "need wood"},
        ))
        self.emotion = self.stack.enter_context(patch.object(
            runner, "analyze_emotion_impact", return_value={"joy": 4}))
        self.stack.enter_context(patch.object(runner, "get_llm"))
        self.bridge = FakeBridge(observation(food=16, nearby={"logs": 4}))
        self.world = MinecraftWorld(self.bridge, clock=lambda: NOON)
        self.situation_world = {}
        self.context = {
            "simulation_history": [], "jenbina_location": "Jenbina's House", "debug_iterations": [],
            "event_log": EventLog(), "sleep_config": RhythmConfig(),
            "world_provider": self.world, "world_memory": self.situation_world,
        }

    def run_beat(self):
        return self.runner.run_single_iteration_headless(self.person, MagicMock(), self.meta, 0, self.context)

    def action_event(self):
        return next(e for e in self.context["event_log"].recent() if e.kind == "action")

    def test_the_scene_comes_from_the_world_not_from_an_llm(self):
        result = self.run_beat()
        self.world_chain.assert_not_called()
        scene = json.loads(result["world_description"])
        self.assertIn("Chop wood from the trees nearby", scene["list_of_actions"])
        self.assertEqual(self.decide.call_args.kwargs["world_description"], result["world_description"])
        self.assertEqual(result["world_summary"]["location"]["name"], HOME_PLACE)
        self.assertEqual(result["world_summary"]["body"], {"health": 20, "food": 16})

    def test_she_is_credited_for_what_happened(self):
        esteem_before = self.person.maslow_needs.get_need_satisfaction("self_esteem")
        result = self.run_beat()
        self.assertEqual(result["matched_action"], "work_on_goals")
        self.assertEqual(result["world_outcome"]["ok"], True)
        self.assertEqual(result["action_decision"]["outcome"],
                         "Chopped wood from the trees. Gained 4 oak logs.")
        self.assertGreater(self.person.maslow_needs.get_need_satisfaction("self_esteem"), esteem_before)
        self.assertEqual(self.bridge.calls, ["start", "end", "start", ("act", "gather_wood", {}), "end"])

    def test_a_failed_action_credits_nothing(self):
        self.bridge.result = {"ok": False, "summary": "Could not reach any wood.", "died": False}
        result = self.run_beat()
        self.assertIsNone(result["matched_action"])
        self.assertEqual(result["world_outcome"]["ok"], False)

    def test_keywords_in_her_words_earn_nothing_in_a_real_world(self):
        self.decide.return_value = {"chosen_action": "Eat a big dinner and sleep", "reasoning": "hungry"}
        result = self.run_beat()
        self.assertIsNone(result["matched_action"])
        self.assertEqual(result["action_decision"]["outcome"], UNCLEAR_CHOICE)
        self.assertNotIn(("act", "eat", {}), self.bridge.calls)

    def test_hunger_is_the_bodys_and_is_not_decayed_by_the_clock(self):
        self.run_beat()
        self.assertEqual(self.person.maslow_needs.get_need_satisfaction("hunger"), 80.0)

    def test_the_outcome_reaches_the_timeline_and_the_emotion_analysis(self):
        self.run_beat()
        self.assertEqual(self.action_event().detail["outcome"],
                         "Chopped wood from the trees. Gained 4 oak logs.")
        self.assertIn("What happened: Chopped wood from the trees.",
                      self.emotion.call_args.kwargs["situation"])

    def test_her_location_becomes_the_place_she_stands_in(self):
        self.run_beat()
        self.assertEqual(self.context["jenbina_location"], HOME_PLACE)
        moves = [e for e in self.context["event_log"].recent() if e.kind == "move"]
        self.assertEqual(len(moves), 1)

    def test_only_her_latest_action_counts_as_recent(self):
        self.context["simulation_history"] = [
            {"action_decision": {"chosen_action": name}}
            for name in ("Explore to the north", "Rest for a while", "Chop wood from the trees nearby")
        ]
        self.run_beat()
        self.assertEqual(self.decide.call_args.kwargs["recent_actions"], ["Chop wood from the trees nearby"])

    def test_the_planner_is_told_what_this_world_offers(self):
        with patch.object(self.person.planning_system, "check_for_replan", return_value=None) as replan:
            self.run_beat()
        offered = replan.call_args.kwargs["world_context"]["possible_actions"]
        self.assertIn("Chop wood from the trees nearby", offered)
        self.assertIn("Rest for a while", offered)

    def test_an_unreachable_world_stops_the_beat_before_any_llm_call(self):
        self.bridge.fail_start = True
        needs_chain = self.stack.enter_context(patch.object(self.runner, "create_basic_needs_chain"))
        with self.assertRaises(WorldUnavailable):
            self.run_beat()
        needs_chain.assert_not_called()
        self.decide.assert_not_called()
        self.assertEqual(self.context["event_log"].recent(), [])

    def test_choosing_sleep_at_night_falls_asleep_without_touching_the_world(self):
        self.world.clock = lambda: MIDNIGHT
        clock = self.stack.enter_context(patch("core.environment.minecraft.scene.datetime"))
        clock.now.return_value = MIDNIGHT
        self.decide.return_value = {"chosen_action": "Go to sleep for the night", "reasoning": "tired"}
        result = self.run_beat()
        self.assertTrue(result["fell_asleep"])
        self.assertEqual(self.bridge.calls, ["start", "end"])

    def test_without_a_provider_the_runner_is_the_palo_alto_runner(self):
        del self.context["world_provider"]
        self.world_chain.return_value = lambda person, world, recent_actions="": json.dumps(
            {"list_of_descriptions": [], "list_of_actions": ["Walk to Coupa Cafe"]})
        self.decide.return_value = dict(ACTION)
        result = self.run_beat()
        self.world_chain.assert_called_once()
        self.assertIsNone(result["world_outcome"])
        self.assertEqual(self.bridge.calls, [])
        self.assertNotIn("outcome", result["action_decision"])


class TestSavedWorldMemory(unittest.TestCase):
    def test_situation_world_round_trips_and_defaults_to_empty(self):
        situation = Situation.fresh(NOON)
        self.assertEqual(situation.world, {})
        situation.world = {"minecraft": {"home": HOME, "deaths": 2}}
        restored = Situation.from_dict(json.loads(json.dumps(situation.to_dict())), NOON)
        self.assertEqual(restored.world, {"minecraft": {"home": HOME, "deaths": 2}})
        self.assertEqual(Situation.from_dict({"world": "nonsense"}, NOON).world, {})

    def test_the_host_hands_the_runner_its_world_and_that_worlds_memory(self):
        from core.heartbeat.host import JenbinaHost
        seen = {}

        def iteration(**kwargs):
            seen.update(kwargs["context"])
            kwargs["context"]["world_memory"]["minecraft"] = {"home": HOME}
            raise RuntimeError("stop after looking")

        store = MagicMock()
        store.people.return_value = []
        world = object()
        host = JenbinaHost(store, MagicMock(), MagicMock(), MagicMock(), MagicMock(),
                           clock=lambda: NOON, iteration_fn=iteration, meta_cognitive_system=MagicMock(),
                           owner="test", world_provider=world)
        host.person = SimpleNamespace()
        with patch("core.heartbeat.host.choose_outreach_target", return_value=None):
            host._beat(NOON)
        self.assertIs(seen["world_provider"], world)
        self.assertEqual(host.situation.world, {"minecraft": {"home": HOME}})

    def test_a_host_without_a_world_passes_none(self):
        from core.heartbeat.host import JenbinaHost
        host = JenbinaHost(MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(),
                           meta_cognitive_system=MagicMock(), owner="test")
        self.assertIsNone(host.world_provider)


class TestTimelineAndRail(unittest.TestCase):
    def test_an_action_event_carries_an_outcome_only_when_there_is_one(self):
        args = ("Chop wood", "need wood", [], 50.0, 55.0, "Home", "afternoon", "clear sky", 15.0)
        self.assertNotIn("outcome", make_action(*args).detail)
        self.assertEqual(make_action(*args, outcome="Chopped 4 logs.").detail["outcome"], "Chopped 4 logs.")

    def test_action_details_lead_with_what_happened(self):
        self.assertEqual(action_details_text("need wood", []), "need wood")
        self.assertEqual(action_details_text("need wood", [], "Chopped 4 logs."),
                         "What happened: Chopped 4 logs.\nneed wood")
        self.assertEqual(action_details_text("", [], "Chopped 4 logs."), "What happened: Chopped 4 logs.")

    def test_the_rail_shows_her_body_when_the_world_reports_one(self):
        summary = {"location": {"name": "Home"}, "time": {"time_of_day": "afternoon"},
                   "weather": {"description": "clear sky", "temperature": 15.0}}
        self.assertNotIn("Health", env_line_html(summary))
        line = env_line_html({**summary, "body": {"health": 14, "food": 16}})
        self.assertIn("Health 14/20", line)
        self.assertIn("Food 16/20", line)
        self.assertNotIn("Health", env_line_html({**summary, "body": {"health": None}}))


if __name__ == "__main__":
    unittest.main()
