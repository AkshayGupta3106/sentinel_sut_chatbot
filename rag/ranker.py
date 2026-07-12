"""
Stage 4: Top-k Ranking

Chroma already returns results sorted by distance, but real production
pipelines almost always add a ranking pass on top of raw vector search:
deduplication, diversity, or a cross-encoder re-rank. This module keeps
that seam explicit so Sentinel AI has a distinct stage to evaluate
("did ranking help or hurt retrieval quality?") instead of collapsing
retrieval and ranking into one opaque step.
"""


def rank_top_k(documents: list[dict], k: int = 5) -> list[dict]:
    """
    Re-rank and truncate retrieved documents to the top k.

    Current strategy: sort by distance (ascending = more similar) and
    drop exact-duplicate chunks. Replace with a cross-encoder re-ranker
    later without touching any other stage.
    """
    seen_text = set()
    ranked = []

    for doc in sorted(documents, key=lambda d: d["distance"]):
        if doc["text"] in seen_text:
            continue
        seen_text.add(doc["text"])
        ranked.append(doc)
        if len(ranked) >= k:
            break

    return ranked
