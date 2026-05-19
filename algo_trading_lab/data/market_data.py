from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from models.schemas import MarketDataPoint


class MarketDataNormalizer:
    """Normalizes external OHLCV rows into the platform schema."""

    @staticmethod
    def from_records(records: list[dict[str, object]], symbol: str, source: str) -> list[MarketDataPoint]:
        normalized: list[MarketDataPoint] = []
        for record in records:
            timestamp = record.get("timestamp") or record.get("date") or datetime.now(timezone.utc)
            normalized.append(
                MarketDataPoint(
                    symbol=str(record.get("symbol") or symbol).upper(),
                    timestamp=timestamp if isinstance(timestamp, datetime) else pd.to_datetime(timestamp).to_pydatetime(),
                    open=float(record["open"]),
                    high=float(record["high"]),
                    low=float(record["low"]),
                    close=float(record["close"]),
                    volume=float(record.get("volume", 0.0)),
                    source=source,
                )
            )
        return normalized

    @staticmethod
    def to_dataframe(points: list[MarketDataPoint]) -> pd.DataFrame:
        if not points:
            return pd.DataFrame(columns=["symbol", "timestamp", "open", "high", "low", "close", "volume", "source"])
        frame = pd.DataFrame([point.model_dump() for point in points])
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame.sort_values("timestamp").reset_index(drop=True)
