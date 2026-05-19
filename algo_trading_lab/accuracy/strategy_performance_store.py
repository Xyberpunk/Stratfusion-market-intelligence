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
