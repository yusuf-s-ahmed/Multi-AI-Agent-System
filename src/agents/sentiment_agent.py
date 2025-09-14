from pydantic import BaseModel
from typing import List
import re
import json
import ollama

# ----------------------------
# Define structured outputs
# ----------------------------
class SentimentOutput(BaseModel):
    positive: int
    negative: int
    neutral: int

# ----------------------------
# Helper to clean LLM JSON
# ----------------------------
def clean_llm_json(raw_text: str) -> str:
    """
    Remove Markdown code fences or other extra text so it's pure JSON.
    """
    cleaned = re.sub(r"```(?:json)?\n([\s\S]*?)```", r"\1", raw_text, flags=re.MULTILINE)
    return cleaned.strip()

# ----------------------------
# Helper to call LLM
# ----------------------------
def ask_llama(prompt: str, model: str = "gemma3:4b") -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# ----------------------------
# Sentiment analysis agent
# ----------------------------
def analyze_sentiment(news: List[str]) -> SentimentOutput:
    prompt = f"""
    You are an AI assistant analyzing news sentiment.
    News headlines: {news}
    Return JSON with positive, negative, neutral counts.
    """
    response = ask_llama(prompt)
    cleaned_response = clean_llm_json(response)
    parsed_result = SentimentOutput.parse_raw(cleaned_response)  # Use parse_raw instead of model_validate_json
    return parsed_result