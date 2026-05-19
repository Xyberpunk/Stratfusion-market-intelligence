from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseEvent(BaseModel):
    """Canonical event envelope shared by all services."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    source: str
    timestamp: datetime = Field(default_factory=utc_now)
    symbol: str | None = None
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    payload: dict[str, Any]
    schema_version: str = "1.0"


class NewsRawEvent(BaseEvent):
    event_type: str = "news.raw"


class NewsCleanedEvent(BaseEvent):
    event_type: str = "news.cleaned"


class SentimentCompletedEvent(BaseEvent):
    event_type: str = "news.sentiment.completed"


class MarketOHLCVRawEvent(BaseEvent):
    event_type: str = "market.ohlcv.raw"


class MarketOptionsRawEvent(BaseEvent):
    event_type: str = "market.options.raw"


class FeaturesGeneratedEvent(BaseEvent):
    event_type: str = "features.generated"


class RegimeDetectedEvent(BaseEvent):
    event_type: str = "regime.detected"


class StrategySignalGeneratedEvent(BaseEvent):
    event_type: str = "strategy.signal.generated"


class EnsembleSignalGeneratedEvent(BaseEvent):
    event_type: str = "ensemble.signal.generated"


class RiskEvaluatedEvent(BaseEvent):
    event_type: str = "risk.evaluated"


class FinalSignalGeneratedEvent(BaseEvent):
    event_type: str = "final.signal.generated"


class AnomalyDetectedEvent(BaseEvent):
    event_type: str = "anomaly.detected"


class ModelPredictionGeneratedEvent(BaseEvent):
    event_type: str = "model.prediction.generated"


class DeadLetterEvent(BaseEvent):
    event_type: str = "system.dead_letter"
    original_topic: str | None = None
    error: str
    retryable: bool = False


class HealthEvent(BaseEvent):
    event_type: str = "system.health"
