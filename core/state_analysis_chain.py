import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from typing import Dict, Any, Callable, Optional

def create_state_analysis_system(llm: BaseLLM, action_decision: str) -> Callable:
    """
    Creates and returns a function that analyzes state changes after actions.
    
    Args:
        llm: Language model instance
    
    Returns:
        Callable that analyzes state changes
    """
    state_analysis_prompt = PromptTemplate(
        input_variables=["action"],
        template="""Given an action that was taken, analyze how it affects the internal state of the person.
        Consider emotional, physical, and mental changes that may result.

        Action taken: {action}
       
        Respond in JSON format with:
        - hunger_level: specific numerical change to hunger level     
        """
    )

    state_analysis_chain = LLMChain(
        llm=llm,
        prompt=state_analysis_prompt,
        verbose=True
    )

    def analyze_state_changes(action_decision: str, compliance_check: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes state changes after an action if it passes compliance check.
        
        Args:
            action_decision: The action to analyze
            compliance_check: Dict containing compliance check results
            
        Returns:
            Dict containing state changes or None if compliance check fails
        """
        if not compliance_check["compliant"]:
            print("\nAction not taken - failed Asimov compliance check")
            return None

        try:
            state_changes = state_analysis_chain.run(action=action_decision)
            state_result = json.loads(state_changes)
            print(f"\nState Changes After Action: {state_result}")
            return state_result
        except json.JSONDecodeError:
            print("\nError analyzing state changes after action")
            return None

    return analyze_state_changes
