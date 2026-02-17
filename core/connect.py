import os
from typing import Literal
from langchain_openai import ChatOpenAI



LLMProvider = Literal["openai", "openai-advanced"]

def get_llm(provider: LLMProvider = "openai", temperature: float = 1, max_tokens: int = None):
    """
    Get LLM instance based on provider preference.

    Args:
        provider: Which LLM service to use
            - "openai": GPT-5-nano (default, cost-effective and powerful)
            - "openai-advanced": GPT-5.2 (for complex reasoning tasks)
        temperature: Creativity level (0 = deterministic, 1 = creative)
        max_tokens: Optional cap on response length

    Returns:
        LLM instance ready to use
    """

    if provider == "openai":
        # Default: Cost-effective and reliable
        kwargs = dict(
            model="gpt-5-nano",
            temperature=temperature,
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return ChatOpenAI(**kwargs)

    elif provider == "openai-advanced":
        # For complex reasoning and meta-cognition
        kwargs = dict(
            model="gpt-5.2",
            temperature=temperature,
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return ChatOpenAI(**kwargs)

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
            model_kwargs={"response_format": {"type": "json_object"}},
            api_key=os.getenv('OPENAI_API_KEY')
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")


# Recommended configurations for different use cases
RECOMMENDED_CONFIGS = {
    "development": "openai",           # Fast iteration, good quality
    "production": "openai",            # Cost-effective for production
    "meta_cognition": "openai-advanced",  # Best reasoning for complex tasks
}

def get_recommended_llm(use_case: str = "development", temperature: float = 0):
    """
    Get LLM with recommended configuration for specific use case.

    Args:
        use_case: One of "development", "production", "meta_cognition"
        temperature: Creativity level

    Returns:
        LLM instance configured for the use case
    """
    provider = RECOMMENDED_CONFIGS.get(use_case, "openai")
    return get_llm(provider=provider, temperature=temperature)
