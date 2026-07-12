"""
Knowledge Base Ingestion

Chunks every markdown file in data/docs/ and loads it into a persistent
ChromaDB collection. Run this once before starting the chatbot, and
again any time you add/change docs.

    python data/ingest.py

Swap the contents of data/docs/ for your real ML interview-prep notes,
the 100-question tool, or the numpy-from-scratch reference -- the
chunking/ingestion logic doesn't need to change.
"""

import os
import sys
import glob
import chromadb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rag.embeddings import embed_query

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
COLLECTION_NAME = "ml_interview_prep"

MIN_CHUNK_CHARS = 200  # merge short paragraphs together up to this size


def chunk_text(text: str, min_len: int = MIN_CHUNK_CHARS) -> list[str]:
    """
    Simple paragraph-based chunking: split on blank lines, then greedily
    merge consecutive paragraphs until each chunk crosses min_len chars.
    Good enough for markdown notes; swap for a token-aware splitter
    (e.g. langchain's RecursiveCharacterTextSplitter) for larger corpora.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buffer = ""

    for para in paragraphs:
        buffer += para + "\n\n"
        if len(buffer) >= min_len:
            chunks.append(buffer.strip())
            buffer = ""

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks


def ingest():
    client = chromadb.PersistentClient(path=PERSIST_DIR)

    # Fresh collection each run to keep ingestion idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    md_files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.md")))
    if not md_files:
        print(f"No markdown files found in {DOCS_DIR}")
        return

    total_chunks = 0
    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)
        if not chunks:
            continue

        ids = [f"{filename}::chunk-{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        embeddings = [embed_query(chunk) for chunk in chunks]

        collection.add(documents=chunks, ids=ids, metadatas=metadatas, embeddings=embeddings)
        total_chunks += len(chunks)
        print(f"  Ingested {len(chunks):>2} chunks from {filename}")

    print(f"\nDone. {total_chunks} total chunks in collection '{COLLECTION_NAME}'.")
    print(f"Persisted to: {os.path.abspath(PERSIST_DIR)}")


if __name__ == "__main__":
    ingest()
