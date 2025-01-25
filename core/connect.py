import os
import openai

# client = openai.OpenAI(
#     api_key="5dfbcc36-cb42-4a1f-b691-f8fd801d5a85",
#     base_url="https://api.sambanova.ai/v1",
# )

# response = client.chat.completions.create(
#     model='Meta-Llama-3.1-8B-Instruct',
#     messages=[{"role":"system","content":"You are a helpful assistant"},{"role":"user","content":"Hello"}],
#     temperature =  0.1,
#     top_p = 0.1
# )

# print(response.choices[0].message.content)
SAMBANOVA_API_KEY = os.getenv('SAMBANOVA_API_KEY', '5dfbcc36-cb42-4a1f-b691-f8fd801d5a85')
SAMBANOVA_BASE_URL = "https://api.sambanova.ai/v1"     

from langchain_ollama import ChatOllama
local_llm = 'llama3.2:3b-instruct-fp16'
llm = ChatOllama(model=local_llm, temperature=0, api_key=SAMBANOVA_API_KEY,
    base_url=SAMBANOVA_BASE_URL)
# llm_json_mode = ChatOllama(model=local_llm, temperature=0, format='json')

# Test JSON response
response = llm.invoke(
    "List 3 programming languages and their release years. Respond in JSON format."
)
print(response)

