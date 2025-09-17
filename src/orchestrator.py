# orchestrator.py

from agents.planner_agent import handle_csv_upload, select_tools, generate_answer
from agents.context_memory import save_context, get_context_text
import json

def process_csv_and_question(file_path: str, question: str):
    csv_data = handle_csv_upload(file_path)
    tools_used = select_tools(question, csv_data)
    final_answer = generate_answer(question, tools_used, csv_data)
    context_text = get_context_text()
    return {
        "tools_used": tools_used.dict(),
        "final_answer": final_answer.dict(),
        "context_memory": get_context_text()
    }

if __name__ == "__main__":
    file_path = "data/sales_data.csv"
    question = "Based on the sales data, benchmark this against our competitors in the UK financial sector, researching recent financial news, and getting real-time stock data from Yahoo Finance API to provide a comprehensive summary."

    result = process_csv_and_question(file_path, question)
    print(json.dumps(result, indent=4, ensure_ascii=False))