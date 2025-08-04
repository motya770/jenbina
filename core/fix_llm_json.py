import json
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from typing import Dict, Any

def fix_llm_json(broken_json: str, llm_json_mode: BaseLLM) -> Dict[str, Any]:
    """
    Attempts to fix and parse JSON from LLM output that may be malformed.
    
    Args:
        broken_json: The potentially malformed JSON string
        llm_json_mode: Language model instance configured for JSON output
        
    Returns:
        Dict containing the parsed JSON
    """
    # First try direct parsing
    try:
        return json.loads(broken_json)
    except json.JSONDecodeError:
        # Try to extract JSON-like content between braces if present
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, broken_json, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        # If still invalid, use LLM to fix it
        fix_json_prompt = PromptTemplate(
            input_variables=["broken_json"],
            template="Fix this invalid JSON and return ONLY valid JSON without any additional text:\n\n{broken_json}"
        )
        
        fix_json_chain = LLMChain(
            llm=llm_json_mode,
            prompt=fix_json_prompt
        )
        
        try:
            fixed_json = fix_json_chain.invoke({"broken_json": broken_json})
            
            # Try to parse the fixed JSON
            return json.loads(fixed_json['text'])
        except (json.JSONDecodeError, KeyError, Exception):
            # If still invalid, try with strict structure
            strict_fix_prompt = PromptTemplate(
                input_variables=["broken_json"],
                template="Convert this content to valid JSON with this structure: {\"key1\": \"value1\", \"key2\": \"value2\"}\n\nContent: {broken_json}"
            )
            
            try:
                fixed_json = LLMChain(
                    llm=llm_json_mode,
                    prompt=strict_fix_prompt
                ).invoke({"broken_json": broken_json})
                
                return json.loads(fixed_json['text'])
            except (json.JSONDecodeError, KeyError, Exception):
                # If all else fails, return a basic structure
                return {"error": "Failed to parse JSON", "original": broken_json}