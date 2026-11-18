"""Turn a Minecraft observation into what her mind reads: a place, a scene
in sentences, and the actions the world offers right now.

Everything here is plain code over the bridge's observation. No LLM is asked
to imagine the world.
"""

from __future__ import annotations

import difflib
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..environment_simulator import TimeData, WeatherData
from ..location_system import Location
from ..world_state import WorldState

HOME_PLACE = "Home"
HOME_RADIUS = 12
FAR_FROM_HOME = 24
MAX_CRAFT_ACTIONS = 4
RESOLVE_CUTOFF = 0.6
SLEEP = "sleep"
TALK = "talk"
MAX_TALK_ACTIONS = 3
MAX_PLAYERS = 5
MAX_SPEECH = 200
# Shown in place of a line that reads like an attempt to give her orders.
UNREADABLE = "(something she could not make sense of)"
PLAIN_NAME = re.compile(r"[A-Za-z0-9_]{3,16}")

# Best first; the same order the bridge uses when she eats.
FOODS = (
    "cooked_beef", "cooked_porkchop", "cooked_mutton", "cooked_chicken", "cooked_rabbit",
    "bread", "baked_potato", "apple", "carrot", "beef", "porkchop", "mutton", "rabbit",
    "sweet_berries", "melon_slice", "potato", "chicken", "rotten_flesh",
)
# Which craftable things are offered first when there are more than fit.
CRAFT_PRIORITY = (
    "stone_pickaxe", "wooden_pickaxe", "planks", "crafting_table", "stick",
    "stone_axe", "stone_sword", "furnace", "wooden_axe", "wooden_sword",
)
CRAFT_LABELS = {
    "planks": "Turn your logs into planks",
    "stick": "Craft sticks",
    "crafting_table": "Craft a crafting table",
    "furnace": "Craft a furnace",
}
DIRECTIONS = ("north", "east", "south", "west")


@dataclass(frozen=True)
class WorldAction:
    """One thing the world offers: the sentence she reads, the bridge routine
    behind it, and the need-satisfaction key it earns when it succeeds."""
    label: str
    name: str
    need_key: str
    args: dict = field(default_factory=dict)


@dataclass
class Scene:
    observation: dict
    place: str
    descriptions: list[str]
    actions: list[WorldAction]
    world_state: WorldState

    @property
    def labels(self) -> list[str]:
        return [action.label for action in self.actions]

    @property
    def body(self) -> dict[str, int]:
        return {"health": _whole(self.observation.get("health"), 20),
                "food": _whole(self.observation.get("food"), 20)}

    def description_data(self) -> dict[str, list[str]]:
        """The shape the action decision chain expects from a world description."""
        return {"list_of_descriptions": list(self.descriptions), "list_of_actions": self.labels}


def _whole(value: Any, default: int) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def _position(observation: dict) -> tuple[float, float, float] | None:
    position = observation.get("position")
    try:
        return float(position["x"]), float(position["y"]), float(position["z"])
    except (TypeError, KeyError, ValueError):
        return None


def distance_from_home(observation: dict, home) -> float | None:
    """Horizontal blocks between her and home, or ``None`` when either is unknown."""
    here = _position(observation)
    if here is None or not _is_position(home):
        return None
    return math.hypot(here[0] - home[0], here[2] - home[2])


def _is_position(value) -> bool:
    return (isinstance(value, (list, tuple)) and len(value) == 3
            and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in value))


def _words(name: str) -> str:
    return str(name).replace("_", " ")


def _article(phrase: str) -> str:
    return ("an " if phrase[:1].lower() in "aeiou" else "a ") + phrase


def place_label(observation: dict, home) -> str:
    """``Home`` near her home position, otherwise the biome in plain words."""
    away = distance_from_home(observation, home)
    if away is not None and away <= HOME_RADIUS:
        return HOME_PLACE
    biome = str(observation.get("biome") or "unknown")
    return "The wild" if biome == "unknown" else _words(biome).capitalize()


def celsius(observation: dict) -> float:
    """A nominal temperature from the biome's Minecraft temperature (0.8 is plains)."""
    try:
        return float(max(-15, min(40, round(float(observation.get("temperature")) * 25))))
    except (TypeError, ValueError):
        return 18.0


def time_of_day(now: datetime) -> str:
    """Her own clock, split the way the Palo Alto world splits it."""
    if 6 <= now.hour < 12:
        return "morning"
    if 12 <= now.hour < 17:
        return "afternoon"
    if 17 <= now.hour < 21:
        return "evening"
    return "night"


def _season(now: datetime) -> str:
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(now.month, "autumn")


def best_food(inventory: dict) -> str | None:
    return next((food for food in FOODS if _whole(inventory.get(food), 0) > 0), None)


def plain_name(name) -> str | None:
    """The name if it is a plain Minecraft name, else ``None``.

    Only a plain name is ever shown to her or put in a prompt, so a name can
    never carry other text.
    """
    return name if isinstance(name, str) and PLAIN_NAME.fullmatch(name) else None


