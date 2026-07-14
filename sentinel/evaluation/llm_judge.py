"""
LLM-as-Judge evaluators.

Uses a separate client from rag/generator.py on purpose -- the judge
model evaluating an answer shouldn't be indistinguishable from the
model that wrote it in the code path, even if it happens to be the
same underlying model today. Swapping the judge to a different
provider (Groq) later is a one-file change.

Same fail-soft contract as the rest of this codebase: no API key means
a clearly tagged skipped result, never a crash.
"""

import json
import os

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
JUDGE_MODEL = os.getenv("SENTINEL_JUDGE_MODEL", "gemini-3.5-flash")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


FAITHFULNESS_PROMPT = """You are a strict evaluator judging whether an AI \
answer is fully supported by the given context.

Context:
{context}

Answer:
{answer}

Score the answer's faithfulness to the context from 0.0 (unsupported or \
contradicts the context) to 1.0 (fully supported, no unsupported claims).
Respond ONLY with JSON, no other text: {{"score": <float 0-1>, "reasoning": "<one sentence>"}}"""

RELEVANCE_PROMPT = """You are a strict evaluator judging whether an AI \
answer actually addresses the user's question.

Question: {query}
Answer: {answer}

Score relevance from 0.0 (does not address the question) to 1.0 (fully \
addresses it).
Respond ONLY with JSON, no other text: {{"score": <float 0-1>, "reasoning": "<one sentence>"}}"""


def _run_judge(prompt: str) -> dict:
    if not GEMINI_API_KEY:
        return {
            "score": None,
            "reasoning": "[FALLBACK: NO GEMINI_API_KEY SET] judge skipped",
            "skipped": True,
        }

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=JUDGE_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        parsed = json.loads(response.text)
        return {
            "score": float(parsed["score"]),
            "reasoning": parsed.get("reasoning", ""),
            "skipped": False,
        }
    except Exception as e:
        return {"score": None, "reasoning": f"[JUDGE ERROR] {e}", "skipped": True}


def judge_faithfulness(context: str, answer: str) -> dict:
    # Truncate defensively -- a judge prompt shouldn't silently balloon
    # in cost because one retrieval returned an unusually large context.
    return _run_judge(FAITHFULNESS_PROMPT.format(context=context[:4000], answer=answer))


def judge_relevance(query: str, answer: str) -> dict:
    return _run_judge(RELEVANCE_PROMPT.format(query=query, answer=answer))
