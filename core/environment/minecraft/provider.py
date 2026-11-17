"""The Minecraft world as the simulation runner sees it.

A beat calls ``observe`` once before it thinks and ``perform`` once after it
has decided. She is logged in only inside those two calls, so she never stands
idle in a running world while her mind works.
"""

from __future__ import annotations

import os
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping

from .bridge_client import DEFAULT_BRIDGE_URL, MinecraftBridge, WorldUnavailable
from .scene import SLEEP, Scene, WorldAction, build_scene, place_label, resolve_action, time_of_day

MEMORY_KEY = "minecraft"
DEATH_SECURITY_PENALTY = 30.0
UNCLEAR_CHOICE = "I could not work out how to do that here."


@dataclass
class Outcome:
    """What really happened when she acted."""
    ok: bool
    summary: str
    need_key: str | None = None
    action: WorldAction | None = None
    died: bool = False
    place: str | None = None
    # What the world looked like afterwards; ``None`` when nothing was done there.
    observation: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "summary": self.summary, "died": self.died, "place": self.place,
            "action": self.action.name if self.action is not None else None,
        }


def _set_need(person, name: str, value: float, now: datetime) -> None:
    need = person.maslow_needs.needs.get(name)
    if need is not None:
        need.satisfaction = max(0.0, min(100.0, float(value)))
        need.last_updated = now


class MinecraftWorld:
    name = "minecraft"
    # Hunger follows her body's food bar here, not the passing of real time.
    skip_needs = ("hunger",)

    def __init__(self, bridge: MinecraftBridge, stay_online: bool = False,
                 clock: Callable[[], datetime] = datetime.now):
        self.bridge = bridge
        self.stay_online = stay_online
        self.clock = clock

    def _leave(self) -> None:
        if not self.stay_online:
            self.bridge.end_session()

    def close(self) -> None:
        """Take her out of the world, even when she is set to stay online.

        Called when she falls asleep and when her host stops: she must never
        be left standing in a running world with nobody home. Never raises.
        """
        try:
            self.bridge.end_session()
        except Exception:
            pass

    def scene_after(self, observation: dict, memory: dict) -> Scene:
        """The scene as it is after an action, for the summary the rail shows."""
        return build_scene(observation, self._memory(memory).get("home"), self.clock())

    @staticmethod
    def _memory(memory: dict) -> dict:
        own = memory.get(MEMORY_KEY)
        if not isinstance(own, dict):
            own = memory[MEMORY_KEY] = {}
        return own

    def sync_body(self, person, observation: dict | None, now: datetime | None = None) -> None:
        """Set her hunger need from the body's food bar in ``observation``."""
        if not isinstance(observation, dict):
            return
        now = now if now is not None else self.clock()
        try:
            food = float(observation.get("food"))
        except (TypeError, ValueError):
            return
        _set_need(person, "hunger", food / 20 * 100, now)

    def _can_sleep(self, person, sleep_config, now: datetime) -> bool:
        """True exactly when choosing sleep would make her fall asleep."""
        if sleep_config is None or not sleep_config.sleep_enabled:
            return False
        return (time_of_day(now) == "night"
                or person.maslow_needs.get_need_satisfaction("sleep") < sleep_config.low_sleep_need)

    def observe(self, person, memory: dict, sleep_config=None, waiting=nullcontext) -> Scene:
        """Log in, look, log out. Raises ``WorldUnavailable`` if she cannot.

        ``waiting`` is entered only around the calls to the bridge, so the
        host can let a chat message be answered while this thread waits for
        the world. Her state is touched only after it has been left.
        """
        with waiting():
            try:
                observation = self.bridge.start_session()
            finally:
                self._leave()
        now = self.clock()
        own = self._memory(memory)
        position = observation.get("position") or {}
        if "home" not in own and all(k in position for k in ("x", "y", "z")):
            own["home"] = [position["x"], position["y"], position["z"]]
        self.sync_body(person, observation, now)
        return build_scene(observation, own.get("home"), now, self._can_sleep(person, sleep_config, now))

    def perform(self, scene: Scene, chosen_text: str, person, memory: dict, waiting=nullcontext) -> Outcome:
        """Do what she chose and report what really happened. Never raises.

        ``waiting`` is entered only around the calls to the bridge; see ``observe``.
        """
        action = resolve_action(scene.actions, chosen_text)
        if action is None:
            outcome = Outcome(False, UNCLEAR_CHOICE, place=scene.place)
        elif action.name == SLEEP:
            # Sleeping is the heartbeat's business: she leaves the world, even
            # when she is set to stay online between beats.
            self.close()
            return Outcome(True, "", SLEEP, action, place=scene.place)
        else:
            outcome = self._act(scene, action, person, memory, waiting)
        if outcome.summary:
            label = action.label if action is not None else chosen_text
            person.working_memory.add_note(
                f"In the world just now I tried to: {label}. {outcome.summary}", cycles=2)
        return outcome

    def _act(self, scene: Scene, action: WorldAction, person, memory: dict, waiting=nullcontext) -> Outcome:
        try:
            # An action can take most of a minute: nothing of hers is touched
            # while this thread only waits for the bridge.
            with waiting():
                try:
                    self.bridge.start_session()
                    result = self.bridge.act(action.name, action.args)
                finally:
                    self._leave()
        except WorldUnavailable as err:
            return Outcome(False, f"I could not reach the world to do it ({err}).", action=action, place=scene.place)

        now = self.clock()
        own = self._memory(memory)
        observation = result.get("observation")
        if not isinstance(observation, dict):
            observation = scene.observation
        ok = bool(result.get("ok"))
        died = bool(result.get("died"))
        summary = str(result.get("summary") or ("Done." if ok else "It did not work."))
        self.sync_body(person, observation, now)
        if died:
            own["deaths"] = int(own.get("deaths", 0)) + 1
            security = person.maslow_needs.needs.get("security")
            if security is not None:
                _set_need(person, "security", security.satisfaction - DEATH_SECURITY_PENALTY, now)
            person.working_memory.add_note(
                "I died in the world and woke at the spawn point. What I carried may be gone.", cycles=3)
        return Outcome(
            ok=ok and not died, summary=summary, need_key=action.need_key if ok and not died else None,
            action=action, died=died, place=place_label(observation, own.get("home")),
            observation=observation,
        )


def world_from_env(env: Mapping[str, str] | None = None) -> MinecraftWorld | None:
    """The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world."""
    env = os.environ if env is None else env
    if str(env.get("JENBINA_WORLD", "")).strip().lower() != "minecraft":
        return None
    bridge = MinecraftBridge(env.get("JENBINA_MINECRAFT_BRIDGE_URL") or DEFAULT_BRIDGE_URL)
    return MinecraftWorld(bridge, stay_online=env.get("JENBINA_MINECRAFT_STAY_ONLINE") == "1")
