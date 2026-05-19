from __future__ import annotations

from tests.test_features import sample_bars
from feature_store.feature_store import InMemoryFeatureStore


def test_feature_store_write_and_latest_read() -> None:
    store = InMemoryFeatureStore()
    timestamp = sample_bars()[0].timestamp
    store.write_snapshot("INFY", timestamp, {"rsi_14": 55.0, "trend_strength": 0.4})
    latest = store.latest("INFY")
    assert latest["rsi_14"].feature_value == 55.0
    assert latest["rsi_14"].freshness_status in {"FRESH", "STALE", "EXPIRED"}
