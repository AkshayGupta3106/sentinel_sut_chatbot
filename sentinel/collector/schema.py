"""
The core data contract of the entire platform.

Every stage of every query produces exactly one StageEvent. Sections
4-8 (trace assembly, metrics, regression detection, RCA) are all just
different ways of querying and aggregating a table of these.
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class StageEvent(BaseModel):
    event_id: str
    trace_id: str
    query_id: Optional[str] = None

    stage_name: str

    timestamp_start: datetime
    timestamp_end: datetime
    latency_ms: float

    status: Literal["success", "error"]

    input_summary: dict
    output_summary: dict
    metadata: dict = {}

    error: Optional[str] = None
