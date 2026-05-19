from __future__ import annotations

from config import Settings
from data.feature_builder import FeatureBuilder
from models.enums import ConfidenceLabel, RiskLevel, TradingSignal
from models.schemas import EnsembleOutput
from risk.risk_engine import RiskEngine
from strategies.base import StrategyContext
from tests.test_strategies import sample_market_data


def test_risk_engine_returns_stop_target_and_final_action() -> None:
    features = FeatureBuilder().build(sample_market_data(rows=60))
    context = StrategyContext(symbol="TCS", features=features, sentiments=[])
    ensemble = EnsembleOutput(
        symbol="TCS",
        timestamp=features.iloc[-1]["timestamp"],
        bullish_probability=0.74,
        bearish_probability=0.18,
        neutral_probability=0.08,
        confidence=ConfidenceLabel.HIGH,
        suggested_action=TradingSignal.BUY,
        risk_level=RiskLevel.MODERATE,
        explanation="Combined market intelligence suggests bullish probability.",
        strategy_breakdown=[],
    )
    guidance = RiskEngine(Settings()).evaluate(context=context, ensemble=ensemble, capital=100000, risk_per_trade=0.01)
    assert guidance.risk.stop_loss < guidance.risk.entry_price
    assert guidance.risk.target > guidance.risk.entry_price
    assert guidance.final_action in {TradingSignal.BUY, TradingSignal.HOLD}
