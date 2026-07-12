"""
Section 6 deliverable.

1. Judge calibration -- do the heuristic evaluators actually separate
   good answers from bad ones?
2. Retrieval evaluation -- hit-rate@k against the golden eval set.
3. Live evaluation -- run a real query through the instrumented
   pipeline, evaluate the actual answer, then re-run to prove caching
   skips already-scored evaluators.

Run:
    python -m sentinel.evaluation.run_eval
"""

from sentinel.collector.instrument import instrument_sut
instrument_sut()

from rag.pipeline import run_pipeline
from .calibration import run_calibration
from .retrieval_evaluator import evaluate_retrieval
from .evaluators import EvaluationEngine


def _section(title: str):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def main():
    _section("1. JUDGE CALIBRATION (heuristic evaluators)")
    calib = run_calibration()
    for r in calib["rows"]:
        print(f"  [{r['label']:>4}] faith={r['heuristic_faithfulness']:.2f}  "
              f"rel={r['heuristic_relevance']:.2f}  {r['query'][:50]}")
    print(f"\n  avg good faithfulness: {calib['avg_good_faithfulness']}   "
          f"avg bad: {calib['avg_bad_faithfulness']}")
    print(f"  avg good relevance:    {calib['avg_good_relevance']}   "
          f"avg bad: {calib['avg_bad_relevance']}")
    print(f"  Faithfulness separates good/bad: {calib['faithfulness_separates_good_bad']}")
    print(f"  Relevance separates good/bad:    {calib['relevance_separates_good_bad']}")

    _section("2. RETRIEVAL EVALUATION (golden set, hit-rate@3)")
    retrieval = evaluate_retrieval(k=3)
    for r in retrieval["results"]:
        marker = "✓" if r["hit"] else "✗"
        print(f"  {marker} {r['query'][:55]:<55} expected={r['expected_source']}")
    print(f"\n  hit_rate@3: {retrieval['hit_rate_at_k']}")

    _section("3. LIVE EVALUATION (real pipeline query, then cached re-run)")
    query = "What is the difference between L1 and L2 regularization?"
    result = run_pipeline(query, k=3)
    trace_id = result["trace_id"]

    engine = EvaluationEngine()
    print(f"  trace_id={trace_id[:8]}...")
    run1 = engine.evaluate(trace_id, query, result["context"], result["answer"])
    for r in run1:
        score_str = f"{r['score']:.2f}" if r["score"] is not None else "N/A"
        print(f"    {r['evaluator_name']:<28} score={score_str}  {r['reasoning'][:55]}")

    print(f"\n  Re-running against the same trace_id (should hit cache)...")
    run2 = engine.evaluate(trace_id, query, result["context"], result["answer"])
    print(f"    New evaluations produced: {len(run2)} (expected: 0)")


if __name__ == "__main__":
    main()
