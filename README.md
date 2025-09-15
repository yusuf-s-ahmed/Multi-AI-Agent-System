# AI Agents Prototype

## Overview
This project allows you to upload a CSV file, ask a question, and let AI agents process the data to provide insights.

## How to Run
1. Place your CSV file in the `data/` folder.
2. Update the `file_path` and `question` variables in `src/orchestrator.py`.
3. Run the program:
   ```bash
   python src/orchestrator.py
   ```

## Project Structure

```
ai-agents-prototype
├── src
│   ├── agents
│   │   ├── data_analyst_agent.py        # Analyses input data 
│   │   ├── researcher_agent.py              # Conducts research by web scraping
|   |   └── information_retrieval_agent.py   # Fetches data using real-time APIs
|   |   └── planner_agent.py                 # Communicates with research, data analyst, info. retreival agents
│   │   └── __init__.py                      # Initializes the agents package
│   ├── helpers
│   │   ├── llm_utils.py        # Utility functions for interacting with the LLM
│   │   └── __init__.py         # Initializes the helpers package
│   ├── orchestrator.py          # Central logic for coordinating agent calls
│   └── __init__.py             # Initializes the main package
|
├── requirements.txt             # Lists project dependencies
├── README.md                    # Project documentation
└── .gitignore                   # Specifies files to ignore in version control
```

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd ai-agents-prototype
   ```

2. **Install Dependencies**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the prototype, get an API key from SerpAPI, make a .env file then execute the orchestrator script:
```
python src/orchestrator.py
```

This will trigger the agents to analyze the provided data and print the results.

## Next Steps

These are the next steps:
- Add Yahoo Finance API to the information retrieval agent.
- Fix final LLM output from executing orchestrator.py script.
- Make the planner agent's child agents execute in parallel using multithreading.
- Make the final answer refer the the context memory to make a comprehensive report.
- Switch out Llama-3 8B and Gemma-3 4B for GPT-4 for rapid prototyping.
- Expose agents as Flask endpoints, to allow requests using Postman, front-end is not really needed.
- Present the Multi-Agent AI system applied in different domains, finance, e-commerce, etc. 
- Recreate in Runa.

## License

This project is licensed under the MIT License. See the LICENSE file for details.