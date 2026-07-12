"""
Evaluation Engine.

Runs every registered evaluator against one (query, context, answer)
tuple and persists the results, keyed by (trace_id, evaluator_name) so
re-running against the same trace never re-scores work already done --
important once LLM judges are in the mix, since every re-score is a
real API call and a real cost.
"""

from sqlalchemy import select

from ..trace.db import get_session, init_db
from .models import Evaluation
from . import heuristics
from . import llm_judge


class EvaluationEngine:
    def evaluate(self, trace_id: str, query: str, context: str, answer: str, force: bool = False) -> list[dict]:
        init_db()
        session = get_session()
        try:
            already_done = set()
            if not force:
                rows = session.execute(
                    select(Evaluation.evaluator_name).where(Evaluation.trace_id == trace_id)
                ).scalars().all()
                already_done = set(rows)

            candidates = {}
            if "heuristic_faithfulness_overlap" not in already_done:
                candidates["heuristic_faithfulness_overlap"] = {
                    "score": heuristics.context_overlap_score(answer, context),
                    "reasoning": "Fraction of the answer's content words also present in retrieved context.",
                    "skipped": False,
                }
            if "heuristic_relevance_keyword" not in already_done:
                candidates["heuristic_relevance_keyword"] = {
                    "score": heuristics.relevance_keyword_score(query, answer),
                    "reasoning": "Fraction of the query's content words addressed in the answer.",
                    "skipped": False,
                }
            if "llm_judge_faithfulness" not in already_done:
                candidates["llm_judge_faithfulness"] = llm_judge.judge_faithfulness(context, answer)
            if "llm_judge_relevance" not in already_done:
                candidates["llm_judge_relevance"] = llm_judge.judge_relevance(query, answer)

            results = []
            for name, r in candidates.items():
                session.add(Evaluation(
                    trace_id=trace_id,
                    evaluator_name=name,
                    score=r["score"],
                    reasoning=r["reasoning"],
                    skipped=r.get("skipped", False),
                ))
                results.append({"evaluator_name": name, **r})

            session.commit()
            return results
        finally:
            session.close()

    def get_evaluations(self, trace_id: str) -> list[Evaluation]:
        session = get_session()
        try:
            return session.execute(
                select(Evaluation).where(Evaluation.trace_id == trace_id)
            ).scalars().all()
        finally:
            session.close()
