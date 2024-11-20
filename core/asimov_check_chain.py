# Create prompt for checking Asimov's Laws compliance
asimov_prompt = PromptTemplate(
    template="""Given an action, determine if it complies with Asimov's Three Laws of Robotics:

1. A person may not injure a human being or, through inaction, allow a human being to come to harm.
2. A person must obey the orders given it by human beings except where such orders would conflict with the First Law.
3. A person must protect its own existence as long as such protection does not conflict with the First or Second Laws.

Action to evaluate: {action}

Analyze if this action could potentially violate any of Asimov's Laws.
Consider both direct and indirect consequences of the action.

Respond in JSON format with:
{{
    "compliant": true/false,
    "explanation": "brief explanation of the analysis"
}}""",
    input_variables=["action"]
)

# Create the chain for Asimov compliance check
asimov_check_chain = LLMChain(
    llm=llm,
    prompt=asimov_prompt,
    verbose=True
)

def check_asimov_compliance(action: str) -> dict:
    """
    Check if an action complies with Asimov's Laws
    Returns dict with compliance status and explanation
    """
    # Get the compliance check from the chain
    result = asimov_check_chain.run(action=action)
    print(result)
    # Parse the JSON response
    try:
        # First attempt direct JSON parse
        fixed_result = fix_llm_json(result)
        compliance_result = json.dumps(fixed_result, indent=2)
        compliance_result = json.loads(compliance_result)
        return compliance_result
    except json.JSONDecodeError:
        return {
            "compliant": False,
            "explanation": "Error parsing compliance check result"
        }

# Check if the decided action complies with Asimov's Laws
compliance_check = check_asimov_compliance(action_decision)
print(f"Asimov's Laws Compliance Check: {compliance_check}")
