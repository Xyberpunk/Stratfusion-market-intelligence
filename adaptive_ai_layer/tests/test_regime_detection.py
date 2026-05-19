from __future__ import annotations

from config import Settings
from models.schemas import RegimeDetectionRequest
from regime.regime_detector import RegimeDetectionEngine
from tests.test_features import sample_bars


def test_regime_detection_returns_explained_output() -> None:
    output = RegimeDetectionEngine(Settings()).detect(RegimeDetectionRequest(symbol="NIFTY", market_data=sample_bars("NIFTY", 90)))
    assert output.symbol == "NIFTY"
    assert output.regime.value
    assert 0 <= output.confidence <= 1
    assert "Market classified" in output.explanation
