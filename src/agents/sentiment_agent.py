from pydantic import BaseModel
from typing import List
import re

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
# Sentiment analysis agent
# ----------------------------
def analyze_sentiment(news: List[str]) -> SentimentOutput:
    """
    Analyze sentiment of news headlines.
    """
    if not news:
        return SentimentOutput(positive=0, negative=0, neutral=0)
    
    # Simulated response from LLM
    raw_response = """
    {
        "positive": 2,
        "negative": 1,
        "neutral": 0
    }
    """
    cleaned_response = clean_llm_json(raw_response)
    return SentimentOutput.parse_raw(cleaned_response)