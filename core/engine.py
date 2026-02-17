from .needs.maslow_needs import BasicNeeds
from .environment.world_state import WorldState, create_world_description_system
from .cognition.action_decision_chain import process_action_decision
from .cognition.asimov_check_chain import create_asimov_check_system
from .cognition.state_analysis_chain import create_state_analysis_system
from .person.person import Person
from .connect import get_llm, get_json_llm


def run_simulation():

    ### LLM
    # Options: "openai" (default), "openai-advanced"
    llm = get_llm(provider="openai", temperature=0)
    llm_json_mode = get_json_llm(provider="openai", temperature=0)

    # Initialize person and world state
    person = Person()
    person.init_inner_monologue(llm)
    person.init_social_cognition()
    person.init_self_narrative()
    person.init_curiosity_system()
    world = WorldState()

    # Create system components
    world_description_system = create_world_description_system(llm)
    asimov_check_system = create_asimov_check_system(llm)
    state_analysis_system = create_state_analysis_system(llm)

    last_action = "Nothing yet."

    # Main simulation loop
    while True:
        # Get world description
        world_description = world_description_system(person, world)

        if person.curiosity_system is not None:
            needs_snapshot_for_curiosity = person.get_needs_snapshot()
            person.curiosity_system.observe_cycle(
                needs=needs_snapshot_for_curiosity,
                world_context={"location": "simulation world", "time_of_day": "unknown", "weather": "unknown"},
                available_actions=[],
                recent_actions=[last_action] if last_action else [],
            )

        # Generate internal monologue before decision
        if person.inner_monologue is not None:
            needs_snapshot = person.get_needs_snapshot()
            emotions_snapshot = person.get_emotions_snapshot()
            working_memory_str = person.working_memory.format_for_prompt()

            needs_summary_str = ", ".join(
                f"{name}: {sat:.0f}%" for name, sat in needs_snapshot.items()
            )
            emotion_summary = person.emotion_system.get_emotional_state_summary()
            emotional_state_str = ", ".join(
                f"{name}: {val}" for name, val in emotion_summary["emotions"].items()
            )

            recent_exp_list = None
            recent_exp_str = "No notable recent experiences."
            if person.learning_system is not None:
                stats = person.learning_system.get_learning_stats()
                recent_exp_list = stats.get("recent_experiences", [])
                if recent_exp_list:
                    recent_exp_str = "\n".join(
                        f"- {e.get('action_taken', 'unknown')}: satisfaction {e.get('overall_satisfaction_before', 0):.0f}→{e.get('overall_satisfaction_after', 0):.0f}"
                        for e in recent_exp_list[-3:]
                    )

            lessons_str = "No lessons yet."
            if person.learning_system is not None:
                lessons_str = person.learning_system.format_lessons_for_prompt()

            goals_str = "No particular goals right now."
            if person.goal_system is not None:
                goals_str = person.goal_system.format_goals_for_prompt()

            person.inner_monologue.think(
                needs=needs_snapshot,
                emotions=emotions_snapshot,
                working_memory_str=working_memory_str,
                needs_summary_str=needs_summary_str,
                emotional_state_str=emotional_state_str,
                world_context_str="Simulation world.",
                recent_action_str=last_action,
                recent_experiences_list=recent_exp_list,
                recent_experiences_str=recent_exp_str,
                lessons_learned_str=lessons_str,
                goals_str=goals_str,
            )

        # Decide on action
        action_decision = process_action_decision(person, world_description, llm)
        last_action = action_decision.get("chosen_action", "unknown")
        if person.curiosity_system is not None:
            person.curiosity_system.update_after_action(last_action)

        # Check if action complies with Asimov's Laws
        compliance_check = asimov_check_system(action_decision["chosen_action"])

        # Analyze state changes if action is compliant
        state_changes = state_analysis_system(
            action_decision["chosen_action"],
            compliance_check
        )

        # Update person's state if changes were analyzed
        if state_changes:
            person.update_all_needs()

        # TODO remove
        break
