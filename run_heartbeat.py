#!/usr/bin/env python3
"""Host Jenbina's continuous life independently of the UI.

Usage:
    python run_heartbeat.py
    python run_heartbeat.py --once
    python run_heartbeat.py --adopt-user-id 3
    python run_heartbeat.py --list-users
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
from typing import Callable

# Add project root to path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env and configure tracing before any LangChain imports.
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "jenbina"

from core.auth.user_db import UserDatabase
from core.connect import get_llm, get_json_llm
from core.heartbeat.host import JenbinaHost
from core.heartbeat.store import BeingStore


def build_host(adopt_user_id: int | None = None) -> JenbinaHost:
    """Build the shared storage and LLMs only when a host is requested."""
    user_db = UserDatabase()
    store = BeingStore(user_db.db_path)
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "openai-advanced")
    llm = get_llm(provider=chat_model, temperature=1, max_tokens=600)
    llm_json_mode = get_json_llm(provider="openai", temperature=1)
    insight_llm = get_llm(provider="openai-advanced", temperature=0.8, max_tokens=500)
    return JenbinaHost(
        store=store, user_db=user_db, llm=llm, llm_json_mode=llm_json_mode,
        insight_llm=insight_llm, adopt_user_id=adopt_user_id,
    )


def main(
    argv: list[str] | None = None,
    host_factory: Callable[..., JenbinaHost] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="Jenbina standalone heartbeat")
    parser.add_argument("--adopt-user-id", type=int,
                        help="Adopt this user's saved Jenbina on the first start")
    parser.add_argument("--list-users", action="store_true", help="List all users and exit")
    parser.add_argument("--once", action="store_true", help="Take one beat and exit")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    if args.list_users:
        users = UserDatabase().get_all_users()
        if not users:
            print("No users found in database.")
        else:
            print(f"{'ID':<6} {'Display Name':<30} {'Email':<40}")
            print("-" * 76)
            for user in users:
                print(f"{user['id']:<6} {user.get('display_name') or '':<30} "
                      f"{user.get('email') or '':<40}")
        return 0

    factory = build_host if host_factory is None else host_factory
    host = factory(adopt_user_id=args.adopt_user_id)
    if not host.start(threads=False):
        print(f"Jenbina is already living in another process ({host.status().holder}).",
              file=sys.stderr)
        return 1

    previous_handlers = {}

    def shutdown(signum, frame):
        # Stop after the moment she is living now. Hand the signal back to its
        # previous handler so a second Ctrl-C quits at once instead of waiting.
        host.stop()
        signal.signal(signum, previous_handlers.get(signum, signal.SIG_DFL))

    try:
        if args.once:
            host.step_once()
        else:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[signum] = signal.signal(signum, shutdown)
            host.run_forever()
    finally:
        try:
            host.stop()
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)
    return 0


if __name__ == "__main__":
    sys.exit(main())
