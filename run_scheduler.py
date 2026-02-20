#!/usr/bin/env python3
"""Standalone scheduled simulation runner for Jenbina.

Runs one simulation iteration every 5 hours, completely independent
of the Streamlit UI.

Usage:
    python run_scheduler.py                     # default user (id=1)
    python run_scheduler.py --user-id 3         # specific user
    python run_scheduler.py --interval-hours 1  # custom interval
    python run_scheduler.py --run-once          # single iteration, then exit
"""

import sys
import os
import signal
import argparse
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file (for OPENAI_API_KEY etc.)
from dotenv import load_dotenv
load_dotenv()

# Set env vars before any LangChain imports
os.environ['LANGSMITH_TRACING'] = 'false'
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "jenbina"

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.auth.user_db import UserDatabase
from core.person.person import Person
from core.connect import get_llm, get_json_llm
from core.cognition.meta_cognition import MetaCognitiveSystem
from core.simulation_runner import run_single_iteration_headless

logger = logging.getLogger("jenbina.scheduler")


def load_person(user_db, user_id, llm, llm_json_mode):
    """Load Person from SQLite, initializing all subsystems.

    Mirrors core/ui/shared_init.py:_load_or_create_person but without
    any Streamlit dependency.
    """
    saved_json = user_db.load_person_state(user_id)
    if saved_json:
        person = Person.deserialize(saved_json, llm_json_mode)
    else:
        person = Person()
        person.update_all_needs()

    if person.learning_system is None:
        person.init_learning_system(llm_json_mode)
    if person.goal_system is None:
        person.init_goal_system(llm_json_mode)
    if person.planning_system is None:
        person.init_planning_system(llm_json_mode)
    if person.inner_monologue is None:
        person.init_inner_monologue(llm)
    if person.social_cognition is None:
        person.init_social_cognition()
    if person.self_narrative is None:
        person.init_self_narrative()
    if person.curiosity_system is None:
        person.init_curiosity_system()
    # Skip insight_system — it's UI-only

    return person


def run_iteration(user_db, user_id, display_name, llm, llm_json_mode, meta_cog, context, counter):
    """Execute one simulation iteration and persist results."""
    iteration_num = counter[0]
    logger.info(f"Starting iteration {iteration_num + 1}")

    try:
        # Fresh load each iteration to pick up changes from the UI
        person = load_person(user_db, user_id, llm, llm_json_mode)

        result = run_single_iteration_headless(
            person=person,
            llm_json_mode=llm_json_mode,
            meta_cognitive_system=meta_cog,
            iteration=iteration_num,
            context=context,
        )

        # Append to simulation history
        iteration_record = {
            "iteration": iteration_num + 1,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": result["iteration_duration"],
            "action_decision": result["action_decision"],
            "needs_state": result["person_dict"]["maslow_needs"],
            "emotions_state": result["person_dict"].get("emotions", {}),
            "world_summary": result["world_summary"],
        }
        context.setdefault("simulation_history", []).append(iteration_record)

        # Persist person state
        user_db.save_person_state(user_id, person.serialize())

        action = result["action_decision"].get("chosen_action", "?") if isinstance(result["action_decision"], dict) else "?"
        logger.info(
            f"Iteration {iteration_num + 1} complete. "
            f"Action: {action} | "
            f"Satisfaction delta: {result['satisfaction_delta']:+.1f}%"
        )

        counter[0] += 1

    except Exception:
        logger.exception(f"Iteration {iteration_num + 1} failed")


def main():
    parser = argparse.ArgumentParser(description="Jenbina scheduled simulation runner")
    parser.add_argument("--user-id", type=int, default=1, help="SQLite user ID to simulate for (default: 1)")
    parser.add_argument("--interval-hours", type=float, default=5.0, help="Hours between iterations (default: 5)")
    parser.add_argument("--run-once", action="store_true", help="Run one iteration and exit")
    parser.add_argument("--list-users", action="store_true", help="List all users and exit")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    user_db = UserDatabase()

    if args.list_users:
        users = user_db.get_all_users()
        if not users:
            print("No users found in database.")
        else:
            print(f"{'ID':<6} {'Display Name':<30} {'Email':<40}")
            print("-" * 76)
            for u in users:
                print(f"{u['id']:<6} {u.get('display_name', ''):<30} {u.get('email', ''):<40}")
        return

    # Verify user exists
    user = user_db.get_user_by_id(args.user_id)
    if user is None:
        logger.error(f"No user found with id={args.user_id}. Use --list-users to see available users.")
        sys.exit(1)

    display_name = user.get("display_name") or user.get("email", "User")
    logger.info(f"Simulating for user: {display_name} (id={user['id']})")

    # Initialize LLMs (same config as core/ui/shared_init.py:init_llm)
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "openai-advanced")
    llm = get_llm(provider=chat_model, temperature=1, max_tokens=600)
    llm_json_mode = get_json_llm(provider="openai", temperature=1)

    meta_cog = MetaCognitiveSystem(llm_json_mode)
    context = {
        "simulation_history": [],
        "jenbina_location": "Jenbina's House",
        "debug_iterations": [],
        "user_db": user_db,
        "user_id": args.user_id,
        "display_name": display_name,
    }
    counter = [0]  # mutable int in list for closure

    # Run once immediately
    run_iteration(user_db, args.user_id, display_name, llm, llm_json_mode, meta_cog, context, counter)

    if args.run_once:
        logger.info("Single iteration complete. Exiting.")
        return

    # Schedule recurring iterations
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_iteration,
        trigger=IntervalTrigger(hours=args.interval_hours),
        args=[user_db, args.user_id, display_name, llm, llm_json_mode, meta_cog, context, counter],
        id="simulation_iteration",
        name="Jenbina Simulation Iteration",
        max_instances=1,
        coalesce=True,
    )

    # Graceful shutdown
    def shutdown(signum, frame):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info(f"Scheduler started. Next iteration in {args.interval_hours} hours.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