def safe_speech(text) -> str:
    """What someone said, made safe to quote: one short line without double
    quotes. A line that reads like instructions is not repeated at all."""
    if not isinstance(text, str):
        return ""
    line = " ".join(text.split()).replace('"', "'")
    if not line:
        return ""
    from ...interaction.guardrails import check_injection  # imported late: it loads the chat stack
    if any(check_injection(line)):
        return UNREADABLE
    return line[:MAX_SPEECH].rstrip()


def speech_line(entry) -> str | None:
    """One heard line as quoted speech, or ``None`` when it cannot be shown."""
    if not isinstance(entry, dict):
        return None
    name = plain_name(entry.get("from"))
    text = safe_speech(entry.get("text"))
    if not name or not text:
        return None
    return f'{name} said to you: "{text}"' if entry.get("whisper") else f'{name} said: "{text}"'


def players(observation: dict) -> tuple[list[tuple[str, int]], list[str]]:
    """Other players by plain name: those in sight with their distance, and
    those somewhere else. Nobody is listed twice."""
    seen: set[str] = set()
    near: list[tuple[str, int]] = []
    for entry in (observation.get("nearby") or {}).get("players") or []:
        name = plain_name(entry.get("name")) if isinstance(entry, dict) else None
        if name and name not in seen:
            seen.add(name)
            near.append((name, _whole(entry.get("distance"), 0)))
    elsewhere: list[str] = []
    for entry in observation.get("elsewhere") or []:
        name = plain_name(entry)
        if name and name not in seen:
            seen.add(name)
            elsewhere.append(name)
    return near[:MAX_PLAYERS], elsewhere[:MAX_PLAYERS]


def describe(observation: dict, place: str, home, heard=()) -> list[str]:
    inventory = observation.get("inventory") or {}
    nearby = observation.get("nearby") or {}
    sky = observation.get("sky") or {}
    away = distance_from_home(observation, home)

    where = f"You are at {place}." if place == HOME_PLACE else f"You are in {place.lower()}."
    if place != HOME_PLACE and away is not None:
        where += f" Home is {away:.0f} blocks away."
    lines = [where]
    lines.append("The sun is up here." if sky.get("is_day", True) else "It is dark here.")
    if sky.get("raining"):
        lines.append("It is raining.")
    lines.append(f"Your body: health {_whole(observation.get('health'), 20)}/20, "
                 f"food {_whole(observation.get('food'), 20)}/20.")
    carried = [f"{_whole(count, 0)} {_words(name)}" for name, count in sorted(inventory.items())]
    lines.append("You carry: " + ", ".join(carried) + "." if carried else "You carry nothing.")
    if observation.get("sheltered"):
        lines.append("You are inside your burrow.")
    if _whole(nearby.get("logs"), 0) > 0:
        lines.append("Trees stand close by.")
    if nearby.get("stone"):
        lines.append("There is stone close by.")
    if nearby.get("water"):
        lines.append("There is water close by.")
    if nearby.get("crafting_table"):
        lines.append("A crafting table is within reach.")
    for animal in nearby.get("animals") or []:
        lines.append(f"{_article(_words(animal.get('name', 'animal'))).capitalize()} is "
                     f"{_whole(animal.get('distance'), 0)} blocks away.")
    for hostile in nearby.get("hostiles") or []:
        lines.append(f"Danger: {_article(_words(hostile.get('name', 'monster')))} is "
                     f"{_whole(hostile.get('distance'), 0)} blocks away.")
    near, elsewhere = players(observation)
    for name, distance in near:
        lines.append(f"{name} is {distance} blocks away.")
    for name in elsewhere:
        lines.append(f"{name} is somewhere else in this world.")
    # What was said is data: it is quoted here and never selects an action.
    lines.extend(line for line in map(speech_line, heard or ()) if line)
    return lines


def _craft_label(item: str) -> str:
    return CRAFT_LABELS.get(item) or f"Craft {_article(_words(item))}"


def talk_actions(observation: dict) -> list[WorldAction]:
    """A talk with each player in sight, then a message to each one elsewhere."""
    near, elsewhere = players(observation)
    actions = [WorldAction(f"Talk with {name}", TALK, "socialize", {"player": name, "near": True})
               for name, _ in near]
    actions += [WorldAction(f"Send a message to {name}, who is elsewhere in the world", TALK, "socialize",
                            {"player": name, "near": False}) for name in elsewhere]
    return actions[:MAX_TALK_ACTIONS]


