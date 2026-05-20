from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketBar(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = "dashboard"


class NewsSentimentEvent(BaseModel):
    symbol: str | None = None
    sector: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    text: str
    sentiment: str | None = None
    sentiment_score: float | None = Field(default=None, ge=-1.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source: str = "dashboard"


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


class LatestNewsItem(BaseModel):
    id: int
    source: str
    title: str
    url: str
    summary: str | None = None
    published_at: datetime | None = None
    scraped_at: datetime
    sentiment: str | None = None
    sentiment_score: float | None = None
    semantic_duplicate: bool = False


class UnifiedPipelineRequest(BaseModel):
    symbol: str
    market_data: list[MarketBar]
    sentiment_events: list[NewsSentimentEvent] = Field(default_factory=list)
    options_chain: list[OptionsChainSnapshot] = Field(default_factory=list)
    benchmark_data: list[MarketBar] = Field(default_factory=list)
    sector_data: list[MarketBar] = Field(default_factory=list)
    base_weights: dict[str, float] = Field(default_factory=lambda: {
        "Breakout": 0.16,
        "MACD Momentum": 0.16,
        "VWAP": 0.16,
        "RSI Reversal": 0.16,
        "ATR Volatility System": 0.16,
        "FinBERT Sentiment": 0.20,
    })
    strategy_names: list[str] | None = None
    capital: float = Field(default=1_000_000.0, gt=0.0)
    risk_per_trade: float = Field(default=0.01, gt=0.0, le=0.1)


class PlatformStatus(BaseModel):
    gateway: str
    adaptive_ai: str
    algo_lab: str
    scraper_news_store: str
    checked_at: datetime


class UnifiedPipelineResponse(BaseModel):
    symbol: str
    timestamp: datetime
    sentiment_outputs: list[dict[str, Any]]
    feature_vector: dict[str, Any] | None = None
    regime: dict[str, Any]
    anomalies: list[dict[str, Any]]
    weighting: dict[str, Any]
    trading_guidance: dict[str, Any]
    latest_news: list[LatestNewsItem]
    explanation: str
