"""
Stage 7: Generation (Gemini)

Calls the Gemini API with the final prompt via the current `google-genai`
SDK (the older `google-generativeai` package is deprecated as of 2025).

Fails soft (returns a clearly tagged fallback string) rather than
crashing when GEMINI_API_KEY is not set, so the rest of the pipeline
stays runnable/demoable without a live key -- and so Sentinel AI has a
real "degraded" status to detect, not just "success" or "hard crash".
"""

import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def generate_answer(prompt: str) -> str:
    """
    Generate an answer from Gemini given the final prompt.

    Returns a fallback string (no exception) if no API key is configured,
    so the pipeline remains runnable end-to-end without live credentials.
    """
    if not GEMINI_API_KEY:
        return (
            "[FALLBACK: NO GEMINI_API_KEY SET] "
            "Set GEMINI_API_KEY in your .env to get real answers. "
            "Pipeline structure is working correctly up to this point."
        )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        # Deliberately re-raise as a typed error the pipeline can catch --
        # Sentinel AI's Event Collector needs to see this as a distinct
        # "generation_error" status, not swallow it silently.
        raise RuntimeError(f"Gemini generation failed: {e}") from e
