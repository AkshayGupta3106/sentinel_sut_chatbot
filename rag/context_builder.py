"""
Stage 5: Context Builder

Assembles ranked chunks into a single context string for the prompt,
respecting a character budget so we don't blow past Gemini's context
window or pay for tokens we don't need. This is a common silent-failure
point in real RAG systems: if max_chars is too small, high-quality
chunks get silently dropped and nobody notices until answers get worse --
exactly the kind of regression Sentinel AI is built to catch.
"""

DEFAULT_MAX_CHARS = 3000


def build_context(documents: list[dict], max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """
    Concatenate ranked document chunks into one context block, each
    tagged with its source file so hallucination/faithfulness checks
    can later verify claims against a specific source.
    """
    parts = []
    total_chars = 0

    for doc in documents:
        source = doc.get("metadata", {}).get("source", "unknown")
        chunk = f"[Source: {source}]\n{doc['text']}"

        if total_chars + len(chunk) > max_chars:
            break

        parts.append(chunk)
        total_chars += len(chunk)

    return "\n\n---\n\n".join(parts)
