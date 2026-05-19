from __future__ import annotations

from collections import defaultdict

from models.schemas import RegimeOutput


class RegimeMemory:
    """Stores historical regime snapshots for market memory."""

    def __init__(self) -> None:
        self._items: dict[str, list[RegimeOutput]] = defaultdict(list)

    def add(self, output: RegimeOutput) -> None:
        self._items[output.symbol.upper()].append(output)

    def latest(self, symbol: str) -> RegimeOutput | None:
        items = self._items.get(symbol.upper(), [])
        return items[-1] if items else None

    def history(self, symbol: str) -> list[RegimeOutput]:
        return self._items.get(symbol.upper(), [])
