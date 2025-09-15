import pandas as pd
import ollama
import json
import re
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Any, List

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
# Clean Markdown JSON
# ----------------------------
def clean_llm_json(raw_output: str) -> str:
    """
    Extracts the first valid JSON object or array from LLM output,
    even if extra text surrounds it.
    """
    # Remove code block markers
    raw_output = raw_output.strip().strip("`")
    raw_output = raw_output.replace("json\n", "").replace("json", "").strip()

    # Regex: find first {...} or [...]
    match = re.search(r'(\{.*\}|\[.*\])', raw_output, re.DOTALL)
    if match:
        return match.group(1)
    return raw_output

# ----------------------------
# Ask Gemma
# ----------------------------
def ask_llm(question: str, data: Optional[pd.DataFrame] = None) -> dict:
    """
    Ask the LLM a question. The LLM can decide whether it can answer directly
    or if one or more tools from `available_tools` are needed.
    """
    data_summary = data.to_csv(index=False) if data is not None else ""
    csv_text = f"Here is some CSV data:\n{data_summary}" if data_summary else "No CSV data is provided."

    tools_json = json.dumps([tool.dict() for tool in available_tools], indent=2)

    prompt = f"""
You are an advanced AI assistant (Llama 3).

Here is the CSV context:
{csv_text}

Question: {question}

Available tools:
{tools_json}

Rules:
1. Always consider both internal CSV data and external context if mentioned in the question.
2. First, evaluate whether the CSV has enough rows, columns, and relevant information to answer the question.
3. Only set `"require_csv": true` if the tool genuinely needs the CSV data to run.
4. If the question explicitly references external context (like "market trends"), you must include the external API tool.
5. Do not include any explanatory text outside the JSON. Output ONLY valid JSON.

Respond STRICTLY in valid JSON with one of these formats:

Direct answer:
{{
  "answer": "...",
  "reasoning": "...",
  "confidence": 0.0
}}

Tool call (one or more tools):
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
"""


    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = clean_llm_json(response["message"]["content"].strip())

    # Validate JSON strictly
    try:
        parsed = json.loads(raw_output)
        if parsed.get("action") == "use_tool":
            if "tools" in parsed:
                return MultiToolCall(**parsed).dict()
            else:
                return MultiToolCall(action="use_tool", tools=[ToolCall(**parsed)]).dict()
        else:
            return DirectAnswer(**parsed).dict()
    except (json.JSONDecodeError, ValidationError) as e:
        return {
            "error": "Invalid JSON returned by model",
            "raw_response": raw_output,
            "validation_error": str(e)
        }

# ----------------------------
# Orchestrator
# ----------------------------
def process_csv_and_question(file_path: str, question: str):
    """
    Returns either DirectAnswer or MultiToolCall.
    Does NOT execute any tools automatically.
    """
    csv_data = handle_csv_upload(file_path)
    return ask_llm(question, data=csv_data)


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    file_path = "C:\\Users\\yusuf\\Desktop\\AI Agents Prototype\\ai-agents-prototype\\data\\sales_data.csv"  # Example
    question = "How was our company performing based on the internal CSV sales data and the current external market trends?"

    try:
        result = process_csv_and_question(file_path, question)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
