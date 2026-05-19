from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AuditRecord(BaseModel):
    correlation_id: str
    event_type: str
    service: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any]


class AuditLog:
    """Append-only in-memory audit log for local operation and tests."""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def append(self, record: AuditRecord) -> None:
        self.records.append(record)

    def by_correlation_id(self, correlation_id: str) -> list[AuditRecord]:
        return [record for record in self.records if record.correlation_id == correlation_id]
