from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class PredictionLogRecord(BaseModel):
    model_name: str
    model_version: str
    symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prediction: dict[str, Any]
    confidence: float
    features_version: str


class PredictionLogger:
    """Logs every model prediction for auditability."""

    def __init__(self) -> None:
        self._records: list[PredictionLogRecord] = []

    def log(self, record: PredictionLogRecord) -> None:
        self._records.append(record)

    def by_symbol(self, symbol: str) -> list[PredictionLogRecord]:
        return [record for record in self._records if record.symbol.upper() == symbol.upper()]
