from __future__ import annotations

from datetime import datetime, timezone

from explanation.explanation_engine import FinalExplanationEngine
from models.enums import ConfidenceLabel, RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, RiskOutput, StrategySignal


def test_final_explanation_includes_regime_strategy_sentiment_and_risk() -> None:
    now = datetime.now(timezone.utc)
    ensemble = EnsembleOutput(
        symbol="INFY",
        timestamp=now,
        bullish_probability=0.72,
        bearish_probability=0.18,
        neutral_probability=0.10,
        confidence=ConfidenceLabel.HIGH,
        suggested_action=TradingSignal.BUY,
        risk_level=RiskLevel.MODERATE,
        explanation="Combined market intelligence suggests bullish probability.",
        strategy_breakdown=[],
        regime="TRENDING",
        weights_used={"MACD Momentum": 0.3},
    )
    risk = RiskOutput(symbol="INFY", entry_price=100, stop_loss=97, target=106, risk_reward_ratio=2, position_size=10, capital_at_risk=30, max_drawdown_limit=0.15, risk_level=RiskLevel.MODERATE, final_action="BUY", reason="approved")
    signal = StrategySignal(strategy_name="MACD Momentum", symbol="INFY", timestamp=now, signal=TradingSignal.BUY, confidence=0.8, score=0.7, reason="macd bullish")
    explanation = FinalExplanationEngine().explain(ensemble=ensemble, risk=risk, strategy_signals=[signal], sentiment_score=0.5, options_summary={"pcr": 1.2, "iv": 22}, regime_explanation="Regime is trending.")
    assert "Combined market intelligence" in explanation
    assert "TRENDING" in explanation
    assert "MACD Momentum" in explanation
