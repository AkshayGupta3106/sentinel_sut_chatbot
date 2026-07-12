"""
Heuristic evaluators.

No LLM calls -- free, instant, and always available (no API key
needed). Deliberately crude: word-overlap is a proxy, not real
semantic judgment, and it will miss subtle contradictions or reward a
answer that copies context words without actually answering the
question. It exists to catch the *obvious* failures cheaply, and to
give the LLM judges (llm_judge.py) something to be compared against
during calibration.
"""

import re

_STOPWORDS = {
    "the", "is", "a", "an", "of", "to", "and", "in", "on", "for", "that",
    "this", "it", "as", "are", "was", "were", "be", "by", "with", "at",
    "from", "or", "not", "but", "can", "will", "which", "into", "than",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def context_overlap_score(answer: str, context: str) -> float:
    """
    Proxy for faithfulness: fraction of the answer's content words that
    also appear somewhere in the retrieved context. An answer that
    talks about something the context never mentions scores low.
    """
    if not answer or not context:
        return 0.0
    answer_tokens = _tokenize(answer)
    if not answer_tokens:
        return 0.0
    context_tokens = _tokenize(context)
    overlap = answer_tokens & context_tokens
    return round(len(overlap) / len(answer_tokens), 3)


def relevance_keyword_score(query: str, answer: str) -> float:
    """
    Proxy for relevance: fraction of the query's content words that are
    actually addressed (present) in the answer.
    """
    if not query or not answer:
        return 0.0
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0
    answer_tokens = _tokenize(answer)
    overlap = query_tokens & answer_tokens
    return round(len(overlap) / len(query_tokens), 3)


def is_fallback_answer(answer: str) -> bool:
    stripped = answer.strip()
    return stripped.startswith("[FALLBACK") or stripped.startswith(
        "I don't have enough information"
    )
