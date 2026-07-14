"""
Evaluation tab for the Streamlit dashboard.

Three sections:
  1. Judge calibration -- do the heuristic evaluators separate good
     answers from bad ones? (static, always runnable, no API key needed)
  2. Retrieval evaluation -- hit-rate@k against the golden eval set
     (static, always runnable, no API key needed)
  3. Live evaluations -- results for every trace that's actually been
     evaluated so far (populated by asking questions in the Chat tab,
     which runs evaluation synchronously right after each answer).
"""

import pandas as pd
import streamlit as st
from sqlalchemy import select

from ..trace.db import get_session, init_db
from .models import Evaluation
from .calibration import run_calibration
from .retrieval_evaluator import evaluate_retrieval


def render_evaluation():
    st.subheader("🧪 Sentinel AI — Evaluation Engine")

    st.markdown("### 1. Judge calibration (heuristic evaluators)")
    st.caption("Do the evaluators actually separate good answers from bad ones? No API key needed.")
    calib = run_calibration()
    calib_df = pd.DataFrame(calib["rows"])
    st.dataframe(calib_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    c1.metric("Avg faithfulness — good vs bad",
               f"{calib['avg_good_faithfulness']} vs {calib['avg_bad_faithfulness']}",
               delta="separates ✓" if calib["faithfulness_separates_good_bad"] else "NOT separating ✗")
    c2.metric("Avg relevance — good vs bad",
               f"{calib['avg_good_relevance']} vs {calib['avg_bad_relevance']}",
               delta="separates ✓" if calib["relevance_separates_good_bad"] else "NOT separating ✗")

    st.divider()

    st.markdown("### 2. Retrieval evaluation (golden set)")
    st.caption("Hit-rate@k: does the expected source doc actually make it into the top-k retrieved chunks?")
    k = st.slider("k", min_value=1, max_value=10, value=3, key="eval_k_slider")
    retrieval = evaluate_retrieval(k=k)
    st.metric(f"Hit-rate@{k}", f"{retrieval['hit_rate_at_k'] * 100:.1f}%")
    retrieval_df = pd.DataFrame(retrieval["results"])
    st.dataframe(retrieval_df, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 3. Live evaluations (from Chat tab)")
    st.caption("Populated automatically each time you ask a question in the Chat tab.")

    init_db()
    session = get_session()
    try:
        rows = session.execute(select(Evaluation).order_by(Evaluation.created_at.desc())).scalars().all()
        eval_df = pd.DataFrame([{
            "trace_id": r.trace_id[:8] + "...",
            "evaluator": r.evaluator_name,
            "score": r.score,
            "reasoning": r.reasoning,
            "skipped": r.skipped,
            "created_at": r.created_at,
        } for r in rows])
    finally:
        session.close()

    if eval_df.empty:
        st.info("No live evaluations yet — ask a question in the Chat tab first.")
        return

    st.dataframe(eval_df, use_container_width=True, hide_index=True)

    st.markdown("**Avg score by evaluator**")
    avg_by_evaluator = eval_df[~eval_df["skipped"]].groupby("evaluator")["score"].mean().reset_index()
    if not avg_by_evaluator.empty:
        st.bar_chart(avg_by_evaluator.set_index("evaluator"))
    else:
        st.caption("All evaluators skipped so far (no GEMINI_API_KEY set — LLM judges only).")
