"""
Stage 2: Embedding Generation

Turns text into a dense vector for similarity search against ChromaDB.

Uses scikit-learn's HashingVectorizer instead of a downloaded neural
embedding model. This is a deliberate engineering tradeoff, not a
shortcut taken by accident -- worth being able to explain in an
interview:

  - Zero network calls, zero model downloads, zero API keys. The SUT
    is fully offline-capable and instant to cold-start.
  - Deterministic and stateless: no vectorizer needs to be fit/persisted
    separately from the vector store itself.
  - Tradeoff: hashed bag-of-words features capture lexical overlap, not
    deep semantic similarity ("optimizer" vs "gradient descent" won't
    match as well as a real sentence-transformer would).

Swap this for `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()`
(local MiniLM) or a Gemini embedding API call when you want real semantic
retrieval quality -- every other stage is unaffected by this choice,
which is exactly why it's isolated in its own module.
"""

from sklearn.feature_extraction.text import HashingVectorizer

EMBEDDING_DIM = 384  # matches common sentence-transformer dims for easy swap-in later

_vectorizer = HashingVectorizer(
    n_features=EMBEDDING_DIM,
    alternate_sign=False,
    norm="l2",
    stop_words="english",
)


def embed_query(text: str) -> list[float]:
    """
    Convert a text string into a dense embedding vector.
    Works identically for queries and document chunks.
    """
    if not text:
        raise ValueError("Cannot embed empty text")

    vector = _vectorizer.transform([text]).toarray()[0]
    return vector.tolist()
