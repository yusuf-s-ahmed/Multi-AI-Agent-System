# planner_agent.py

import pandas as pd
import json
from pydantic import BaseModel
from typing import Any, Optional, List
from agents.data_analyst_agent import analyze_csv
from agents.researcher_agent import web_scrape
from agents.information_retrieval_agent import fetch_api_data
from agents.context_memory import save_context, get_context_text
import ollama
from helpers.llm_utils import clean_llm_json

# ----------------------------
# Schemas
# ----------------------------
class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

class ToolCall(BaseModel):
    tool: str
    details: str
    require_csv: Optional[bool] = False

class MultiToolCall(BaseModel):
    action: str
    tools: List[ToolCall]

class ToolSpec(BaseModel):
    name: str
    description: str
    requires_csv: bool = False

# ----------------------------
# Tools
# ----------------------------
available_tools: List[ToolSpec] = [
    ToolSpec(name="csv", description="Analyze uploaded CSV data for totals, averages, metrics.", requires_csv=True),
    ToolSpec(name="web_scrape", description="Research online news or updates about a topic.", requires_csv=False),
    ToolSpec(name="api_call", description="Fetch external market or company data.", requires_csv=False)
]

# ----------------------------
# CSV loader
# ----------------------------
def handle_csv_upload(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

# ----------------------------
# Step 1: Select tools dynamically
# ----------------------------
def select_tools(question: str, data: Optional[pd.DataFrame] = None) -> MultiToolCall:
    data_summary = data.to_csv(index=False) if data is not None else ""
    csv_text = f"CSV data:\n{data_summary}" if data_summary else "No CSV provided."
    tools_json = json.dumps([tool.dict() for tool in available_tools], indent=2)

    prompt = f"""
You are an AI planner. Based on the CSV and the question below, decide which tools to use.
Do NOT answer the question, only return JSON with the format:

{{
  "action": "use_tool",
  "tools": [
    {{"tool": "<tool_name>", "details": "Explain what the tool should do", "require_csv": true|false}}
  ]
}}

CSV context:
{csv_text}

Question: {question}

Available tools:
{tools_json}

Rules:
- Include "csv" if CSV is provided.
- Include "api_call" or "web_scrape" if the question mentions companies, stocks, or market trends.
- Return valid JSON only.
"""
    response = ollama.chat(model="llama3:8b", messages=[{"role": "user", "content": prompt}])
    raw_output = clean_llm_json(response["message"]["content"].strip())

    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, list):
            # Wrap list in action if LLM returned only tools
            parsed = {"action": "use_tool", "tools": parsed}
    except json.JSONDecodeError:
        parsed = {"action": "use_tool", "tools": []}

    # Ensure keys
    if "action" not in parsed:
        parsed["action"] = "use_tool"
    if "tools" not in parsed:
        parsed["tools"] = []

    return MultiToolCall(**parsed)

# ----------------------------
# Step 2: Generate final answer
# ----------------------------
def generate_answer(question: str, tools_used: MultiToolCall, data: Optional[pd.DataFrame] = None) -> DirectAnswer:
    agent_outputs = {}

    for tool in tools_used.tools:
        if tool.tool == "csv":
            res = analyze_csv(df=data)
            agent_outputs["csv"] = res.dict()
        elif tool.tool == "api_call":
            res = fetch_api_data(endpoint="https://placeholder.api")
            agent_outputs["api_call"] = res.dict()
        elif tool.tool == "web_scrape":
            res = web_scrape(query=question)
            agent_outputs["web_scrape"] = res.dict()
        else:
            agent_outputs[tool.tool] = {"answer": None, "reasoning": "Tool not implemented", "confidence": 0.0}

    # Save this run into in-memory context
    save_context(question, agent_outputs)

    # Build planner’s contextual answer
    context_text = get_context_text()
    planner_prompt = f"""
You are a reasoning agent.
Context:
{context_text}

Question: {question}

Tool outputs:
{json.dumps(agent_outputs, indent=2)}

Provide a final combined answer in JSON with keys:
- answer
- reasoning
- confidence
"""

    response = ollama.chat(model="llama3:8b", messages=[{"role": "user", "content": planner_prompt}])
    raw_output = clean_llm_json(response["message"]["content"].strip())

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed = {"answer": "Unable to generate final answer", "reasoning": "Parsing error", "confidence": 0.0}

    return DirectAnswer(**parsed)

