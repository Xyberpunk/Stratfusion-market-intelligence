from __future__ import annotations

from feature_store.feature_store import FeatureRecord, InMemoryFeatureStore


class FeatureServingService:
    """Serving API for latest and historical feature reads."""

    def __init__(self, store: InMemoryFeatureStore) -> None:
        self.store = store

    def latest_values(self, symbol: str, timeframe: str = "1d") -> dict[str, float]:
        return {name: record.feature_value for name, record in self.store.latest(symbol, timeframe).items()}

    def latest_records(self, symbol: str, timeframe: str = "1d") -> list[FeatureRecord]:
        return list(self.store.latest(symbol, timeframe).values())
