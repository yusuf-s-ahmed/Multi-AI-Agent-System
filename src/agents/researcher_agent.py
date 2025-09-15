import ollama
import json
from pydantic import BaseModel
from helpers.llm_utils import clean_llm_json
from typing import Any

class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

def web_scrape(query: str) -> DirectAnswer:
    prompt = f"""
You are an AI researcher. Simulate web scraping for the following query:
'{query}'

Rules:
- Return strictly JSON:
{{
    "answer": "...",
    "reasoning": "...",
    "confidence": 0.0
}}
- Use placeholders for the data, since actual web scraping is not implemented.
"""
    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = clean_llm_json(response["message"]["content"].strip())
    parsed = json.loads(raw_output)
    return DirectAnswer(**parsed)
