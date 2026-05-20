from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal

from shared.data.schemas import NormalizedOHLCV

Timeframe = Literal["1m", "5m", "15m"]


class CandleAggregator:
    """Aggregates NSE quote snapshots into rolling 1m, 5m, and 15m candles."""

    _WINDOWS: dict[Timeframe, int] = {"1m": 60, "5m": 300, "15m": 900}

    def __init__(self) -> None:
        self._candles: dict[tuple[str, Timeframe], dict[datetime, NormalizedOHLCV]] = defaultdict(dict)

    def add_tick(self, symbol: str, price: float, volume: float | None, timestamp: datetime | None = None) -> list[NormalizedOHLCV]:
        """Adds one tick/snapshot and returns the updated timeframe candles."""
        if price <= 0:
            raise ValueError("price must be positive")
        ts = self._to_utc(timestamp or datetime.now(timezone.utc))
        safe_volume = max(float(volume or 0.0), 0.0)
        updated: list[NormalizedOHLCV] = []
        for timeframe in self._WINDOWS:
            bucket = self._floor(ts, timeframe)
            key = (symbol.upper(), timeframe)
            existing = self._candles[key].get(bucket)
            if existing is None:
                candle = NormalizedOHLCV(
                    symbol=symbol.upper(),
                    timestamp=bucket,
                    timeframe=timeframe,
                    open=float(price),
                    high=float(price),
                    low=float(price),
                    close=float(price),
                    volume=safe_volume,
                    source="NSEPython",
                )
            else:
                candle = existing.model_copy(
                    update={
                        "high": max(existing.high, float(price)),
                        "low": min(existing.low, float(price)),
                        "close": float(price),
                        "volume": max(existing.volume, safe_volume),
                    }
                )
            self._candles[key][bucket] = candle
            updated.append(candle)
        return updated

    def build_1m(self, symbol: str | None = None) -> list[NormalizedOHLCV]:
        return self._latest("1m", symbol)

    def build_5m(self, symbol: str | None = None) -> list[NormalizedOHLCV]:
        return self._latest("5m", symbol)

    def build_15m(self, symbol: str | None = None) -> list[NormalizedOHLCV]:
        return self._latest("15m", symbol)

    def latest(self, symbol: str, timeframe: Timeframe = "1m", limit: int = 100) -> list[NormalizedOHLCV]:
        candles = sorted(self._candles[(symbol.upper(), timeframe)].values(), key=lambda item: item.timestamp)
        return candles[-limit:]

    def _latest(self, timeframe: Timeframe, symbol: str | None) -> list[NormalizedOHLCV]:
        if symbol:
            return self.latest(symbol, timeframe)
        rows: list[NormalizedOHLCV] = []
        for (key_symbol, key_timeframe), candles in self._candles.items():
            if key_timeframe == timeframe:
                rows.extend(self.latest(key_symbol, timeframe, limit=len(candles)))
        return sorted(rows, key=lambda item: (item.symbol, item.timestamp))

    @classmethod
    def _floor(cls, value: datetime, timeframe: Timeframe) -> datetime:
        ts = cls._to_utc(value)
        seconds = cls._WINDOWS[timeframe]
        epoch = int(ts.timestamp())
        floored = epoch - (epoch % seconds)
        return datetime.fromtimestamp(floored, tz=timezone.utc)

    @staticmethod
    def _to_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
