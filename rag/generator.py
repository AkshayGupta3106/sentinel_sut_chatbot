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
import time
import requests
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def _is_groq() -> bool:
    if GROQ_API_KEY:
        return True
    if GEMINI_API_KEY and GEMINI_API_KEY.startswith("gsk_"):
        return True
    return False


def _get_groq_key() -> str:
    if GROQ_API_KEY:
        return GROQ_API_KEY
    if GEMINI_API_KEY and GEMINI_API_KEY.startswith("gsk_"):
        return GEMINI_API_KEY
    return ""


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def generate_answer(prompt: str) -> str:
    """
    Generate an answer from the LLM given the final prompt.
    Automatically routes to Groq if a Groq key (gsk_...) is detected,
    otherwise uses Gemini.

    Returns a fallback string (no exception) if no API key is configured,
    so the pipeline remains runnable end-to-end without live credentials.
    """
    use_groq = _is_groq()
    api_key = _get_groq_key() if use_groq else GEMINI_API_KEY

    if not api_key:
        return (
            "[FALLBACK: NO API KEY SET] "
            "Set GEMINI_API_KEY or GROQ_API_KEY in your .env to get real answers. "
            "Pipeline structure is working correctly up to this point."
        )

    max_retries = 5
    backoff_factor = 2.0
    initial_delay = 1.0

    for attempt in range(max_retries):
        try:
            if use_groq:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": GROQ_MODEL_NAME,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            else:
                client = _get_client()
                response = client.models.generate_content(
                    model=GEMINI_MODEL_NAME,
                    contents=prompt,
                )
                return response.text
        except Exception as e:
            is_rate_limit = False
            # Check for HTTPError 429
            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                if e.response.status_code == 429:
                    is_rate_limit = True
            elif "429" in str(e) or "ResourceExhausted" in str(e) or "Quota exceeded" in str(e):
                is_rate_limit = True

            if is_rate_limit and attempt < max_retries - 1:
                delay = initial_delay * (backoff_factor ** attempt)
                if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            pass
                time.sleep(delay)
                continue

            # Re-raise as typed error for the pipeline to catch
            if use_groq:
                raise RuntimeError(f"Groq generation failed: {e}") from e
            else:
                raise RuntimeError(f"Gemini generation failed: {e}") from e


