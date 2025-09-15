import pandas as pd
import ollama
import json
from pydantic import BaseModel
from helpers.llm_utils import clean_llm_json
from typing import Any, Optional, List

class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

def analyze_csv(df: pd.DataFrame) -> DirectAnswer:
    csv_text = df.to_csv(index=False) if df is not None else "No CSV data"
    prompt = f"""
You are a data analyst AI. Analyze the CSV data below and provide a summary of the company's performance.

CSV Data:
{csv_text}

Rules:
- Output strictly in JSON:
{{
    "answer": "...",
    "reasoning": "...",
    "confidence": 0.0
}}
- Include totals, averages, or trends if relevant.
"""
    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = clean_llm_json(response["message"]["content"].strip())
    parsed = json.loads(raw_output)
    return DirectAnswer(**parsed)
