"""
Stage 1: Query Validation

Cheap, fast sanity checks before spending any money/latency on embedding
or generation. This is the first stage Sentinel AI will wrap -- and the
cheapest place to reject a bad query.
"""

MAX_QUERY_LENGTH = 1000


def validate_query(raw_query: str) -> str:
    """
    Validate and normalize an incoming user query.

    Raises:
        ValueError: if the query is empty, whitespace-only, or too long.
    """
    if raw_query is None:
        raise ValueError("Query cannot be None")

    query = raw_query.strip()

    if not query:
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(
            f"Query too long ({len(query)} chars). Max is {MAX_QUERY_LENGTH}."
        )

    return query
