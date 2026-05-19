from __future__ import annotations

from enum import StrEnum


class SentimentLabel(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RegimeLabel(StrEnum):
    TRENDING = "TRENDING"
    SIDEWAYS = "SIDEWAYS"
    PANIC = "PANIC"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    BULLISH_REGIME = "BULLISH_REGIME"
    BEARISH_REGIME = "BEARISH_REGIME"
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"


class StrategyCategory(StrEnum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    VOLATILITY = "volatility"
    SENTIMENT = "sentiment"
    OPTIONS = "options"
    RISK_OFF = "risk_off"


class AnomalySeverity(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class TargetKind(StrEnum):
    DIRECTIONAL = "directional"
    REGIME = "regime"
    STRATEGY_SUITABILITY = "strategy_suitability"


class DirectionalTarget(StrEnum):
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"
