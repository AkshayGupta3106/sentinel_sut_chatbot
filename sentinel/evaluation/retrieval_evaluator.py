"""
Retrieval Evaluator.

Runs the real retrieval stages directly (embed_query, Retriever,
rank_top_k) against the golden set and checks whether the expected
source document actually made it into the top-k. No LLM call, no API
key needed -- this is a pure retrieval-quality check, decoupled from
generation entirely.
"""

from rag.embeddings import embed_query
from rag.retriever import Retriever
from rag.ranker import rank_top_k

from .golden_set import GOLDEN_EVAL_SET


def evaluate_retrieval(k: int = 3) -> dict:
    retriever = Retriever()
    results = []

    for item in GOLDEN_EVAL_SET:
        query_vector = embed_query(item["query"])
        retrieved = retriever.retrieve_documents(query_vector, k=k * 2)
        ranked = rank_top_k(retrieved, k=k)
        retrieved_sources = sorted({doc["metadata"].get("source") for doc in ranked})

        hit = item["expected_source"] in retrieved_sources
        results.append({
            "query": item["query"],
            "expected_source": item["expected_source"],
            "retrieved_sources": retrieved_sources,
            "hit": hit,
        })

    hit_rate = sum(r["hit"] for r in results) / len(results)
    return {"hit_rate_at_k": round(hit_rate, 3), "k": k, "results": results}
