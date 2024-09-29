### LLM
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
local_llm = 'llama3.2:3b-instruct-fp16'
llm = ChatOllama(model=local_llm, temperature=0)
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')

import os

os.environ["LANGCHAIN_API_KEY"] = "*"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "local-llama32-rag"

### Generate

# Prompt
rag_prompt = """Hello, how are you?"""

generation = llm.invoke([HumanMessage(content=rag_prompt)])
print(generation.content)