"""
Stage 8: Response Parser

Normalizes the raw LLM output into a clean, structured final response.
Currently minimal (strip whitespace, basic stats) -- this is the natural
place to later add structured-output parsing (JSON mode), citation
extraction, or safety filtering, all without touching upstream stages.
"""


def parse_response(raw_text: str) -> dict:
    if raw_text is None:
        raise ValueError("Cannot parse a None response")

    cleaned = raw_text.strip()

    return {
        "answer": cleaned,
        "char_length": len(cleaned),
        "is_fallback": cleaned.startswith("[FALLBACK"),
    }
