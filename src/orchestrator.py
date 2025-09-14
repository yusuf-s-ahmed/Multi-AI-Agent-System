from agents.csv_agent import analyze_csv_data
from agents.sentiment_agent import analyze_sentiment as agent_sentiment_analysis
import json

def orchestrator():
    sales_data = {
        "quarter": ["Q1", "Q2", "Q3", "Q4"],
        "revenue": [12000, 15000, 17000, 16000]
    }

    news_headlines = [
        "Company X stock surges 10%",
        "Market downturn affects finance sector",
        "New product launch boosts revenue"
    ]

    csv_result = analyze_csv_data(sales_data)
    news_result = agent_sentiment_analysis(news_headlines)

    combined_output = {
        "csv_agent": csv_result.dict(),  # Use dict() instead of model_dump()
        "news_agent": news_result.dict()  # Use dict() instead of model_dump()
    }

    print(json.dumps(combined_output, indent=4))

if __name__ == "__main__":
    orchestrator()