"""
Basic Streamlit interface for the ML/DS Interview Prep RAG Chatbot.

Calls rag.pipeline.run_pipeline() directly -- no need to run the FastAPI
server separately for local testing/demo purposes.

Run:
    streamlit run streamlit_app.py
"""

import streamlit as st
import threading
import pandas as pd
import glob
import os
from sqlalchemy import select

from sentinel.collector.instrument import instrument_sut
instrument_sut()  # must run before run_pipeline is ever called

from rag.pipeline import run_pipeline
from sentinel.dashboard import render_dashboard
from sentinel.metrics.dashboard_view import render_metrics
from sentinel.trace.db import get_session, init_db
from sentinel.evaluation.models import Evaluation
from sentinel.trace.models import Trace
from sentinel.evaluation.evaluators import EvaluationEngine
from sentinel.evaluation.retrieval_evaluator import evaluate_retrieval
from sentinel.evaluation.calibration import run_calibration

def run_evaluations_async(trace_id: str, query: str, context: str, answer: str):
    try:
        engine = EvaluationEngine()
        engine.evaluate(trace_id, query, context, answer)
    except Exception:
        pass

def load_all_evaluations():
    init_db()
    session = get_session()
    try:
        stmt = (
            select(Evaluation, Trace.started_at)
            .join(Trace, Evaluation.trace_id == Trace.trace_id)
            .order_by(Trace.started_at.desc())
        )
        results = session.execute(stmt).all()
        return [{
            "trace_id": r[0].trace_id,
            "started_at": r[1].strftime("%Y-%m-%d %H:%M:%S") if r[1] else "",
            "evaluator": r[0].evaluator_name,
            "score": f"{r[0].score:.2f}" if r[0].score is not None else "N/A",
            "reasoning": r[0].reasoning,
            "skipped": "Yes" if r[0].skipped else "No"
        } for r in results]
    except Exception:
        return []
    finally:
        session.close()

st.set_page_config(page_title="ML/DS Interview Prep RAG", page_icon="🧠")

st.title("🧠 ML/DS Interview Prep Chatbot")
st.caption("System Under Test for Sentinel AI — ask a question from the knowledge base.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    k = st.slider("Chunks to retrieve (k)", min_value=1, max_value=10, value=5)
    st.divider()
    st.caption("Knowledge base topics:")
    
    # Dynamically list all markdown documents from data/docs/
    md_files = sorted(glob.glob("data/docs/*.md"))
    for filepath in md_files:
        topic_name = os.path.basename(filepath).replace(".md", "").replace("_", " ").title()
        st.caption(f"- {topic_name}")
        
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

tab_chat, tab_dashboard, tab_metrics, tab_evaluations = st.tabs([
    "💬 Chat", "📊 Sentinel Dashboard", "📈 Metrics", "🧪 Evaluations"
])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Retrieval details"):
                    st.write("**Sources used:**", ", ".join(msg["sources"]) or "none")
                    st.write("**Chunks retrieved:**", msg.get("num_chunks_retrieved"))
                    st.write("**Chunks used:**", msg.get("num_chunks_used"))
                    if msg.get("is_fallback"):
                        st.warning("No GEMINI_API_KEY set — this is a fallback response, not a real answer.")

    query = st.chat_input("Ask about bias-variance, regularization, MLOps, features...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Running the RAG pipeline..."):
                try:
                    result = run_pipeline(query, k=k)
                    answer = result["answer"]
                    st.markdown(answer)

                    with st.expander("Retrieval details"):
                        st.write("**Sources used:**", ", ".join(result["sources"]) or "none")
                        st.write("**Chunks retrieved:**", result["num_chunks_retrieved"])
                        st.write("**Chunks used:**", result["num_chunks_used"])
                        st.write("**Trace ID:**", f"`{result['trace_id']}`")
                        if result["is_fallback"]:
                            st.warning("No GEMINI_API_KEY set — this is a fallback response, not a real answer.")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": result["sources"],
                        "num_chunks_retrieved": result["num_chunks_retrieved"],
                        "num_chunks_used": result["num_chunks_used"],
                        "is_fallback": result["is_fallback"],
                        "trace_id": result["trace_id"],
                    })

                    # Run evaluations in a background thread to prevent adding latency
                    threading.Thread(
                        target=run_evaluations_async,
                        args=(result["trace_id"], query, result["context"], answer),
                        daemon=True
                    ).start()

                except ValueError as e:
                    st.error(f"Invalid query: {e}")
                except RuntimeError as e:
                    st.error(f"Pipeline error: {e}")

