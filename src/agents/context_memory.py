# context_memory.py

import json

# In-memory store, resets each run
_context_history = []

def save_context(question: str, tool_outputs: dict):
    """
    Append the latest run (question + tool outputs) into the in-memory context.
    """
    _context_history.append({
        "question": question,
        "tool_outputs": tool_outputs
    })

def get_context_text() -> str:
    """
    Return past context as a readable string for prompts.
    """
    if not _context_history:
        return "No previous context."
    
    text = "Previous interactions:\n"
    for i, h in enumerate(_context_history, 1):
        text += f"{i}. Q: {h['question']}\n   A: {json.dumps(h['tool_outputs'], indent=2)}\n"
    return text
