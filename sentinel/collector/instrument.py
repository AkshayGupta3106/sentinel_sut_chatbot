"""
Non-invasive instrumentation.

This is the only file in the whole platform that "reaches into" the
SUT -- and it does so from the outside, at runtime, without editing a
single line inside rag/. Call instrument_sut() once at startup (before
the first query runs) and every one of the 8 pipeline stages starts
emitting StageEvents automatically.

Why monkey-patching instead of adding @trace_stage decorators directly
inside rag/pipeline.py? Two reasons:

  1. It proves the separation of concerns is real. If Sentinel AI were
     deleted, rag/ would still work, unmodified, because rag/ never
     depended on it in the first place.
  2. It's exactly how production APM tooling works. Datadog's ddtrace,
     Elastic APM, and OpenTelemetry's auto-instrumentation libraries
     all attach to frameworks (Flask, requests, psycopg2...) this same
     way -- patching well-known function references at import time,
     without the target library ever knowing observability exists.
"""

from functools import wraps

from rag import pipeline as rag_pipeline
from rag.retriever import Retriever

from .event_collector import trace_stage
from ..context import trace_id_var, query_id_var, new_trace_id, new_query_id

_already_instrumented = False


def instrument_sut() -> None:
    """
    Patch every stage of rag.pipeline.run_pipeline to emit trace events.
    Idempotent -- safe to call more than once (e.g. from both main.py
    and streamlit_app.py in the same process).
    """
    global _already_instrumented
    if _already_instrumented:
        return

    # Stages 1, 2, 4, 5, 6, 8 -- plain functions imported into rag.pipeline's
    # own namespace via `from .x import y`. We patch the name as it exists
    # in rag_pipeline's namespace, since that's what run_pipeline() actually
    # calls.
    rag_pipeline.validate_query = trace_stage("query_validation")(rag_pipeline.validate_query)
    rag_pipeline.embed_query = trace_stage("embedding_generation")(rag_pipeline.embed_query)
    rag_pipeline.rank_top_k = trace_stage("top_k_ranking")(rag_pipeline.rank_top_k)
    rag_pipeline.build_context = trace_stage("context_builder")(rag_pipeline.build_context)
    rag_pipeline.build_prompt = trace_stage("prompt_builder")(rag_pipeline.build_prompt)
    rag_pipeline.generate_answer = trace_stage("generation_gemini")(rag_pipeline.generate_answer)
    rag_pipeline.parse_response = trace_stage("response_parser")(rag_pipeline.parse_response)

    # Stage 3 -- a bound method (Retriever.retrieve_documents). Patch the
    # class itself so every instance (current and future) is traced.
    Retriever.retrieve_documents = trace_stage("chromadb_retrieval")(Retriever.retrieve_documents)

    # Wrap run_pipeline() itself -- this is the ONE place that assigns a
    # fresh trace_id/query_id per incoming query, so all 8 stage events
    # underneath it share the same trace_id.
    original_run_pipeline = rag_pipeline.run_pipeline

    @wraps(original_run_pipeline)
    def traced_run_pipeline(raw_query: str, k: int = 5) -> dict:
        trace_id = new_trace_id()
        query_id = new_query_id()

        trace_token = trace_id_var.set(trace_id)
        query_token = query_id_var.set(query_id)
        try:
            result = original_run_pipeline(raw_query, k=k)
            result["trace_id"] = trace_id
            return result
        finally:
            trace_id_var.reset(trace_token)
            query_id_var.reset(query_token)

    rag_pipeline.run_pipeline = traced_run_pipeline
    _already_instrumented = True
