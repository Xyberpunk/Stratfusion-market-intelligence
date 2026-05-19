from __future__ import annotations

from config import Settings
from features.feature_builder import AdaptiveFeatureBuilder
from models.schemas import AnomalyDetectionRequest, AnomalyOutput
from anomaly.divergence_detector import DivergenceDetector
from anomaly.fake_breakout_detector import FakeBreakoutDetector
from anomaly.isolation_forest_detector import IsolationForestDetector
from anomaly.zscore_detector import ZScoreAnomalyDetector


class AnomalyDetectionEngine:
    """Combines z-score rules, divergence rules, fake-breakout checks, and Isolation Forest."""

    def __init__(self, settings: Settings) -> None:
        self.feature_builder = AdaptiveFeatureBuilder()
        self.zscore = ZScoreAnomalyDetector(settings)
        self.divergence = DivergenceDetector()
        self.fake_breakout = FakeBreakoutDetector()
        self.isolation_forest = IsolationForestDetector()

    def detect(self, request: AnomalyDetectionRequest) -> list[AnomalyOutput]:
        frame = self.feature_builder.build_frame(request)
        outputs: list[AnomalyOutput] = []
        for detector in (self.zscore, self.divergence, self.fake_breakout, self.isolation_forest):
            outputs.extend(detector.detect(request.symbol, frame))
        deduped: dict[str, AnomalyOutput] = {}
        for output in outputs:
            current = deduped.get(output.anomaly_type)
            if current is None or output.score > current.score:
                deduped[output.anomaly_type] = output
        return list(deduped.values())
