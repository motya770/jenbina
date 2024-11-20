# Only proceed with action if it's compliant with Asimov's Laws
if compliance_check["compliant"]:
    # Create prompt to analyze action results and state changes
    state_analysis_prompt = PromptTemplate(
        template="""Given an action that was taken, analyze how it affects the internal state of the person.
        Consider emotional, physical, and mental changes that may result.

        Action taken: {action}
       
        Respond in JSON format with:
        - hunger_level: specific numerical change to hunger level     
        """
    )

    # Create chain for state analysis
    state_analysis_chain = LLMChain(
        llm=llm,
        prompt=state_analysis_prompt,
        verbose=True
    )

    # Analyze state changes
    try:
        state_changes = state_analysis_chain.run(action=action_decision)
        print(state_changes)
        state_result = json.loads(state_changes)
        print(f"\nState Changes After Action: {state_result}")
    except json.JSONDecodeError:
        print("\nError analyzing state changes after action")
else:
    print("\nAction not taken - failed Asimov compliance check")
