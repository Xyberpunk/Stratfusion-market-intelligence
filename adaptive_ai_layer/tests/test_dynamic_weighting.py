from __future__ import annotations

from config import Settings
from models.enums import RegimeLabel
from models.schemas import RegimeOutput, WeightingRequest
from weighting.dynamic_weight_engine import DynamicWeightEngine
from tests.test_features import sample_bars


def test_dynamic_weighting_normalizes_and_explains() -> None:
    timestamp = sample_bars()[0].timestamp
    regime = RegimeOutput(
        symbol="RELIANCE",
        timestamp=timestamp,
        regime=RegimeLabel.TRENDING,
        confidence=0.82,
        features={"trend_strength": 0.5},
        explanation="Market classified as TRENDING.",
    )
    request = WeightingRequest(
        symbol="RELIANCE",
        timestamp=timestamp,
        base_weights={"MACD Momentum": 0.25, "RSI Reversal": 0.25, "ATR Volatility": 0.25, "FinBERT Sentiment": 0.25},
        regime=regime,
        sentiment_score=0.3,
        volatility_score=0.4,
    )
    output = DynamicWeightEngine(Settings()).suggest(request)
    assert abs(sum(output.weights.values()) - 1.0) < 1e-6
    assert output.weights["MACD Momentum"] > output.weights["RSI Reversal"]
    assert output.reason
