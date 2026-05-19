from __future__ import annotations

from config import Settings
from data.feature_builder import FeatureBuilder
from regime.regime_detector import RegimeDetector
from strategies.base import StrategyContext
from tests.test_strategies import sample_market_data


def test_regime_detector_returns_regime_output() -> None:
    features = FeatureBuilder().build(sample_market_data(rows=60))
    context = StrategyContext(symbol="NIFTY", features=features, sentiments=[])
    output = RegimeDetector(Settings()).detect(context)
    assert output.symbol == "NIFTY"
    assert 0.0 <= output.confidence <= 1.0
    assert output.regime.value
