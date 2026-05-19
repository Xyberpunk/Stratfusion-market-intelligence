from __future__ import annotations

from collections import defaultdict

from models.schemas import AnomalyOutput


class AnomalyMemory:
    """Stores anomaly events and their future outcome context."""

    def __init__(self) -> None:
        self._items: dict[str, list[AnomalyOutput]] = defaultdict(list)

    def add_many(self, outputs: list[AnomalyOutput]) -> None:
        for output in outputs:
            self._items[output.symbol.upper()].append(output)

    def recent(self, symbol: str, limit: int = 50) -> list[AnomalyOutput]:
        return self._items.get(symbol.upper(), [])[-limit:]
