import re

def clean_llm_json_old(raw_text: str) -> str:
    """
    Remove Markdown code fences or other extra text so it's pure JSON.
    """
    cleaned = re.sub(r"```(?:json)?\n([\s\S]*?)```", r"\1", raw_text, flags=re.MULTILINE)
    return cleaned.strip()


def clean_llm_json(raw_output: str) -> str:
    """
    Extracts the first valid JSON object or array from LLM output,
    even if extra text surrounds it.
    """
    # Remove code block markers
    raw_output = raw_output.strip().strip("`")
    raw_output = raw_output.replace("json\n", "").replace("json", "").strip()

    # Regex: find first {...} or [...]
    match = re.search(r'(\{.*\}|\[.*\])', raw_output, re.DOTALL)
    if match:
        return match.group(1)
    return raw_output