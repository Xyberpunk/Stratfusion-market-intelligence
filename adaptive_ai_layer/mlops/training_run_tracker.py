from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class TrainingRunRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    model_name: str
    model_version: str | None = None
    status: str = "CREATED"
    metrics: dict[str, float] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class TrainingRunTracker:
    """Tracks model training run lifecycle."""

    def __init__(self) -> None:
        self._runs: dict[str, TrainingRunRecord] = {}

    def start(self, model_name: str) -> TrainingRunRecord:
        record = TrainingRunRecord(model_name=model_name)
        self._runs[record.run_id] = record
        return record

    def finish(self, run_id: str, model_version: str, metrics: dict[str, float]) -> TrainingRunRecord:
        record = self._runs[run_id]
        record.model_version = model_version
        record.metrics = metrics
        record.status = "COMPLETED"
        record.finished_at = datetime.now(timezone.utc)
        return record

    def fail(self, run_id: str) -> TrainingRunRecord:
        record = self._runs[run_id]
        record.status = "FAILED"
        record.finished_at = datetime.now(timezone.utc)
        return record
