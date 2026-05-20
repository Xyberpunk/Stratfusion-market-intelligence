from __future__ import annotations

from collections import defaultdict
from typing import Literal

from shared.data.schemas import NormalizedOHLCV

Timeframe = Literal["1m", "5m", "15m"]


class InMemoryCandleStore:
    """Process-local candle store used when durable market storage is disabled."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, Timeframe], dict[str, NormalizedOHLCV]] = defaultdict(dict)

    def save_market_ohlcv(self, candle: NormalizedOHLCV) -> None:
        key = (candle.symbol.upper(), candle.timeframe)
        self._items[key][candle.timestamp.isoformat()] = candle

    def save_many(self, candles: list[NormalizedOHLCV]) -> None:
        for candle in candles:
            self.save_market_ohlcv(candle)

    def latest(self, symbol: str, timeframe: Timeframe = "1m", limit: int = 100) -> list[NormalizedOHLCV]:
        values = sorted(self._items[(symbol.upper(), timeframe)].values(), key=lambda item: item.timestamp)
        return values[-limit:]
