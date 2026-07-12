"""
Context propagation.

A single query fires 8 separate function calls across 8 different
modules. Every event those calls emit needs to be tagged with the same
trace_id so they can be re-assembled into one trace later (Section 4).

contextvars is the right tool here (not a global variable, not a
thread-local) because it's async-safe and correctly isolated per
request even if the FastAPI app someday runs concurrent requests on
the same thread/event loop.
"""

import contextvars
import uuid

trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "trace_id", default=None
)
query_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "query_id", default=None
)


def new_trace_id() -> str:
    return str(uuid.uuid4())


def new_query_id() -> str:
    return str(uuid.uuid4())
