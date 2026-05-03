# Metadata collection schemas — Iceberg snapshot batch metadata.
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class BatchMetadataOut(BaseModel):
    """One Iceberg snapshot batch record."""
    id: str
    table_id: str
    snapshot_id: str
    parent_snapshot_id: Optional[str] = None
    date_hour: Optional[datetime] = None
    operation: Optional[str] = None          # append | overwrite | replace | delete
    committed_at: Optional[datetime] = None
    # Row/file deltas for this batch
    added_records: Optional[int] = None
    added_files: Optional[int] = None
    deleted_rows: Optional[int] = None
    deleted_files: Optional[int] = None
    # Cumulative table stats
    total_records: Optional[int] = None
    total_files: Optional[int] = None
    total_size_bytes: Optional[int] = None
    # Quality / freshness
    freshness_lag_minutes: Optional[int] = None
    schema_id: Optional[int] = None
    collected_at: datetime

    model_config = {"from_attributes": True}
