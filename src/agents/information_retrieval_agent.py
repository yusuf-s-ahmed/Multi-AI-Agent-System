import ollama
import json
from pydantic import BaseModel
from helpers.llm_utils import clean_llm_json
from typing import Any

class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

def fetch_api_data(endpoint: str) -> DirectAnswer:
    prompt = f"""
You are an AI information retrieval agent. Simulate an API call to:
'{endpoint}'

Rules:
- Return strictly JSON:
{{
    "answer": "...",
    "reasoning": "...",
    "confidence": 0.0
}}
- Include a placeholder response for now.
"""
    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = clean_llm_json(response["message"]["content"].strip())
    parsed = json.loads(raw_output)
    return DirectAnswer(**parsed)
