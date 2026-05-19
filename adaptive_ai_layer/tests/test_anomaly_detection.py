from __future__ import annotations

from config import Settings
from models.schemas import AnomalyDetectionRequest
from anomaly.anomaly_detector import AnomalyDetectionEngine
from tests.test_features import sample_bars


def test_anomaly_detection_returns_list() -> None:
    bars = sample_bars(rows=80)
    bars[-1].volume = 1000000
    outputs = AnomalyDetectionEngine(Settings()).detect(AnomalyDetectionRequest(symbol="TCS", market_data=bars))
    assert isinstance(outputs, list)
    assert all(output.explanation for output in outputs)
