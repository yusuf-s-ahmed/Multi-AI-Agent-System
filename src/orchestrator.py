import pandas as pd
from src.agents.csv_agent import analyze_csv_data
from src.agents.sentiment_agent import analyze_sentiment
import json

def handle_csv_upload(file_path: str) -> pd.DataFrame:
    """
    Parse the uploaded CSV file into a pandas DataFrame.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

def analyze_question(question: str) -> str:
    """
    Analyze the user's question and determine the intent.
    """
    question = question.lower()
    if "total" in question or "revenue" in question:
        return "calculate_total"
    elif "sentiment" in question or "news" in question:
        return "analyze_sentiment"
    else:
        return "unknown"

def route_request(intent: str, data, question: str):
    """
    Route the request to the appropriate agent based on the intent.
    """
    if intent == "calculate_total":
        # Convert DataFrame to dictionary for the CSV agent
        data_dict = data.to_dict(orient="list")
        return analyze_csv_data(data_dict).dict()
    elif intent == "analyze_sentiment":
        # Assume the DataFrame has a column "headlines" for sentiment analysis
        if "headlines" not in data.columns:
            raise ValueError("The CSV file must contain a 'headlines' column for sentiment analysis.")
        headlines = data["headlines"].tolist()
        return analyze_sentiment(headlines).dict()
    else:
        return {"error": "Unknown intent. Please ask about revenue or sentiment."}

def process_csv_and_question(file_path: str, question: str):
    """
    Orchestrate the process of handling a CSV file and a question.
    """
    data = handle_csv_upload(file_path)
    intent = analyze_question(question)
    result = route_request(intent, data, question)
    return result

if __name__ == "__main__":
    # Example usage
    file_path = "data/sales_data.csv"  # Replace with the path to your CSV file
    question = "What is the total revenue?"  # Replace with your question

    try:
        result = process_csv_and_question(file_path, question)
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"Error: {e}")