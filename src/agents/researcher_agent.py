import ollama
import json
from pydantic import BaseModel
from helpers.llm_utils import clean_llm_json
from typing import Any
from serpapi.google_search import GoogleSearch
import requests
from bs4 import BeautifulSoup

class DirectAnswer(BaseModel):
    answer: Any
    reasoning: str
    confidence: float

SERPAPI_KEY = "dde12eee74584a5d1241998b29e6208199f8458a5d0fd7e7b0ee668baeb3ba6d"

def scrape_page(url: str) -> dict:
    """Scrape the main text from a web page using requests + BeautifulSoup"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)

        return {"url": url, "text": text[:2000]}  # limit for safety
    except Exception as e:
        return {"url": url, "error": str(e)}

def web_scrape(query: str) -> DirectAnswer:
    """Fetch top 3 Google results and scrape their content"""
    # --- Step 1: Fetch top 3 results from SerpAPI ---
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])[:3]

    if not organic_results:
        return DirectAnswer(
            answer=[],
            reasoning=f"No results found for '{query}'",
            confidence=0.0
        )

    # --- Step 2: Scrape each page ---
    scraped_results = []
    for res in organic_results:
        url = res.get("link")
        page_data = scrape_page(url)
        scraped_results.append({
            "title": res.get("title"),
            "url": url,
            "snippet": res.get("snippet"),
            "content": page_data.get("text", ""),
            "error": page_data.get("error")
        })

    reasoning = f"Fetched and scraped top {len(scraped_results)} Google search results for '{query}'."
    confidence = 0.9  # placeholder confidence

    return DirectAnswer(
        answer=scraped_results,
        reasoning=reasoning,
        confidence=confidence
    )

# Example usage
if __name__ == "__main__":
    result = web_scrape("Coffee")
    print(result.json(indent=2))
