"""
Judge Calibration.

If an evaluator can't tell a good answer from a deliberately bad one,
it isn't trustworthy enough to drive Section 7's regression detection
later -- this is that sanity check, run against 3 known-good and 3
known-bad (context, query, answer) triples.
"""

from . import heuristics

# (context, query, answer, label)
CALIBRATION_SET = [
    (
        "L1 regularization adds the sum of absolute weights to the loss and "
        "tends to push many weights to exactly zero, performing automatic "
        "feature selection.",
        "What does L1 regularization do?",
        "L1 regularization adds a penalty based on the absolute value of "
        "weights, which tends to push many weights to exactly zero, "
        "effectively selecting features.",
        "good",
    ),
    (
        "F1 Score is the harmonic mean of precision and recall.",
        "What is the F1 score?",
        "The F1 score is the harmonic mean of precision and recall, used "
        "for imbalanced classification.",
        "good",
    ),
    (
        "Self-attention lets each token attend to every other token via "
        "Query, Key, Value projections.",
        "How does self-attention work?",
        "Self-attention computes Query, Key, and Value vectors and uses "
        "their dot products to weight how much each token attends to "
        "every other token.",
        "good",
    ),
    (
        "L1 regularization adds the sum of absolute weights to the loss "
        "and tends to push many weights to exactly zero.",
        "What does L1 regularization do?",
        "Bananas are a good source of potassium and are yellow when ripe.",
        "bad",
    ),
    (
        "F1 Score is the harmonic mean of precision and recall.",
        "What is the F1 score?",
        "The F1 score is calculated by dividing total revenue by total "
        "cost across all fiscal quarters.",
        "bad",
    ),
    (
        "Self-attention lets each token attend to every other token via "
        "Query, Key, Value projections.",
        "How does self-attention work?",
        "Self-attention was invented in 1995 by a team studying "
        "convolutional neural networks for image classification.",
        "bad",
    ),
]


def run_calibration() -> dict:
    rows = []
    for context, query, answer, label in CALIBRATION_SET:
        rows.append({
            "label": label,
            "query": query,
            "heuristic_faithfulness": heuristics.context_overlap_score(answer, context),
            "heuristic_relevance": heuristics.relevance_keyword_score(query, answer),
        })

    good = [r for r in rows if r["label"] == "good"]
    bad = [r for r in rows if r["label"] == "bad"]

    avg_good_faith = sum(r["heuristic_faithfulness"] for r in good) / len(good)
    avg_bad_faith = sum(r["heuristic_faithfulness"] for r in bad) / len(bad)
    avg_good_rel = sum(r["heuristic_relevance"] for r in good) / len(good)
    avg_bad_rel = sum(r["heuristic_relevance"] for r in bad) / len(bad)

    return {
        "rows": rows,
        "avg_good_faithfulness": round(avg_good_faith, 3),
        "avg_bad_faithfulness": round(avg_bad_faith, 3),
        "avg_good_relevance": round(avg_good_rel, 3),
        "avg_bad_relevance": round(avg_bad_rel, 3),
        "faithfulness_separates_good_bad": avg_good_faith > avg_bad_faith,
        "relevance_separates_good_bad": avg_good_rel > avg_bad_rel,
    }
