from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.enums import AnomalySeverity, RegimeLabel, SentimentLabel, StrategyCategory, TargetKind


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketBar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = "unknown"

    @model_validator(mode="after")
    def validate_ohlcv(self) -> "MarketBar":
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("high must be >= open, low and close")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("low must be <= open, high and close")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
        return self


class NewsSentimentEvent(BaseModel):
    symbol: str | None = None
    sector: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    text: str
    sentiment: SentimentLabel | None = None
    sentiment_score: float | None = Field(default=None, ge=-1.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = "news"


class OptionsChainSnapshot(BaseModel):
    symbol: str
    timestamp: datetime
    pcr: float = Field(ge=0.0)
    max_pain: float | None = None
    iv: float | None = Field(default=None, ge=0.0)
    call_oi_change: float = 0.0
    put_oi_change: float = 0.0
    options_volume_call: float = 0.0
    options_volume_put: float = 0.0


class FeatureBuildRequest(BaseModel):
    symbol: str
    market_data: list[MarketBar]
    sentiment_events: list[NewsSentimentEvent] = Field(default_factory=list)
    options_chain: list[OptionsChainSnapshot] = Field(default_factory=list)
    benchmark_data: list[MarketBar] = Field(default_factory=list)
    sector_data: list[MarketBar] = Field(default_factory=list)


class FeatureBuildResponse(BaseModel):
    symbol: str
    rows: int
    latest_timestamp: datetime | None
    features: list[dict[str, Any]]
    explanation: str


class FeatureVectorOutput(BaseModel):
    symbol: str
    timestamp: datetime
    timeframe: str = "1m"
    features: dict[str, float | int | None]


class RegimeDetectionRequest(FeatureBuildRequest):
    """Request body for regime detection using the shared feature input contract."""


class RegimeOutput(BaseModel):
    symbol: str
    timestamp: datetime
    regime: RegimeLabel
    confidence: float = Field(ge=0.0, le=1.0)
    features: dict[str, Any]
    explanation: str


class StrategyPerformanceRecord(BaseModel):
    strategy_name: str
    symbol: str
    sector: str = "unknown"
    regime: str
    timeframe: str = "1d"
    volatility_bucket: str = "normal"
    accuracy: float = Field(ge=0.0, le=1.0)
    win_rate: float = Field(ge=0.0, le=1.0)
    avg_return: float
    max_drawdown: float
    sample_size: int = Field(ge=0)
    last_updated: datetime = Field(default_factory=utc_now)


class WeightingRequest(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=utc_now)
    base_weights: dict[str, float]
    regime: RegimeOutput
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    volatility_score: float = Field(default=0.0, ge=0.0)
    anomalies: list["AnomalyOutput"] = Field(default_factory=list)
    historical_performance: list[StrategyPerformanceRecord] = Field(default_factory=list)
    risk_level: str = "MODERATE"


class WeightingOutput(BaseModel):
    symbol: str
    timestamp: datetime
    weights: dict[str, float]
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class AnomalyOutput(BaseModel):
    symbol: str
    timestamp: datetime
    anomaly_type: str
    severity: AnomalySeverity
    score: float = Field(ge=0.0)
    features: dict[str, Any]
    explanation: str


class AnomalyDetectionRequest(FeatureBuildRequest):
    """Request body for anomaly detection using the shared feature input contract."""


class FinBERTBatchRequest(BaseModel):
    items: list[NewsSentimentEvent]


class FinBERTOutput(BaseModel):
    text: str
    symbol: str | None = None
    sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    raw_scores: dict[str, float]
    event_type: str | None = None
    timestamp: datetime


class TrainingRunRequest(BaseModel):
    model_name: str
    target_kind: TargetKind
    symbol: str
    market_data: list[MarketBar]
    sentiment_events: list[NewsSentimentEvent] = Field(default_factory=list)
    options_chain: list[OptionsChainSnapshot] = Field(default_factory=list)
    horizon: int = Field(default=5, ge=1, le=60)
    walk_forward_splits: int = Field(default=3, ge=2, le=10)


class TrainingRunOutput(BaseModel):
    run_id: str
    model_name: str
    target_kind: TargetKind
    symbol: str
    metrics: dict[str, float]
    feature_columns: list[str]
    model_path: str | None
    explanation: str


class ModelRegistryItem(BaseModel):
    model_name: str
    model_type: str
    target_kind: TargetKind
    path: str | None
    metrics: dict[str, float]
    created_at: datetime


class PaperTradeFeedback(BaseModel):
    symbol: str
    strategy_name: str
    regime: str
    timestamp: datetime = Field(default_factory=utc_now)
    signal: str
    realized_return: float
    max_adverse_excursion: float = 0.0
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
