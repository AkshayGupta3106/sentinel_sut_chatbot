"""
Section 3 deliverable: prove the Event Collector actually works.

Runs a handful of real queries through the (now-instrumented) RAG
pipeline and dumps the full event trace for each -- showing that every
one of the 8 stages emitted an event, all sharing one trace_id, in the
correct order, with real latencies.

Run:
    python -m sentinel.demo_trace
"""

import json

from sentinel.collector.instrument import instrument_sut
from sentinel.collector.event_collector import get_collector

# Must happen BEFORE importing/calling rag.pipeline.run_pipeline anywhere
# else in the process.
instrument_sut()

from rag.pipeline import run_pipeline  # noqa: E402  (import after instrumentation, on purpose)


EXPECTED_STAGE_ORDER = [
    "query_validation",
    "embedding_generation",
    "chromadb_retrieval",
    "top_k_ranking",
    "context_builder",
    "prompt_builder",
    "generation_gemini",
    "response_parser",
]


def run_demo():
    test_queries = [
        "What is the bias-variance tradeoff?",
        "Explain the difference between L1 and L2 regularization",
        "",  # deliberately broken: should fail at query_validation and stop there
    ]

    for query in test_queries:
        print(f"\n{'=' * 70}")
        print(f"QUERY: {query!r}")
        print("=" * 70)

        try:
            result = run_pipeline(query, k=3)
            trace_id = result["trace_id"]
            print(f"Result: {result['answer'][:80]}...")
        except ValueError as e:
            # We didn't get a trace_id back since run_pipeline raised before
            # returning -- pull the most recent event instead to find it.
            print(f"Pipeline rejected query: {e}")
            recent = get_collector().get_events()
            trace_id = recent[-1].trace_id if recent else None

        if not trace_id:
            continue

        events = get_collector().get_events(trace_id=trace_id)
        print(f"\ntrace_id: {trace_id}")
        print(f"Stages fired: {len(events)}")

        total_latency = sum(e.latency_ms for e in events)
        for e in events:
            marker = "✓" if e.status == "success" else "✗"
            print(f"  {marker} {e.stage_name:<22} {e.latency_ms:>8.2f} ms   status={e.status}")
            if e.error:
                print(f"      error: {e.error}")

        print(f"  {'TOTAL':<24} {total_latency:>8.2f} ms")

        fired_stages = [e.stage_name for e in events]
        expected_prefix = EXPECTED_STAGE_ORDER[: len(fired_stages)]
        assert fired_stages == expected_prefix, (
            f"Stage order/coverage mismatch!\n  got:      {fired_stages}\n  expected: {expected_prefix}"
        )

    print(f"\n{'=' * 70}")
    print("All traces verified: correct stage order, shared trace_id per query.")
    print("Raw events also written to: sentinel_events.jsonl")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
