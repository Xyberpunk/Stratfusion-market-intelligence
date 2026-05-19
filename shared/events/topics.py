from __future__ import annotations

from enum import StrEnum


class KafkaTopic(StrEnum):
    NEWS_RAW = "news.raw"
    NEWS_CLEANED = "news.cleaned"
    NEWS_SENTIMENT_COMPLETED = "news.sentiment.completed"
    MARKET_OHLCV_RAW = "market.ohlcv.raw"
    MARKET_OPTIONS_RAW = "market.options.raw"
    FEATURES_GENERATED = "features.generated"
    REGIME_DETECTED = "regime.detected"
    STRATEGY_SIGNAL_GENERATED = "strategy.signal.generated"
    ENSEMBLE_SIGNAL_GENERATED = "ensemble.signal.generated"
    RISK_EVALUATED = "risk.evaluated"
    FINAL_SIGNAL_GENERATED = "final.signal.generated"
    ANOMALY_DETECTED = "anomaly.detected"
    MODEL_PREDICTION_GENERATED = "model.prediction.generated"
    SYSTEM_DEAD_LETTER = "system.dead_letter"
    SYSTEM_HEALTH = "system.health"


ALL_TOPICS: tuple[KafkaTopic, ...] = tuple(KafkaTopic)
