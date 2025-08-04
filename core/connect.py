import os
import openai

# Configuration for different LLM providers
SAMBANOVA_API_KEY = os.getenv('SAMBANOVA_API_KEY', '5dfbcc36-cb42-4a1f-b691-f8fd801d5a85')
SAMBANOVA_BASE_URL = "https://api.sambanova.ai/v1"

from langchain_ollama import ChatOllama

def get_local_llm():
    """Get local Ollama LLM instance"""
    local_llm = 'llama3.2:3b-instruct-fp16'
    return ChatOllama(model=local_llm, temperature=0)

def get_sambanova_llm():
    """Get SambaNova LLM instance"""
    local_llm = 'llama3.2:3b-instruct-fp16'
    return ChatOllama(
        model=local_llm, 
        temperature=0, 
        api_key=SAMBANOVA_API_KEY,
        base_url=SAMBANOVA_BASE_URL
    )

def get_json_llm():
    """Get LLM configured for JSON output"""
    local_llm = 'llama3.2:3b-instruct-fp16'
    return ChatOllama(model=local_llm, temperature=0, format='json')