with tab_dashboard:
    render_dashboard()

with tab_metrics:
    render_metrics()

with tab_evaluations:
    st.subheader("🧪 Sentinel AI — Quality Evaluations")
    st.caption("Live trace evaluations are computed asynchronously in the background. "
               "Offline evaluations assess overall retrieval hit-rate and calibrate the scoring system.")
    
    eval_sub1, eval_sub2, eval_sub3 = st.tabs([
        "🎯 Offline Retrieval (Golden Set)", 
        "⚖️ Judge Calibration", 
        "📜 Live Trace History"
    ])
    
    with eval_sub1:
        st.markdown("### Golden Set Retrieval Performance")
        st.caption("Runs the retrieval pipeline against hand-curated questions to verify if expected source documents make it to top-k.")
        
        k_eval = st.slider("Select k (top chunks retrieved)", min_value=1, max_value=6, value=3, key="golden_set_k_slider")
        
        if st.button("▶ Run Retrieval Evaluation", key="btn_run_ret_eval"):
            with st.spinner("Evaluating retrieval quality..."):
                ret_eval = evaluate_retrieval(k=k_eval)
                st.metric(label=f"Hit-Rate@{k_eval}", value=f"{ret_eval['hit_rate_at_k'] * 100:.1f}%")
                
                detail_rows = []
                for r in ret_eval["results"]:
                    detail_rows.append({
                        "Query": r["query"],
                        "Expected Source": r["expected_source"],
                        "Retrieved Sources": ", ".join(r["retrieved_sources"]),
                        "Hit": "✅ Hit" if r["hit"] else "❌ Miss"
                    })
                st.dataframe(detail_rows, use_container_width=True, hide_index=True)
                
    with eval_sub2:
        st.markdown("### Heuristic Judge Calibration")
        st.caption("Checks if heuristic evaluators can successfully distinguish between known good and bad response pairs.")
        
        if st.button("▶ Run Calibration Check", key="btn_run_calibration"):
            with st.spinner("Running calibration..."):
                calib = run_calibration()
                
                col_c1, col_c2 = st.columns(2)
                col_c1.metric("Avg Good Faithfulness", f"{calib['avg_good_faithfulness']:.2f}")
                col_c2.metric("Avg Bad Faithfulness", f"{calib['avg_bad_faithfulness']:.2f}")
                
                col_c3, col_c4 = st.columns(2)
                col_c3.metric("Avg Good Relevance", f"{calib['avg_good_relevance']:.2f}")
                col_c4.metric("Avg Bad Relevance", f"{calib['avg_bad_relevance']:.2f}")
                
                st.write(f"Faithfulness separates good/bad: **{'Yes ✅' if calib['faithfulness_separates_good_bad'] else 'No ❌'}**")
                st.write(f"Relevance separates good/bad: **{'Yes ✅' if calib['relevance_separates_good_bad'] else 'No ❌'}**")
                
                calib_rows = []
                for r in calib["rows"]:
                    calib_rows.append({
                        "Label": r["label"].upper(),
                        "Faithfulness": f"{r['heuristic_faithfulness']:.2f}",
                        "Relevance": f"{r['heuristic_relevance']:.2f}",
                        "Query": r["query"]
                    })
                st.dataframe(calib_rows, use_container_width=True, hide_index=True)
                
    with eval_sub3:
        st.markdown("### Live Trace Evaluation History")
        st.caption("Shows scores generated by both heuristic and LLM-as-a-Judge evaluators for user chat sessions.")
        
        if st.button("🔄 Refresh Evaluations", key="btn_refresh_evals"):
            st.rerun()
            
        evals = load_all_evaluations()
        if not evals:
            st.info("No live trace evaluations stored yet. Go to the Chat tab and ask a question!")
        else:
            df_evals = pd.DataFrame(evals)
            df_evals["trace_id_short"] = df_evals["trace_id"].str[:8] + "..."
            st.dataframe(
                df_evals[["started_at", "trace_id_short", "evaluator", "score", "reasoning", "skipped"]],
                use_container_width=True,
                hide_index=True
            )
