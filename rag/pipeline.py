"""
Pipeline Orchestrator

Chains all 8 stages exactly as laid out in the original architecture:

    Query Validation -> Embedding Generation -> ChromaDB Retrieval
    -> Top-k Ranking -> Context Builder -> Prompt Builder -> Gemini
    -> Response Parser -> Final Response

This is the exact function-call chain Sentinel AI's Event Collector
(Sprint/Section 3) will wrap with tracing decorators, stage by stage,
without modifying any of the logic below. Every function name here
matches the function catalog from Section 1's recon table on purpose.
"""

from .query_validator import validate_query
from .embeddings import embed_query
from .retriever import Retriever
from .ranker import rank_top_k
from .context_builder import build_context
from .prompt_builder import build_prompt
from .generator import generate_answer
from .response_parser import parse_response

_retriever = None


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def run_pipeline(raw_query: str, k: int = 5) -> dict:
    """
    Run the full RAG pipeline end to end for a single query.

    Returns a dict with the final answer plus useful debug fields
    (retrieved sources, fallback flag) that Sentinel AI will later
    replace/augment with full stage-by-stage traces.
    """
    query = validate_query(raw_query)

    query_vector = embed_query(query)

    retriever = _get_retriever()
    retrieved_docs = retriever.retrieve_documents(query_vector, k=k * 2)  # overfetch, then rank

    ranked_docs = rank_top_k(retrieved_docs, k=k)

    context = build_context(ranked_docs)

    prompt = build_prompt(query, context)

    raw_answer = generate_answer(prompt)

    result = parse_response(raw_answer)
    result["sources"] = sorted({
        doc["metadata"].get("source", "unknown") for doc in ranked_docs
    })
    result["num_chunks_retrieved"] = len(retrieved_docs)
    result["num_chunks_used"] = len(ranked_docs)

    return result
