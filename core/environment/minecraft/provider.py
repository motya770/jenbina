"""The Minecraft world as the simulation runner sees it.

A beat calls ``observe`` once before it thinks and ``perform`` once after it
has decided. She is logged in only inside those two calls, so she never stands
idle in a running world while her mind works.

Others may live in the world too. She sees them in her scene, is shown what
they said, and can choose to talk with one: a short exchange inside
``perform``, her lines written by the ``voice`` the beat passes in.

Her host calls ``start`` when it begins hosting her and ``stop`` when it ends:
with a launcher, that starts and stops the world's own processes.
"""

from __future__ import annotations

import os
import time
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Mapping

from urllib.parse import urlsplit

from .bridge_client import DEFAULT_BRIDGE_URL, MinecraftBridge, WorldUnavailable
from .conversation import ME, inhabitant_key
from .launcher import WorldLauncher, is_local, repo_root
from .scene import (
    SLEEP, TALK, Scene, WorldAction, build_scene, place_label, plain_name, resolve_action, safe_speech,
    time_of_day,
)

MEMORY_KEY = "minecraft"
DEATH_SECURITY_PENALTY = 30.0
UNCLEAR_CHOICE = "I could not work out how to do that here."

# A talk: how many lines she says at most, and how long it may take in all.
MAX_EXCHANGES = 3
TALK_SECONDS = 90.0
ANSWER_WAIT_MS = 30000
APPROACH_BUDGET_MS = 25000
TALKS_PER_DAY = 12
# What she overheard is shown on her next look, unless it has grown old.
HEARD_KEEP = timedelta(hours=1)
HEARD_LIMIT = 20
HEARD_LENGTH = 256
# How many of the last lines exchanged with each inhabitant she keeps.
LAST_LINES = 6
REPLY_LINES = 3
TALK_SUMMARY_LIMIT = 600
NO_WORDS = "I could not find the words to say to {name}."
NO_ANSWER = "I spoke to {name} but got no answer."
NOT_FOUND = "I looked for {name} but could not find them in the world."
LOST_TOUCH = " Then I lost touch with the world."
MORE_SAID = " (and more was said.)"


