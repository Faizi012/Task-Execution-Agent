
from crewai import LLM

llm = LLM(
    model="openai/qwen2.5:3b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0.1,
    timeout=300,
    max_tokens=512
)

print("Qwen local LLM configured!")
