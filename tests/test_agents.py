from src.agents.csv_agent import agent_csv_analysis
from src.agents.sentiment_agent import agent_sentiment_analysis
from pydantic import ValidationError
import pytest

def test_agent_csv_analysis():
    test_data = {
        "quarter": ["Q1", "Q2", "Q3", "Q4"],
        "revenue": [12000, 15000, 17000, 16000]
    }
    expected_output = {
        "total_revenue": 62000.0,
        "best_quarter": "Q3"
    }
    
    result = agent_csv_analysis(test_data)
    
    assert result.result.total_revenue == expected_output["total_revenue"]
    assert result.result.best_quarter == expected_output["best_quarter"]

def test_agent_sentiment_analysis():
    test_news = [
        "Company X stock surges 10%",
        "Market downturn affects finance sector",
        "New product launch boosts revenue"
    ]
    expected_output = {
        "positive": 2,
        "negative": 1,
        "neutral": 0
    }
    
    result = agent_sentiment_analysis(test_news)
    
    assert result.result.positive == expected_output["positive"]
    assert result.result.negative == expected_output["negative"]
    assert result.result.neutral == expected_output["neutral"]

def test_agent_csv_analysis_invalid_data():
    invalid_data = {
        "quarter": ["Q1", "Q2", "Q3", "Q4"],
        "revenue": ["invalid", "data", "here"]
    }
    
    with pytest.raises(ValidationError):
        agent_csv_analysis(invalid_data)

def test_agent_sentiment_analysis_empty_news():
    empty_news = []
    expected_output = {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    }
    
    result = agent_sentiment_analysis(empty_news)
    
    assert result.result.positive == expected_output["positive"]
    assert result.result.negative == expected_output["negative"]
    assert result.result.neutral == expected_output["neutral"]