"""
FastAPI entrypoint for the ML/DS Interview Prep RAG Chatbot.

This is the System Under Test (SUT) for Sentinel AI. Nothing in this
file (or rag/) should ever import anything from a future `sentinel/`
package -- observability wraps the SUT from the outside, it never lives
inside it. That separation is the whole point of the project.

Run:
    python data/ingest.py        # one-time: build the knowledge base
    uvicorn main:app --reload    # start the API

Then:
    curl -X POST http://localhost:8000/chat \\
         -H "Content-Type: application/json" \\
         -d '{"query": "What is the bias-variance tradeoff?"}'
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sentinel.collector.instrument import instrument_sut
instrument_sut()  # must run before run_pipeline is ever called

from rag.pipeline import run_pipeline

app = FastAPI(
    title="ML/DS Interview Prep RAG Chatbot",
    description="System Under Test for the Sentinel AI observability platform.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question")
    k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    num_chunks_retrieved: int
    num_chunks_used: int
    is_fallback: bool
    trace_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = run_pipeline(req.query, k=req.k)
    except ValueError as e:
        # Query validation failures -> 400
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Retriever/generation failures -> 502 (upstream dependency failed)
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        num_chunks_retrieved=result["num_chunks_retrieved"],
        num_chunks_used=result["num_chunks_used"],
        is_fallback=result["is_fallback"],
        trace_id=result["trace_id"],
    )
