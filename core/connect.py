import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama



LLMProvider = Literal["openai", "openai-advanced", "ollama", "sambanova"]

def get_llm(provider: LLMProvider = "openai", temperature: float = 1):
    """
    Get LLM instance based on provider preference.
    
    Args:
        provider: Which LLM service to use
            - "openai": GPT-4o-mini (default, cost-effective and powerful)
            - "openai-advanced": GPT-4o (for complex reasoning tasks)
            - "ollama": Local Llama 3.2 (offline/privacy mode)
            - "sambanova": SambaNova cloud LLM
        temperature: Creativity level (0 = deterministic, 1 = creative)
    
    Returns:
        LLM instance ready to use
    """
    
    if provider == "openai":
        # Default: Cost-effective and reliable
        return ChatOpenAI(
            model="gpt-5-nano",
            temperature=temperature,
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    elif provider == "openai-advanced":
        # For complex reasoning and meta-cognition
        return ChatOpenAI(
            model="gpt-5.2",
            temperature=temperature,
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    elif provider == "ollama":
        # Local fallback for offline/privacy needs
        local_llm = 'llama3.2:3b-instruct-fp16'
        return ChatOllama(model=local_llm, temperature=temperature)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_json_llm(provider: LLMProvider = "openai", temperature: float = 1):
    """
    Get LLM configured for reliable JSON output.
    
    Args:
        provider: Which LLM service to use
        temperature: Creativity level (0 = deterministic)
    
    Returns:
        LLM instance configured for JSON mode
    """
    
    if provider == "openai" or provider == "openai-advanced":
        model = "gpt-5.2" if provider == "openai-advanced" else "gpt-5-nano"
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    elif provider == "ollama":
        local_llm = 'llama3.2:3b-instruct-fp16'
        return ChatOllama(model=local_llm, temperature=temperature, format='json')
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Legacy functions for backwards compatibility
def get_local_llm():
    """Get local Ollama LLM instance (legacy)"""
    return get_llm(provider="ollama")

def get_sambanova_llm():
    """Get SambaNova LLM instance (legacy)"""
    return get_llm(provider="sambanova")


# Recommended configurations for different use cases
RECOMMENDED_CONFIGS = {
    "development": "openai",           # Fast iteration, good quality
    "production": "openai",            # Cost-effective for production
    "meta_cognition": "openai-advanced",  # Best reasoning for complex tasks
    "offline": "ollama",               # Local/privacy mode
}

def get_recommended_llm(use_case: str = "development", temperature: float = 0):
    """
    Get LLM with recommended configuration for specific use case.
    
    Args:
        use_case: One of "development", "production", "meta_cognition", "offline"
        temperature: Creativity level
    
    Returns:
        LLM instance configured for the use case
    """
    provider = RECOMMENDED_CONFIGS.get(use_case, "openai")
    return get_llm(provider=provider, temperature=temperature)

