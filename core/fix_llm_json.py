import json

def fix_llm_json(broken_json: str) -> dict:
    """
    Attempts to fix and parse JSON from LLM output that may be malformed.
    Returns parsed JSON dict or raises JSONDecodeError if unfixable.
    """
    # First try direct parsing
    try:
        return json.loads(broken_json)
    except json.JSONDecodeError:
        # Try to extract JSON-like content between braces if present
        import re
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
            llm=llm_json_mode,  # Use JSON mode LLM
            prompt=fix_json_prompt
        )
        
        fixed_json = fix_json_chain.invoke({"broken_json": broken_json})
        
        try:
            # Try to parse the fixed JSON
            return json.loads(fixed_json['text'])
        except (json.JSONDecodeError, KeyError):
            # If still invalid, try with strict structure
            strict_fix_prompt = PromptTemplate(
                input_variables=["broken_json"],
                template="Convert this content to valid JSON with this structure: {\"key1\": \"value1\", \"key2\": \"value2\"}\n\nContent: {broken_json}"
            )
            
            fixed_json = LLMChain(
                llm=llm_json_mode,
                prompt=strict_fix_prompt
            ).invoke({"broken_json": broken_json})
            
            return json.loads(fixed_json['text'])