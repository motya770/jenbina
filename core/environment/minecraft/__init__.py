"""Jenbina's Minecraft world: a real, persistent place she perceives and acts in.

Turned on with ``JENBINA_WORLD=minecraft``. See ``minecraft/README.md`` and
``docs/plans/2026-11-17-minecraft-world-design.md``.
"""

from .bridge_client import DEFAULT_BRIDGE_URL, MinecraftBridge, WorldUnavailable
from .provider import MinecraftWorld, Outcome, world_from_env
from .scene import Scene, WorldAction, build_scene, resolve_action

__all__ = [
    "DEFAULT_BRIDGE_URL",
    "MinecraftBridge",
    "MinecraftWorld",
    "Outcome",
    "Scene",
    "WorldAction",
    "WorldUnavailable",
    "build_scene",
    "resolve_action",
    "world_from_env",
]
