# AI Agents Prototype

This project is a prototype for AI agents that analyze CSV data and news sentiment. The agents utilize a language model to perform their tasks and return structured outputs.

## Project Structure

```
ai-agents-prototype
├── src
│   ├── agents
│   │   ├── csv_agent.py        # Implementation of the CSV analysis agent
│   │   ├── sentiment_agent.py   # Implementation of the news sentiment analysis agent
│   │   └── __init__.py         # Initializes the agents package
│   ├── helpers
│   │   ├── llm_utils.py        # Utility functions for interacting with the LLM
│   │   ├── json_utils.py       # Functions for handling JSON data
│   │   └── __init__.py         # Initializes the helpers package
│   ├── orchestrator.py          # Central logic for coordinating agent calls
│   └── __init__.py             # Initializes the main package
├── tests
│   ├── test_agents.py           # Unit tests for agent modules
│   ├── test_helpers.py          # Unit tests for helper functions
│   └── __init__.py             # Initializes the tests package
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

To run the prototype, execute the orchestrator script:
```
python src/orchestrator.py
```

This will trigger the agents to analyze the provided data and print the results.

## Testing

To run the tests, ensure you are in the virtual environment and execute:
```
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.