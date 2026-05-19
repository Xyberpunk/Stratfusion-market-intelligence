from __future__ import annotations

from api.routes_pipeline import _aggregate_sentiment_score, _risk_level_from_anomalies


def test_aggregate_sentiment_score() -> None:
    score = _aggregate_sentiment_score(
        [
            {"sentiment": "bullish", "confidence": 0.8},
            {"sentiment": "bearish", "confidence": 0.2},
        ]
    )
    assert score > 0


def test_risk_level_from_anomalies() -> None:
    assert _risk_level_from_anomalies([{"severity": "HIGH"}]) == "HIGH"
    assert _risk_level_from_anomalies([{"severity": "MODERATE"}]) == "MODERATE"
    assert _risk_level_from_anomalies([]) == "LOW"
