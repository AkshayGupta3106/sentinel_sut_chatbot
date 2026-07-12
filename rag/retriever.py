"""
Stage 3: ChromaDB Retrieval

Wraps a persistent Chroma collection and performs vector similarity
search against the pre-ingested ML/DS interview-prep knowledge base
(see data/ingest.py).
"""

import os
import chromadb

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
COLLECTION_NAME = "ml_interview_prep"


class Retriever:
    def __init__(self, persist_dir: str = PERSIST_DIR, collection_name: str = COLLECTION_NAME):
        self.client = chromadb.PersistentClient(path=persist_dir)
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            raise RuntimeError(
                f"Collection '{collection_name}' not found. "
                f"Run `python data/ingest.py` first to build the knowledge base."
            ) from e

    def retrieve_documents(self, query_embedding: list[float], k: int = 5) -> list[dict]:
        """
        Retrieve the k most similar chunks to the query embedding.

        Returns a list of dicts: {id, text, metadata, distance}
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        docs = []
        ids = results.get("ids", [[]])[0]
        for i in range(len(ids)):
            docs.append({
                "id": ids[i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return docs
