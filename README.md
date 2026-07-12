# ML/DS Interview Prep RAG Chatbot (SUT)

This is the **System Under Test** for Sentinel AI. It's a real, working
RAG chatbot answering questions from an ML/DS interview-prep knowledge
base — deliberately built with 8 distinct, individually-callable stages
so that Sentinel AI's Event Collector can wrap each one independently.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your Gemini API key in
python data/ingest.py         # builds the ChromaDB knowledge base
uvicorn main:app --reload     # starts the API on http://localhost:8000
```

Works even **without** a Gemini API key — the generation stage returns
a clearly tagged `[FALLBACK: NO GEMINI_API_KEY SET]` response so you can
verify the retrieval pipeline end-to-end before wiring up billing.

## Try it

**Option A — Streamlit chat UI (fastest way to try it):**

```bash
streamlit run streamlit_app.py
```

Opens a chat interface with an expandable "Retrieval details" panel per
answer (sources used, chunks retrieved vs used, fallback warning) —
a small preview of the kind of per-query visibility Sentinel AI will
formalize later.

**Option B — raw API:**

```bash
uvicorn main:app --reload
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the bias-variance tradeoff?"}'
```

## Pipeline stages (maps directly to Section 1's recon table)

| # | Stage | File | Function |
|---|---|---|---|
| 1 | Query Validation | `rag/query_validator.py` | `validate_query()` |
| 2 | Embedding Generation | `rag/embeddings.py` | `embed_query()` |
| 3 | ChromaDB Retrieval | `rag/retriever.py` | `Retriever.retrieve_documents()` |
| 4 | Top-k Ranking | `rag/ranker.py` | `rank_top_k()` |
| 5 | Context Builder | `rag/context_builder.py` | `build_context()` |
| 6 | Prompt Builder | `rag/prompt_builder.py` | `build_prompt()` |
| 7 | Gemini Generation | `rag/generator.py` | `generate_answer()` |
| 8 | Response Parser | `rag/response_parser.py` | `parse_response()` |

All 8 are chained in `rag/pipeline.py::run_pipeline()` — that single
function is the exact seam Sentinel AI's Event Collector will wrap in
Section 3.

## Knowledge base

`data/docs/*.md` currently holds 5 placeholder topics: bias-variance
tradeoff, gradient descent variants, classification metrics, L1/L2
regularization, and transformer self-attention. Swap these for your
real 100-question interview tool content or numpy-from-scratch notes
— `data/ingest.py` doesn't care what's in the markdown, it just chunks
and embeds whatever it finds.

## Known failure modes (seeded on purpose — useful for Sentinel AI later)

- Empty/oversized query → `ValueError` from `validate_query()` → HTTP 400
- Missing/unbuilt ChromaDB collection → `RuntimeError` from `Retriever.__init__`
- No `GEMINI_API_KEY` → soft fallback string (not a crash) from `generate_answer()`
- Gemini API failure (rate limit, timeout) → `RuntimeError` → HTTP 502

These four failure modes map directly to the "Failure Modes" column
in Section 1 of the Sentinel AI master plan — don't fix or hide them,
they're the test cases your observability platform needs to catch.

## Sentinel AI — Event Collector (live now)

The `sentinel/` package instruments every one of the 8 stages above via
**runtime monkey-patching** — not a single line inside `rag/` was
touched. `instrument_sut()` patches `rag.pipeline`'s function
references from the outside, the same technique real APM agents
(Datadog `ddtrace`, Elastic APM, OpenTelemetry auto-instrumentation)
use to attach to code they don't own.

Every query now:
- Gets a unique `trace_id`, threaded through all 8 stages via `contextvars`
- Emits a `StageEvent` per stage (latency, status, input/output summary, errors) to an async, non-blocking queue
- Gets those events flushed to `sentinel_events.jsonl` by a background writer thread — tracing never adds latency to the response path

Prove it to yourself:

```bash
python -m sentinel.demo_trace
```

This runs 3 test queries (2 normal, 1 deliberately empty) and prints
the full stage-by-stage trace for each — including the empty-query
case, which correctly shows only 1 stage firing (`query_validation`,
`status=error`) because the real pipeline short-circuits there. That's
not scripted; it's the actual instrumented pipeline behaving correctly.

Both `main.py` and `streamlit_app.py` call `instrument_sut()` on
startup, so tracing is live in both the API and the chat UI — check
the `trace_id` in any `/chat` response, or the "Retrieval details"
expander in Streamlit.

## What's next (Section 4+)

`sentinel_events.jsonl` is now a real, if simple, event log. Section 4
(Trace Collector) assembles these into full waterfall traces; Section
5+ builds metrics, regression detection, and root cause analysis on
top of the same event stream.
