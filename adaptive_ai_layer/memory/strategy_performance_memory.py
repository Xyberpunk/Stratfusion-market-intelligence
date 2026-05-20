from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class StrategyOutcomeRecord(BaseModel):
    strategy_name: str
    symbol: str
    regime: str
    signal: Literal["BUY", "SELL", "HOLD"]
    result: Literal["WIN", "LOSS", "NEUTRAL", "PENDING"]
    pnl: float | None = None
    drawdown: float | None = None
    volatility: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategyPerformanceMemoryStore:
    """Collects strategy outcomes for future adaptive trust decisions."""

    def __init__(self) -> None:
        self._records: list[StrategyOutcomeRecord] = []

    def record_signal_outcome(self, record: StrategyOutcomeRecord) -> None:
        self._records.append(record)

    def get_strategy_performance_by_regime(self, strategy_name: str, regime: str) -> list[StrategyOutcomeRecord]:
        return [
            record
            for record in self._records
            if record.strategy_name == strategy_name and record.regime.upper() == regime.upper()
        ]

    def get_strategy_performance_by_symbol(self, strategy_name: str, symbol: str) -> list[StrategyOutcomeRecord]:
        return [
            record
            for record in self._records
            if record.strategy_name == strategy_name and record.symbol.upper() == symbol.upper()
        ]

    def get_recent_strategy_accuracy(self, strategy_name: str, limit: int = 100) -> float:
        records = [record for record in self._records if record.strategy_name == strategy_name and record.result != "PENDING"][-limit:]
        if not records:
            return 0.0
        return sum(1 for record in records if record.result == "WIN") / len(records)
