from __future__ import annotations

from collections import defaultdict

from models.schemas import AccuracyOutput


class StrategyPerformanceStore:
    """Stores accuracy snapshots grouped by strategy."""

    def __init__(self) -> None:
        self._items: dict[str, list[AccuracyOutput]] = defaultdict(list)

    def add(self, item: AccuracyOutput) -> None:
        self._items[item.strategy_name].append(item)

    def get(self, strategy_name: str) -> list[AccuracyOutput]:
        return self._items.get(strategy_name, [])

    def all(self) -> list[AccuracyOutput]:
        return [item for items in self._items.values() for item in items]

    def get_strategy_performance_by_regime(self, strategy_name: str, regime: str) -> list[AccuracyOutput]:
        return [item for item in self.get(strategy_name) if item.regime.upper() == regime.upper()]

    def get_strategy_performance_by_symbol(self, strategy_name: str, symbol: str) -> list[AccuracyOutput]:
        return [item for item in self.get(strategy_name) if item.symbol.upper() == symbol.upper()]

    def get_recent_strategy_accuracy(self, strategy_name: str) -> float:
        rows = self.get(strategy_name)
        return rows[-1].accuracy if rows else 0.0

    def by_symbol_and_regime(self, symbol: str, regime: str) -> list[AccuracyOutput]:
        return [
            item
            for item in self.all()
            if item.symbol.upper() == symbol.upper() and item.regime.upper() == regime.upper()
        ]
