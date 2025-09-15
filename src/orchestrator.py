import pandas as pd
import ollama
import json
import re
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Any, List
from helpers.llm_utils import clean_llm_json

# ----------------------------
# Strict JSON schemas
# ----------------------------
class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

class ToolCall(BaseModel):
    tool: str = Field(..., description="The name of the tool to call")
    details: str = Field(..., description="Instructions for the tool")
    require_csv: Optional[bool] = Field(False, description="Does the tool require CSV data?")

class MultiToolCall(BaseModel):
    action: str = Field(..., description="Always 'use_tool'")
    tools: List[ToolCall]

class ToolSpec(BaseModel):
    name: str = Field(..., description="Short identifier for the tool")
    description: str = Field(..., description="What the tool does")
    requires_csv: bool = Field(False, description="Does this tool require CSV data?")

# Define available tools
available_tools: List[ToolSpec] = [
    ToolSpec(name="csv", description="Analyze uploaded company's CSV data for totals, averages, metrics.", requires_csv=True),
    ToolSpec(name="sentiment", description="Analyze sentiment of text entries.", requires_csv=False),
    ToolSpec(name="api_call", description="Fetch external data.", requires_csv=False)
]

# ----------------------------
# CSV Loader
# ----------------------------
def handle_csv_upload(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

# ----------------------------
# Step 1: Select tools
# ----------------------------
def select_tools(question: str, data: Optional[pd.DataFrame] = None) -> MultiToolCall:
    data_summary = data.to_csv(index=False) if data is not None else ""
    csv_text = f"Here is some CSV data:\n{data_summary}" if data_summary else "No CSV data is provided."
    tools_json = json.dumps([tool.dict() for tool in available_tools], indent=2)

    prompt = f"""
You are an advanced AI assistant. Based on the question and CSV data below, decide which tools to use.  
Do NOT produce a full answer, only return JSON in this format:

{{
  "action": "use_tool",
  "tools": [
    {{
      "tool": "<tool_name_from_available_tools>",
      "details": "Explain what the tool should do",
      "require_csv": true|false
    }}
  ]
}}

CSV context:
{csv_text}

Question: {question}

Available tools:
{tools_json}

Rules:
- Only include tools actually needed to answer the question.
- Always include "api_call" if the question requires external context.
- Output strictly valid JSON.
"""
    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = clean_llm_json(response["message"]["content"].strip())
    parsed = json.loads(raw_output)
    return MultiToolCall(**parsed)

# ----------------------------
# Step 2: Generate final answer
# ----------------------------
def generate_answer(question: str, tools_used: MultiToolCall, data: Optional[pd.DataFrame] = None) -> DirectAnswer:
    data_summary = data.to_csv(index=False) if data is not None else ""
    tools_json = json.dumps([tool.dict() for tool in tools_used.tools], indent=2)

    prompt = f"""
You are an advanced AI assistant. Based on the question, CSV data, and tools selected, produce a final answer.

Question: {question}

CSV data:
{data_summary if data_summary else 'No CSV provided'}

Tools selected:
{tools_json}

Rules:
- Format output strictly in JSON:
{{
  "answer": "...",
  "reasoning": "...",
  "confidence": 0.0
}}
- Include reasoning that explains how tools were used.
"""
    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_output = clean_llm_json(response["message"]["content"].strip())
    parsed = json.loads(raw_output)
    return DirectAnswer(**parsed)

# ----------------------------
# Orchestrator
# ----------------------------
def process_csv_and_question(file_path: str, question: str):
    csv_data = handle_csv_upload(file_path)
    tools_used = select_tools(question, csv_data)
    final_answer = generate_answer(question, tools_used, csv_data)
    return {
        "tools_used": tools_used.dict(),
        "final_answer": final_answer.dict()
    }

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    file_path = "C:\\Users\\yusuf\\Desktop\\AI Agents Prototype\\ai-agents-prototype\\data\\sales_data.csv"
    question = "How was our company performing based on the internal CSV sales data and the current external market trends?"

    try:
        result = process_csv_and_question(file_path, question)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
