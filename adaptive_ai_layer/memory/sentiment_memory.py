from __future__ import annotations

from pydantic import BaseModel


class SentimentOutcomeRecord(BaseModel):
    symbol: str
    sentiment: str
    confidence: float
    realized_return: float
    accurate: bool


class SentimentMemory:
    """Tracks whether sentiment signals were directionally useful."""

    def __init__(self) -> None:
        self._records: list[SentimentOutcomeRecord] = []

    def add(self, record: SentimentOutcomeRecord) -> None:
        self._records.append(record)

    def accuracy(self, symbol: str | None = None) -> float:
        records = self._records if symbol is None else [record for record in self._records if record.symbol.upper() == symbol.upper()]
        if not records:
            return 0.0
        return sum(1 for record in records if record.accurate) / len(records)