def available_actions(observation: dict, home, can_sleep: bool, can_talk: bool = True) -> list[WorldAction]:
    """What she can do right now, most pressing first. Each label is unique."""
    inventory = observation.get("inventory") or {}
    nearby = observation.get("nearby") or {}
    actions: list[WorldAction] = []

    if nearby.get("hostiles") and not observation.get("sheltered"):
        actions.append(WorldAction("Dig a burrow and shelter in it", "take_shelter", "find_shelter"))
    food = best_food(inventory)
    if food and _whole(observation.get("food"), 20) < 20:
        actions.append(WorldAction(f"Eat the {_words(food)} you are carrying", "eat", "eat"))
    if can_talk:
        actions.extend(talk_actions(observation))
    animals = nearby.get("animals") or []
    if animals:
        animal = _words(animals[0].get("name", "animal"))
        actions.append(WorldAction(f"Hunt the {animal} nearby for food", "hunt", "work_on_goals"))
    if nearby.get("water"):
        actions.append(WorldAction("Drink from the water nearby", "drink", "drink"))
    if _whole(nearby.get("logs"), 0) > 0:
        actions.append(WorldAction("Chop wood from the trees nearby", "gather_wood", "work_on_goals"))

    craftable = [item for item in CRAFT_PRIORITY if item in (observation.get("craftable") or [])]
    for item in craftable[:MAX_CRAFT_ACTIONS]:
        actions.append(WorldAction(_craft_label(item), "craft", "develop_skills", {"item": item}))

    has_pickaxe = any(name.endswith("_pickaxe") and _whole(count, 0) > 0 for name, count in inventory.items())
    if has_pickaxe and nearby.get("stone"):
        actions.append(WorldAction("Mine stone with your pickaxe", "mine_stone", "work_on_goals"))

    away = distance_from_home(observation, home)
    if away is not None and away > FAR_FROM_HOME:
        x, y, z = home
        actions.append(WorldAction("Walk back home", "go_home", "find_shelter", {"x": x, "y": y, "z": z}))

    for direction in DIRECTIONS:
        actions.append(WorldAction(f"Explore to the {direction}", "explore", "learn_new_things",
                                   {"direction": direction}))
    actions.append(WorldAction("Look around and take in the surroundings", "look_around", "explore_meaning"))
    actions.append(WorldAction("Rest for a while", "rest", "rest"))
    if can_sleep:
        actions.append(WorldAction("Go to sleep for the night", SLEEP, SLEEP))
    return actions


def build_world_state(observation: dict, place: str, descriptions: list[str], now: datetime) -> WorldState:
    """A ``WorldState`` made of the existing dataclasses, so the summary, the
    rail and the timeline read the Minecraft world like any other."""
    here = _position(observation) or (0.0, 0.0, 0.0)
    sky = observation.get("sky") or {}
    location = Location(
        name=place,
        type="home" if place == HOME_PLACE else "wilderness",
        address=f"x {here[0]:.0f}, y {here[1]:.0f}, z {here[2]:.0f}",
        description=" ".join(descriptions),
        coordinates=(here[0], here[2]),
        opening_hours={},
        features=[],
        popularity=0.0,
        price_range="",
        mood="quiet",
    )
    # The time is her own clock: the heartbeat decides when she sleeps. The
    # Minecraft sky is part of the scene, not of the time of day.
    time_data = TimeData(
        current_time=now,
        day_of_week=now.strftime("%A"),
        is_daytime=bool(sky.get("is_day", True)),
        time_of_day=time_of_day(now),
        season=_season(now),
        moon_phase="",
    )
    if sky.get("raining"):
        sky_words = "rain"
    else:
        sky_words = "clear sky" if sky.get("is_day", True) else "dark sky"
    weather = WeatherData(
        temperature=celsius(observation), humidity=50.0, description=sky_words, wind_speed=0.0,
        pressure=1013.0, visibility=10.0, sunrise="", sunset="", timestamp=now,
    )
    return WorldState(
        weather_data=weather, time_data=time_data, current_location_info=location,
        environment_description=" ".join(descriptions),
    )


def build_scene(observation: dict, home, now: datetime, can_sleep: bool = False,
                heard=(), can_talk: bool = True) -> Scene:
    """``heard`` is what other players said since she last looked; ``can_talk``
    is false once she has had her talks for the day."""
    place = place_label(observation, home)
    descriptions = describe(observation, place, home, heard)
    return Scene(
        observation=observation,
        place=place,
        descriptions=descriptions,
        actions=available_actions(observation, home, can_sleep, can_talk),
        world_state=build_world_state(observation, place, descriptions, now),
    )


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def resolve_action(actions: list[WorldAction], chosen_text: str) -> WorldAction | None:
    """The offered action her free-text choice means, or ``None``.

    Exact match first (ignoring case and punctuation), then one label
    contained in the other, then the closest label if it is close enough.
    """
    chosen = _normalise(chosen_text)
    if not chosen:
        return None
    by_label = {_normalise(action.label): action for action in actions}
    if chosen in by_label:
        return by_label[chosen]
    contained = [label for label in by_label if label in chosen or chosen in label]
    if contained:
        return by_label[max(contained, key=len)]
    close = difflib.get_close_matches(chosen, list(by_label), n=1, cutoff=RESOLVE_CUTOFF)
    return by_label[close[0]] if close else None
