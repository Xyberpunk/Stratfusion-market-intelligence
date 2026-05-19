from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from feature_store.freshness_checker import FeatureFreshnessChecker
from feature_store.feature_versioning import FeatureVersioner


class FeatureRecord(BaseModel):
    symbol: str
    timestamp: datetime
    timeframe: str
    feature_name: str
    feature_value: float
    feature_version: str
    source: str
    freshness_status: str


class InMemoryFeatureStore:
    """Feature store with latest and historical serving semantics."""

    def __init__(self) -> None:
        self.versioner = FeatureVersioner()
        self.freshness = FeatureFreshnessChecker()
        self._records: list[FeatureRecord] = []

    def write_snapshot(self, symbol: str, timestamp: datetime, features: dict[str, float], timeframe: str = "1d", source: str = "adaptive_ai_layer") -> list[FeatureRecord]:
        records: list[FeatureRecord] = []
        for name, value in features.items():
            if not isinstance(value, (int, float)):
                continue
            record = FeatureRecord(
                symbol=symbol.upper(),
                timestamp=timestamp,
                timeframe=timeframe,
                feature_name=name,
                feature_value=float(value),
                feature_version=self.versioner.version(name),
                source=source,
                freshness_status=self.freshness.status(timestamp),
            )
            records.append(record)
        self._records.extend(records)
        return records

    def latest(self, symbol: str, timeframe: str = "1d") -> dict[str, FeatureRecord]:
        matching = [record for record in self._records if record.symbol == symbol.upper() and record.timeframe == timeframe]
        latest: dict[str, FeatureRecord] = {}
        for record in sorted(matching, key=lambda item: item.timestamp):
            latest[record.feature_name] = record
        return latest

    def historical(self, symbol: str, feature_name: str, start: datetime | None = None, end: datetime | None = None) -> list[FeatureRecord]:
        records = [record for record in self._records if record.symbol == symbol.upper() and record.feature_name == feature_name]
        if start:
            records = [record for record in records if record.timestamp >= start]
        if end:
            records = [record for record in records if record.timestamp <= end]
        return sorted(records, key=lambda item: item.timestamp)
