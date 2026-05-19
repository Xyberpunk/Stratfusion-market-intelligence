from __future__ import annotations

from datetime import datetime, timezone

from ai.explanation_engine import ExplanationEngine
from config import Settings
from ensemble.dynamic_weighting import DynamicWeightingEngine
from ensemble.ensemble_engine import EnsembleEngine
from ensemble.weight_manager import WeightManager
from models.enums import RiskLevel, TradingSignal
from models.schemas import StrategySignal
from strategies.registry import StrategyRegistry


def test_ensemble_produces_probability_guidance() -> None:
    registry = StrategyRegistry()
    manager = WeightManager(Settings(), registry)
    engine = EnsembleEngine(DynamicWeightingEngine(manager), ExplanationEngine())
    now = datetime.now(timezone.utc)
    signals = [
        StrategySignal(strategy_name="RSI Reversal", symbol="INFY", timestamp=now, signal=TradingSignal.BUY, confidence=0.8, score=0.7, reason="oversold", metadata={}),
        StrategySignal(strategy_name="MACD Momentum", symbol="INFY", timestamp=now, signal=TradingSignal.BUY, confidence=0.7, score=0.5, reason="positive", metadata={}),
        StrategySignal(strategy_name="VWAP", symbol="INFY", timestamp=now, signal=TradingSignal.SELL, confidence=0.4, score=-0.3, reason="below", metadata={}),
    ]
    output = engine.run(symbol="INFY", signals=signals, regime=None, risk_level=RiskLevel.MODERATE)
    assert output.bullish_probability > output.bearish_probability
    assert "Combined market intelligence" in output.explanation
    assert "guarantee" not in output.explanation.lower()
