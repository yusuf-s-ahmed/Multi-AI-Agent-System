from pydantic import BaseModel
from typing import Dict, List
import json
import re

# ----------------------------
# Define structured outputs
# ----------------------------
class CSVOutput(BaseModel):
    total_revenue: float
    best_quarter: str

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
# Function to analyze CSV data
# ----------------------------
def analyze_csv_data(data: Dict[str, List[float]]) -> CSVOutput:
    """
    Analyze CSV data to calculate total revenue and the best quarter.
    """
    if not all(isinstance(x, (int, float)) for x in data["revenue"]):
        raise ValueError("All revenue values must be numbers.")
    
    total_revenue = sum(data["revenue"])
    best_quarter_index = data["revenue"].index(max(data["revenue"]))
    best_quarter = data["quarter"][best_quarter_index]
    
    return CSVOutput(total_revenue=total_revenue, best_quarter=best_quarter)

# ----------------------------
# Function to handle CSV analysis request
# ----------------------------
def handle_csv_analysis_request(data: Dict[str, List[float]]) -> str:
    result = analyze_csv_data(data)
    return json.dumps(result.dict())