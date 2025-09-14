def clean_llm_json(raw_text: str) -> str:
    """
    Remove Markdown code fences or other extra text so it's pure JSON.
    """
    cleaned = re.sub(r"```(?:json)?\n([\s\S]*?)```", r"\1", raw_text, flags=re.MULTILINE)
    return cleaned.strip()

def ask_llama(prompt: str, model: str = "gemma3:4b") -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]