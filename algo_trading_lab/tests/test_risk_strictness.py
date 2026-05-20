from __future__ import annotations

from datetime import timedelta

from config import Settings
from data.feature_builder import FeatureBuilder
from models.enums import ConfidenceLabel, RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, StrategyBreakdown
from risk.risk_engine import RiskEngine
from strategies.base import StrategyContext
from tests.test_strategies import sample_market_data


def _ensemble(features, probability: float = 0.74, confidence: ConfidenceLabel = ConfidenceLabel.HIGH) -> EnsembleOutput:
    return EnsembleOutput(
        symbol="INFY",
        timestamp=features.iloc[-1]["timestamp"],
        bullish_probability=probability,
        bearish_probability=0.12,
        neutral_probability=max(0.0, 1 - probability - 0.12),
        confidence=confidence,
        suggested_action=TradingSignal.BUY,
        risk_level=RiskLevel.MODERATE,
        explanation="Combined market intelligence suggests bullish probability.",
        strategy_breakdown=[
            StrategyBreakdown(strategy_name="MACD Momentum", signal=TradingSignal.BUY, raw_weight=0.3, adjusted_weight=0.3, confidence=0.8, score=0.7, contribution=0.2, reason="bullish"),
            StrategyBreakdown(strategy_name="VWAP", signal=TradingSignal.BUY, raw_weight=0.2, adjusted_weight=0.2, confidence=0.7, score=0.5, contribution=0.1, reason="bullish"),
        ],
    )


def test_low_confidence_and_weak_probability_hold() -> None:
    features = FeatureBuilder().build(sample_market_data("INFY", rows=70))
    context = StrategyContext(symbol="INFY", features=features, sentiments=[])
    guidance = RiskEngine(Settings()).evaluate(context=context, ensemble=_ensemble(features, 0.56, ConfidenceLabel.LOW), capital=100000, risk_per_trade=0.01)
    assert guidance.final_action == TradingSignal.HOLD
    assert guidance.risk.override_applied is True


def test_stale_data_holds_signal() -> None:
    points = sample_market_data("INFY", rows=70)
    for point in points:
        point.timestamp = point.timestamp - timedelta(days=30)
    features = FeatureBuilder().build(points)
    context = StrategyContext(symbol="INFY", features=features, sentiments=[])
    guidance = RiskEngine(Settings()).evaluate(context=context, ensemble=_ensemble(features), capital=100000, risk_per_trade=0.01)
    assert guidance.final_action == TradingSignal.HOLD
    assert "stale" in guidance.risk.reason
