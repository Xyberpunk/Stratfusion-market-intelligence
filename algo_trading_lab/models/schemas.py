from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from models.enums import ConfidenceLabel, MarketRegime, RiskLevel, RiskProfile, SentimentLabel, TradingSignal


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketDataPoint(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str

    @model_validator(mode="after")
    def validate_ohlcv(self) -> "MarketDataPoint":
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be >= open, close and low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be <= open, close and high")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
        return self


class SentimentInput(BaseModel):
    symbol: str
    timestamp: datetime
    sentiment: SentimentLabel
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    source: str
    confidence: float = Field(ge=0.0, le=1.0)


class OptionsChainInput(BaseModel):
    symbol: str
    timestamp: datetime
    pcr: float = Field(ge=0.0)
    max_pain: float | None = None
    iv: float | None = Field(default=None, ge=0.0)
    call_oi_change: float
    put_oi_change: float


class StrategySignal(BaseModel):
    strategy_name: str
    symbol: str
    timestamp: datetime
    signal: TradingSignal
    confidence: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=-1.0, le=1.0)
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegimeOutput(BaseModel):
    symbol: str
    timestamp: datetime
    regime: MarketRegime
    confidence: float = Field(ge=0.0, le=1.0)
    features: dict[str, Any] = Field(default_factory=dict)


class StrategyBreakdown(BaseModel):
    strategy_name: str
    signal: TradingSignal
    raw_weight: float
    adjusted_weight: float
    confidence: float
    score: float
    contribution: float
    reason: str


class EnsembleOutput(BaseModel):
    symbol: str
    timestamp: datetime
    bullish_probability: float = Field(ge=0.0, le=1.0)
    bearish_probability: float = Field(ge=0.0, le=1.0)
    neutral_probability: float = Field(ge=0.0, le=1.0)
    confidence: ConfidenceLabel
    suggested_action: TradingSignal
    risk_level: RiskLevel
    explanation: str
    strategy_breakdown: list[StrategyBreakdown]
    regime: str | None = None
    weights_used: dict[str, float] = Field(default_factory=dict)


class RiskOutput(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=utc_now)
    approved: bool = False
    input_action: str = "HOLD"
    final_action: str = "HOLD"
    entry_price: float
    stop_loss: float | None
    target: float | None
    risk_reward_ratio: float | None
    position_size: float | None
    capital_at_risk: float | None
    max_drawdown_limit: float
    risk_level: RiskLevel
    reason: str = ""
    override_applied: bool = False


class FinalTradingGuidance(BaseModel):
    ensemble: EnsembleOutput
    risk: RiskOutput
    final_action: TradingSignal
    final_explanation: str


class BacktestResult(BaseModel):
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    average_return: float
    accuracy: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccuracyOutput(BaseModel):
    strategy_name: str
    symbol: str
    regime: str
    timeframe: str
    accuracy: float
    win_rate: float
    avg_return: float
    sample_size: int


class CustomStrategyComponent(BaseModel):
    name: str
    weight: float = Field(gt=0.0, le=1.0)


class CustomStrategyConfig(BaseModel):
    name: str
    strategies: list[CustomStrategyComponent]
    risk_profile: RiskProfile = RiskProfile.MODERATE
    dynamic_weighting: bool = True
    symbols: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    timeframes: list[str] = Field(default_factory=lambda: ["1d"])
    regime_behavior: dict[str, float] = Field(default_factory=dict)

    @field_validator("strategies")
    @classmethod
    def validate_strategies(cls, value: list[CustomStrategyComponent]) -> list[CustomStrategyComponent]:
        if not value:
            raise ValueError("at least one strategy component is required")
        total = sum(component.weight for component in value)
        if total <= 0:
            raise ValueError("strategy weights must sum to a positive value")
        return value


class GenerateSignalRequest(BaseModel):
    symbol: str
    market_data: list[MarketDataPoint]
    sentiments: list[SentimentInput] = Field(default_factory=list)
    options_chain: OptionsChainInput | None = None
    strategy_names: list[str] | None = None
    custom_weights: dict[str, float] = Field(default_factory=dict)
    capital: float = Field(default=1_000_000.0, gt=0.0)
    risk_per_trade: float = Field(default=0.01, gt=0.0, le=0.1)


class EnsembleRunRequest(BaseModel):
    symbol: str
    signals: list[StrategySignal]
    regime: RegimeOutput | None = None
    custom_weights: dict[str, float] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.MODERATE


class BacktestRunRequest(BaseModel):
    symbol: str
    market_data: list[MarketDataPoint]
    strategy_name: str | None = None
    custom_strategy: CustomStrategyConfig | None = None
    initial_capital: float = Field(default=1_000_000.0, gt=0.0)
    train_ratio: float = Field(default=0.7, gt=0.1, lt=0.95)


class AnomalyEvent(BaseModel):
    symbol: str
    timestamp: datetime
    anomaly_type: str
    severity: RiskLevel
    score: float = Field(ge=0.0)
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)
