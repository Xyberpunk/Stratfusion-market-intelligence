from __future__ import annotations

from datetime import datetime, timezone

from config import Settings
from ensemble.dynamic_weighting import DynamicWeightingEngine
from ensemble.weight_manager import WeightManager
from models.enums import MarketRegime, TradingSignal
from models.schemas import AccuracyOutput, RegimeOutput, StrategySignal
from strategies.registry import StrategyRegistry


def _signal(name: str) -> StrategySignal:
    return StrategySignal(
        strategy_name=name,
        symbol="INFY",
        timestamp=datetime.now(timezone.utc),
        signal=TradingSignal.BUY,
        confidence=0.8,
        score=0.7,
        reason="test",
    )


def test_accuracy_memory_adjusts_weights_without_dominating() -> None:
    registry = StrategyRegistry()
    engine = DynamicWeightingEngine(WeightManager(Settings(), registry))
    signals = [_signal("MACD Momentum"), _signal("RSI Reversal"), _signal("VWAP")]
    regime = RegimeOutput(symbol="INFY", timestamp=datetime.now(timezone.utc), regime=MarketRegime.TRENDING, confidence=0.8)
    weights = engine.weights(
        signals=signals,
        regime=regime,
        accuracy=[
            AccuracyOutput(strategy_name="MACD Momentum", symbol="INFY", regime="trending", timeframe="1d", accuracy=0.82, win_rate=0.8, avg_return=0.02, sample_size=30),
            AccuracyOutput(strategy_name="RSI Reversal", symbol="INFY", regime="trending", timeframe="1d", accuracy=0.35, win_rate=0.35, avg_return=-0.01, sample_size=30),
        ],
    )
    assert weights["MACD Momentum"] > weights["RSI Reversal"]
    assert max(weights.values()) <= 0.45
    assert min(weights.values()) >= 0.05
