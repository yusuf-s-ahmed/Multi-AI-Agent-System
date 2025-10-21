# planner_agent.py

import pandas as pd
import json
import re
import random
from pydantic import BaseModel
from typing import Any, Optional, List
import yfinance as yf
import ollama
from agents.data_analyst_agent import analyze_csv
from agents.researcher_agent import web_scrape
from agents.context_memory import save_context, get_context_text
from agents.information_retrieval_agent import fetch_stock_data
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
    ToolSpec(name="api_call", description="Fetch stock/market/company data from Yahoo Finance.", requires_csv=False)
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
# Ticker extraction
# ----------------------------
FALLBACK_FIN_TICKERS = ["HSBC", "UBS"]

def extract_tickers(text: str) -> list[str]:
    tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
    valid_tickers = [t for t in tickers if t not in ["API"]]
    if not valid_tickers:
        valid_tickers = random.sample(FALLBACK_FIN_TICKERS, k=min(2, len(FALLBACK_FIN_TICKERS)))
    return list(set(valid_tickers))

# ----------------------------
# Fetch stock data
# ----------------------------

"""

def fetch_stock_data(ticker: str) -> DirectAnswer:
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info

        if not fast or fast.get("lastPrice") is None:
            return DirectAnswer(
                answer={},
                reasoning=f"No financial data found for ticker '{ticker}' (possibly invalid or delisted)",
                confidence=0.0
            )

        key_data = {
            "symbol": ticker.upper(),
            "lastPrice": fast.get("lastPrice"),
            "marketCap": fast.get("marketCap"),
            "yearHigh": fast.get("yearHigh"),
            "yearLow": fast.get("yearLow"),
            "sharesOutstanding": fast.get("sharesOutstanding"),
        }

        return DirectAnswer(answer=key_data, reasoning=f"Fetched Yahoo Finance fast_info data for ticker '{ticker}'.", confidence=0.95)

    except Exception as e:
        return DirectAnswer(
            answer={},
            reasoning=f"Error fetching data for ticker '{ticker}': {e}",
            confidence=0.0
        )

"""

# ----------------------------
# Summarize stock (optional)
# ----------------------------
def summarize_stock(ticker: str) -> str:
    result = fetch_stock_data(ticker)
    if not result.answer:
        return f"Cannot summarize: {result.reasoning}"

    prompt = f"""
You are a financial analyst. Analyse this stock data in lots of detail, include key metrics, in 3-4 concise sentences:

{json.dumps(result.answer, indent=2)}

Return strictly plain text.
"""
    try:
        response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        print("Unable to summarise stock data:")
        return f"Unable to summarise stock data: {e}"

# ----------------------------
# Select tools dynamically
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
- Include "api_call" if the question asks about companies, tickers, or stock/market data.
- Include "web_scrape" if the question asks about news or trends.
- Return valid JSON only.
"""
    response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": prompt}])
    raw_output = clean_llm_json(response["message"]["content"].strip())

    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, list):
            parsed = {"action": "use_tool", "tools": parsed}
    except json.JSONDecodeError:
        parsed = {"action": "use_tool", "tools": []}

    if "action" not in parsed:
        parsed["action"] = "use_tool"
    if "tools" not in parsed:
        parsed["tools"] = []

    return MultiToolCall(**parsed)

# ----------------------------
# Generate final answer
# ----------------------------
def generate_answer(question: str, tools_used: MultiToolCall, data: Optional[pd.DataFrame] = None) -> DirectAnswer:
    agent_outputs = {}

    for tool in tools_used.tools:
        if tool.tool == "csv":
            res = analyze_csv(df=data)
            agent_outputs["csv"] = res.dict()
            print("[DEBUG] [40% COMPLETED] CSV analysis complete")

        elif tool.tool == "api_call":
            tickers = extract_tickers(tool.details or question)
            print("[DEBUG] [45% COMPLETED] ticker(s) extracted", tickers)
            api_results = {}
            for ticker in tickers:
                count = 1
                res = fetch_stock_data(ticker)
                print(f"[DEBUG] [50% COMPLETED] API call complete for ticker {count}: ", ticker)
                if res.answer:
                    formatted = (
                        f"Symbol: {res.answer.get('symbol')}\n"
                        f"Last Price: {res.answer.get('lastPrice')}\n"
                        f"Market Cap: {res.answer.get('marketCap')}\n"
                        f"52-Week High: {res.answer.get('yearHigh')}\n"
                        f"52-Week Low: {res.answer.get('yearLow')}\n"
                        f"Shares Outstanding: {res.answer.get('sharesOutstanding')}"
                    )
                    api_results[ticker] = {"raw": res.dict(), "formatted": formatted}
                    print("Stock data found for: ", ticker)
                else:
                    api_results[ticker] = res.dict()
                    print("Stock data not found for:", ticker)
                count += 1

            agent_outputs["api_call"] = api_results

        elif tool.tool == "web_scrape":
            res = web_scrape(query=question)
            agent_outputs["web_scrape"] = res.dict()
            print("[DEBUG] [50% COMPLETED] web scraping complete")

        else:
            agent_outputs[tool.tool] = {"answer": None, "reasoning": "Tool not implemented", "confidence": 0.0}

    save_context(question, agent_outputs)
    context_text = get_context_text()

    print("[DEBUG] [55% COMPLETED] web scraping complete")

    planner_prompt = f"""
You are a reasoning agent.

Context:
{context_text}

Question: {question}

Tool outputs:
{json.dumps(agent_outputs, indent=2)}

Instructions:
- Include all stock metrics (symbol, lastPrice, marketCap, yearHigh, yearLow, sharesOutstanding) in your final answer.
- Include revenue data from CSV if available.
- Include insights from web scraping if available.
- Provide a combined summary that mentions trends, stock data, and research insights.
- Return JSON with keys: answer, reasoning, confidence
"""

    print("[DEBUG] [Attempting to generate final answer]")

    response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": planner_prompt}])
    raw_output = clean_llm_json(response["message"]["content"].strip())

    print("[DEBUG] [Successfully generated final answer]")

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed = {"answer": "Unable to generate final answer", "reasoning": "Parsing error", "confidence": 0.0}

    return DirectAnswer(**parsed)

# ----------------------------
# CLI Example
# ----------------------------
if __name__ == "__main__":
    while True:
        question = input("Enter a question (or 'exit' to quit): ").strip()
        if question.lower() == "exit":
            break

        df = None  # optionally load CSV here
        tools = select_tools(question, data=df)
        final_answer = generate_answer(question, tools_used=tools, data=df)

        print("\nFinal Answer JSON:")
        print(json.dumps(final_answer.dict(), indent=2))
        print("\n" + "-"*50 + "\n")
