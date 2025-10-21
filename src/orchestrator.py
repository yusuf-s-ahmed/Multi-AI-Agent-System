# orchestrator.py

import json
import traceback
from agents.planner_agent import handle_csv_upload, select_tools, generate_answer
from agents.context_memory import get_context_text

def log_status(stage: str, message: str):
    """Prints formatted debug messages for visibility."""
    print(f"[DEBUG] [{stage}] {message}")

def process_csv_and_question(file_path: str, question: str):
    try:
        log_status("0% COMPLETED", f"Starting process for question: '{question}'")
        log_status("0% COMPLETED", f"Loading CSV from {file_path}")
        csv_data = handle_csv_upload(file_path)
        log_status("10% COMPLETED", "CSV successfully loaded")

        log_status("10% COMPLETED", "Selecting tools based on question and CSV data")
        tools_used = select_tools(question, csv_data)
        log_status("30% COMPLETED", f"Tools selected: {[t.tool for t in tools_used.tools]}")

        log_status("30% COMPLETED", "Generating final answer using selected tools")

        # ---

        final_answer = generate_answer(question, tools_used, csv_data)

        # ---

        log_status("90% COMPLETED", "Final answer generated successfully")

        log_status("90% COMPLETED", "Retrieving context memory")
        context_text = get_context_text()

        result = {
            "tools_used": tools_used.dict(),
            "final_answer": final_answer.dict(),
            "context_memory": context_text
        }

        log_status("100% COMPLETED", "Process completed successfully")
        return result

    except Exception as e:
        log_status("ERROR", f"An error occurred: {e}")
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    file_path = "data/sales_data.csv"
    question = (
        "Based on the sales data, benchmark this against our competitors "
        "in the United Kingdom financial sector, HSBC, researching recent "
        "financial news, and getting real-time stock data from Yahoo Finance API "
        "to provide a comprehensive summary."
    )

    result = process_csv_and_question(file_path, question)
    print("\n=== FINAL OUTPUT ===")
    # print(json.dumps(result, indent=4, ensure_ascii=False))

    print(json.dumps(result["tools_used"], indent=4, ensure_ascii=False))
    print(json.dumps(result["final_answer"], indent=4, ensure_ascii=False))

    print("\n=== CONTEXT MEMORY IS SAVED ===")
    context = result["context_memory"]