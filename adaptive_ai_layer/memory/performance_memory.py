from __future__ import annotations

from collections import defaultdict

from models.schemas import StrategyPerformanceRecord


class StrategyPerformanceMemory:
    """Stores strategy performance history by regime, symbol, sector, and volatility bucket."""

    def __init__(self) -> None:
        self._records: list[StrategyPerformanceRecord] = []

    def add(self, record: StrategyPerformanceRecord) -> None:
        self._records.append(record)

    def query(self, strategy_name: str | None = None, regime: str | None = None, symbol: str | None = None) -> list[StrategyPerformanceRecord]:
        records = self._records
        if strategy_name:
            records = [record for record in records if record.strategy_name == strategy_name]
        if regime:
            records = [record for record in records if record.regime == regime]
        if symbol:
            records = [record for record in records if record.symbol.upper() == symbol.upper()]
        return records

    def best_by_regime(self) -> dict[str, StrategyPerformanceRecord]:
        grouped: dict[str, list[StrategyPerformanceRecord]] = defaultdict(list)
        for record in self._records:
            grouped[record.regime].append(record)
        return {
            regime: max(items, key=lambda item: (item.accuracy, item.avg_return, item.sample_size))
            for regime, items in grouped.items()
        }