@dataclass
class Outcome:
    """What really happened when she acted."""
    ok: bool
    summary: str
    need_key: str | None = None
    action: WorldAction | None = None
    died: bool = False
    place: str | None = None
    # What the world looked like afterwards; ``None`` when nothing was done
    # there, or when she could not see how it ended.
    observation: dict | None = None
    # She acted, or may have, and did not see the result: what she knows of
    # the world is from before the action.
    unseen: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "summary": self.summary, "died": self.died, "place": self.place,
            "unseen": self.unseen,
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
                 clock: Callable[[], datetime] = datetime.now,
                 launcher: WorldLauncher | None = None,
                 talks_per_day: int = TALKS_PER_DAY,
                 timer: Callable[[], float] = time.monotonic):
        self.bridge = bridge
        self.stay_online = stay_online
        self.clock = clock
        # How many talks she may begin in one day; 0 means she never talks.
        self.talks_per_day = talks_per_day
        # Seconds that only ever go forward, for the length of a talk.
        self.timer = timer
        # Starts and stops the server and the bridge; ``None`` when the owner
        # runs them.
        self.launcher = launcher

    def start(self) -> None:
        """Start the world's processes if they are ours to start.

        Returns once they are launched; ``observe`` waits until they are
        ready. Raises ``WorldUnavailable`` when the world is not set up.
        """
        if self.launcher is not None:
            self.launcher.start()

    def stop(self) -> None:
        """Stop the processes ``start`` launched. Never raises.

        It does not log her out: ``close`` does, and only the host that has
        her may call it.
        """
        if self.launcher is not None:
            try:
                self.launcher.stop()
            except Exception:
                pass

    def _leave(self) -> None:
        if not self.stay_online:
            self.bridge.end_session()

    def close(self) -> None:
        """Take her out of the world, even when she is set to stay online.

        Called by her host when she falls asleep and when it stops: she must
        never be left standing in a running world with nobody home. Never raises.
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

    @staticmethod
    def _talks_today(own: dict, now: datetime) -> int:
        talks = own.get("talks")
        if not isinstance(talks, dict) or talks.get("day") != now.date().isoformat():
            return 0
        try:
            return int(talks.get("count", 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _stash_heard(own: dict, observation: dict | None, now: datetime) -> None:
        """Keep what an observation says was heard, for her next look."""
        if not isinstance(observation, dict):
            return
        carried = own.get("heard") if isinstance(own.get("heard"), list) else []
        for entry in observation.get("heard") or []:
            if not isinstance(entry, dict):
                continue
            speaker, text = entry.get("from"), entry.get("text")
            if isinstance(speaker, str) and isinstance(text, str):
                carried.append({"from": speaker, "text": text[:HEARD_LENGTH],
                                "whisper": bool(entry.get("whisper")), "at": now.isoformat()})
        own["heard"] = carried[-HEARD_LIMIT:]

    @staticmethod
    def _take_heard(own: dict, now: datetime) -> list[dict]:
        """The carried lines that are still fresh; the carried list is emptied."""
        carried = own.get("heard") if isinstance(own.get("heard"), list) else []
        own["heard"] = []
        fresh = []
        for entry in carried:
            try:
                age = now - datetime.fromisoformat(entry["at"])
            except (TypeError, KeyError, ValueError):
                continue
            if age <= HEARD_KEEP:
                fresh.append(entry)
        return fresh

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
            if self.launcher is not None:
                # A world that is still starting, or that went down, is waited
                # for here, with her mind free to talk meanwhile.
                self.launcher.ensure_ready()
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
        # What she overheard since her last look, then what she hears now.
        heard = self._take_heard(own, now) + [e for e in observation.get("heard") or [] if isinstance(e, dict)]
        return build_scene(
            observation, own.get("home"), now, self._can_sleep(person, sleep_config, now),
            heard=heard, can_talk=self._talks_today(own, now) < self.talks_per_day)

    def perform(self, scene: Scene, chosen_text: str, person, memory: dict, waiting=nullcontext,
                voice=None, keep_going=None) -> Outcome:
        """Do what she chose and report what really happened. Never raises.

        ``waiting`` is entered only around the calls to the bridge; see ``observe``.
        ``voice`` writes her lines when she chooses to talk (see
        ``conversation.Voice``); without one she has no words. ``keep_going``
        returns false once her host no longer has her: a talk then stops.
        """
        action = resolve_action(scene.actions, chosen_text)
        if action is None:
            outcome = Outcome(False, UNCLEAR_CHOICE, place=scene.place)
        elif action.name == SLEEP:
            # Sleeping is the heartbeat's business. When she does fall asleep
            # her host takes her out of the world, without holding her mind.
            return Outcome(True, "", SLEEP, action, place=scene.place)
        elif action.name == TALK:
            outcome = self._talk(scene, action, person, memory, waiting, voice, keep_going)
        else:
            outcome = self._act(scene, action, person, memory, waiting)
        if outcome.summary:
            label = action.label if action is not None else chosen_text
            person.working_memory.add_note(
                f"In the world just now I tried to: {label}. {outcome.summary}", cycles=2)
        return outcome

    def _act(self, scene: Scene, action: WorldAction, person, memory: dict, waiting=nullcontext) -> Outcome:
        arrived = None
        try:
            # An action can take most of a minute: nothing of hers is touched
            # while this thread only waits for the bridge.
            with waiting():
                try:
                    arrived = self.bridge.start_session()
                    result = self.bridge.act(action.name, action.args)
                finally:
                    self._leave()
        except WorldUnavailable as err:
            # What she heard on arriving has left the bridge; it is kept here.
            self._stash_heard(self._memory(memory), arrived, self.clock())
            # The action may have begun before the world was lost.
            return Outcome(False, f"I could not reach the world to do it ({err}).",
                           action=action, place=scene.place, unseen=True)

        now = self.clock()
        own = self._memory(memory)
        observation = result.get("observation")
        # Anything said while she was thinking or acting waits for her next look.
        self._stash_heard(own, arrived, now)
        self._stash_heard(own, observation if isinstance(observation, dict) else None, now)
        if not isinstance(observation, dict):
            # She was cut off (an action that ran out of time): where she is
            # and how her body is now is not known. Nothing is made up from
            # what she saw before; the next beat looks again.
            observation = None
        ok = bool(result.get("ok")) and observation is not None
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
            action=action, died=died,
            place=place_label(observation, own.get("home")) if observation is not None else scene.place,
            observation=observation, unseen=observation is None,
        )


    # -- talking ------------------------------------------------------------

    def _talk(self, scene: Scene, action: WorldAction, person, memory: dict, waiting,
              voice, keep_going) -> Outcome:
        """A short exchange with another inhabitant, inside this one beat.

        Every call to the bridge is made with her mind released; her voice is
        asked with it held (the LLM wait releases it by itself). She is logged
        out at the end whatever happened.
        """
        name = plain_name(action.args.get("player"))
        if voice is None or name is None:
            return Outcome(False, NO_WORDS.format(name=name or "them"), action=action, place=scene.place)
        own = self._memory(memory)
        people = own.get("people") if isinstance(own.get("people"), dict) else {}
        known = people.get(name) if isinstance(people.get(name), dict) else {}
        last_lines = [line for line in known.get("lines") or [] if isinstance(line, str)]

        transcript: list[tuple[str, str]] = []
        looks: list[dict] = []      # every observation the bridge gave during the talk
        observation = None
        said = 0
        offline = abandoned = False
        lost: WorldUnavailable | None = None
        started = self.timer()

        def hosting() -> bool:
            return keep_going is None or bool(keep_going())

        try:
            with waiting():
                looks.append(self.bridge.start_session())
                if action.args.get("near"):
                    # Walking up is a courtesy: the talk goes on if she cannot.
                    walked = self.bridge.act("approach_player", {"name": name}, APPROACH_BUDGET_MS)
                    if isinstance(walked.get("observation"), dict):
                        looks.append(walked["observation"])
                    if walked.get("left_world"):
                        # A walk that overran ended with her logged out.
                        looks.append(self.bridge.start_session())
            while said < MAX_EXCHANGES and self.timer() - started < TALK_SECONDS:
                if not hosting():
                    # Her host no longer has her: she is not this process's to speak for.
                    abandoned = True
                    break
                line, end = voice(name, scene.descriptions, last_lines, transcript)
                if not hosting():
                    # Her mind was free while the words were found, and her host
                    # changed hands meanwhile: they are not said.
                    abandoned = True
                    break
                left = TALK_SECONDS - (self.timer() - started)
                if not line or left <= 0:
                    break
                wait_ms = int(min(ANSWER_WAIT_MS, left * 1000))
                try:
                    with waiting():
                        reply = self.bridge.say(name, line, wait_ms)
                except WorldUnavailable:
                    said += 1       # the line may have been said before the world was lost
                    raise
                if not reply.get("ok"):
                    offline = True
                    break
                said += 1
                # Kept the way everything said is kept: quotable inside double quotes.
                transcript.append((ME, line.replace('"', "'")))
                pieces = [entry for entry in reply.get("heard") or []
                          if isinstance(entry, dict) and entry.get("from") == name
                          and safe_speech(entry.get("text"))]
                theirs = [safe_speech(entry["text"]) for entry in pieces[:REPLY_LINES]]
                # More pieces than a reply holds are not lost: she overheard them.
                looks.append({"heard": pieces[REPLY_LINES:]})
                transcript.extend((name, text) for text in theirs)
                if not theirs or end:
                    break
            if not abandoned and not hosting():
                abandoned = True
            if not abandoned:
                with waiting():
                    observation = self.bridge.observe()
                looks.append(observation)
        except WorldUnavailable as err:
            lost = err
            observation = None
        finally:
            with waiting():
                self._leave()

        now = self.clock()
        for look in looks:
            self._stash_heard(own, look, now)
        self.sync_body(person, observation, now)
        answers = [text for speaker, text in transcript if speaker != ME]
        if said > 0:
            own["talks"] = {"day": now.date().isoformat(), "count": self._talks_today(own, now) + 1}
        if transcript:
            lines = [f"{'me' if speaker == ME else name}: {text}" for speaker, text in transcript]
            if not isinstance(own.get("people"), dict):
                own["people"] = {}
            own["people"][name] = {
                "met": known.get("met") or now.isoformat(),
                "talks": int(known.get("talks") or 0) + 1,
                "last": now.isoformat(),
                "lines": (last_lines + lines)[-LAST_LINES:],
            }
        self._remember_talk(person, name, answers)

        place = place_label(observation, own.get("home")) if observation is not None else scene.place
        unseen = observation is None
        if answers:
            # Whole lines while they fit; never cut in the middle of what someone said.
            summary = f"I talked with {name}."
            for speaker, text in transcript:
                piece = f' I said: "{text}"' if speaker == ME else f' {name} said: "{text}"'
                if len(summary) + len(piece) + len(MORE_SAID) > TALK_SUMMARY_LIMIT:
                    summary += MORE_SAID
                    break
                summary += piece
            if lost is not None:
                summary += LOST_TOUCH
            return Outcome(True, summary, action.need_key, action, place=place,
                           observation=observation, unseen=unseen)
        if lost is not None:
            # A line may have been said before the world was lost.
            summary = f"I could not reach the world to do it ({lost})."
        elif said > 0:
            summary = NO_ANSWER.format(name=name)
        elif offline:
            summary = NOT_FOUND.format(name=name)
        else:
            summary = NO_WORDS.format(name=name)
        return Outcome(False, summary, action=action, place=place, observation=observation, unseen=unseen)

    @staticmethod
    def _remember_talk(person, name: str, answers: list[str]) -> None:
        """What they said shapes what she knows of them; the talk counts once
        as social contact. An inhabitant is kept apart from the people she
        talks with in the app by its own key."""
        if not answers:
            return
        key = inhabitant_key(name)
        social = getattr(person, "social_cognition", None)
        if social is not None:
            model = social.get_or_create_model(key)
            beliefs = list(model.beliefs)
            for text in answers:
                social.observe_entity_message(key, text)
            # A belief is free text lifted from what was said, and is shown
            # unquoted wherever a person model is printed. What someone says
            # in the game is kept only as quoted speech, so none is kept here.
            model.beliefs[:] = beliefs
        tracker = getattr(person, "social_interaction_tracker", None)
        if tracker is not None:
            from ...social.social_interaction_tracker import infer_emotional_tone
            tracker.record_chat(key, infer_emotional_tone(" ".join(answers)))


def _talks_per_day(env: Mapping[str, str]) -> int:
    """``JENBINA_MINECRAFT_TALKS_PER_DAY``: a whole number of 0 or more, else the default."""
    try:
        wanted = int(str(env.get("JENBINA_MINECRAFT_TALKS_PER_DAY", "")).strip())
    except ValueError:
        return TALKS_PER_DAY
    return wanted if wanted >= 0 else TALKS_PER_DAY


def world_from_env(env: Mapping[str, str] | None = None) -> MinecraftWorld | None:
    """The world chosen by ``JENBINA_WORLD``; ``None`` keeps the Palo Alto world."""
    env = os.environ if env is None else env
    if str(env.get("JENBINA_WORLD", "")).strip().lower() != "minecraft":
        return None
    bridge = MinecraftBridge(env.get("JENBINA_MINECRAFT_BRIDGE_URL") or DEFAULT_BRIDGE_URL)
    launcher = None
    # Her world starts and stops with her, unless that is switched off or the
    # bridge is on another machine.
    if env.get("JENBINA_MINECRAFT_AUTOSTART", "1") != "0" and is_local(urlsplit(bridge.base_url).hostname):
        launcher = WorldLauncher(repo_root(), bridge, env=env)
    return MinecraftWorld(bridge, stay_online=env.get("JENBINA_MINECRAFT_STAY_ONLINE") == "1",
                          launcher=launcher, talks_per_day=_talks_per_day(env))
