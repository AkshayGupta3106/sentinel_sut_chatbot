"""
Runs the full hard question bank (data/hard_question_bank.py, 45
deliberately tricky/advanced questions across all 15 KB topics)
through the instrumented pipeline -- AND evaluates every single one.

This is different from ask_question_bank.py on purpose: that script
only traces queries, it never evaluates them (only Streamlit chat and
run_eval.py do). Evaluation coverage was sitting at 3/118 traces before
this script exists -- the whole point here is to fix that, so Power
BI's Quality Trends view actually has real data to show instead of
mostly-empty columns.

Run:
    python ask_hard_questions.py
    python ask_hard_questions.py --limit 10     # quick smoke test
"""

import argparse
import time
from collections import defaultdict

from sentinel.collector.instrument import instrument_sut
instrument_sut()

from rag.pipeline import run_pipeline
from sentinel.evaluation.evaluators import EvaluationEngine
from data.hard_question_bank import HARD_QUESTION_BANK
from data.question_bank import TOPIC_TO_SOURCE_FILE


def run(limit: int | None = None, verbose: bool = True):
    questions = HARD_QUESTION_BANK[:limit] if limit else HARD_QUESTION_BANK
    engine = EvaluationEngine()

    print(f"Running {len(questions)} hard questions through pipeline + evaluation...\n")

    stats = defaultdict(list)
    quality_scores = []
    start = time.time()

    for i, item in enumerate(questions, 1):
        query = item["question"]
        topic = item["topic"]
        expected_source = TOPIC_TO_SOURCE_FILE[topic]

        try:
            result = run_pipeline(query, k=5)  # k=5: harder questions may need more context
            hit = expected_source in result["sources"]

            eval_results = engine.evaluate(
                result["trace_id"], query, result["context"], result["answer"]
            )
            real_scores = {r["evaluator_name"]: r["score"] for r in eval_results if r["score"] is not None}
            quality_scores.append(real_scores)

            stats["hit"].append(hit)
            marker = "✓" if hit else "✗"
            score_preview = ", ".join(f"{k.split('_')[0]}={v:.2f}" for k, v in real_scores.items()) or "no scores (all skipped)"

            if verbose:
                print(f"[{i:>2}/{len(questions)}] {marker} [{topic:<28}] {query[:55]}")
                print(f"          {score_preview}")

        except ValueError as e:
            if verbose:
                print(f"[{i:>2}/{len(questions)}] ⚠ ERROR [{topic:<28}] {query[:55]} -- {e}")

    elapsed = time.time() - start
    total = len(stats["hit"])
    hits = sum(stats["hit"])

    print(f"\n{'=' * 70}")
    print(f"Done in {elapsed:.1f}s")
    print(f"{'=' * 70}")
    print(f"Retrieval hit-rate on hard questions: {hits}/{total} ({hits/total*100:.1f}%)" if total else "No results.")

    scored = [s for s in quality_scores if s]
    if scored:
        all_evaluator_names = {k for s in scored for k in s.keys()}
        print(f"\nEvaluated: {len(scored)}/{total} questions had at least one real (non-skipped) score")
        for name in sorted(all_evaluator_names):
            vals = [s[name] for s in scored if name in s]
            if vals:
                print(f"  {name:<28} avg={sum(vals)/len(vals):.3f}  (n={len(vals)})")
    else:
        print("\nNo evaluator scores were produced (all skipped -- check GEMINI_API_KEY "
              "for LLM judges; heuristics should never skip).")

    print(f"\nRun `python -m sentinel.trace.sync` then `python -m sentinel.export.powerbi_export`")
    print(f"to get this new data into your Power BI export.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N questions")
    args = parser.parse_args()

    run(limit=args.limit)
