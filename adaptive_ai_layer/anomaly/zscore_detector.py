from __future__ import annotations

import pandas as pd

from config import Settings
from models.enums import AnomalySeverity
from models.schemas import AnomalyOutput


class ZScoreAnomalyDetector:
    """Detects z-score and percentile anomalies from engineered features."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def detect(self, symbol: str, frame: pd.DataFrame) -> list[AnomalyOutput]:
        if frame.empty:
            return []
        latest = frame.iloc[-1]
        timestamp = latest["timestamp"]
        outputs: list[AnomalyOutput] = []
        volume_z = abs(float(latest.get("unusual_volume_score", 0.0)))
        if volume_z >= self.settings.anomaly_zscore_threshold:
            outputs.append(self._output(symbol, timestamp, "unusual_volume", volume_z, {"volume_zscore": volume_z}, "Volume is unusually far from its rolling baseline."))
        shock = float(latest.get("volatility_shock_score", 0.0))
        if shock >= 2.5:
            outputs.append(self._output(symbol, timestamp, "volatility_shock", shock, {"volatility_shock_score": shock}, "High-low range expansion indicates a volatility shock."))
        oi = float(latest.get("options_anomaly_score", 0.0))
        if oi >= 2.5:
            outputs.append(self._output(symbol, timestamp, "options_anomaly", oi, {"options_anomaly_score": oi}, "Options open-interest activity is unusually elevated."))
        liquidity = float(latest.get("liquidity_breakdown_score", 0.0))
        if liquidity >= 0.75:
            outputs.append(self._output(symbol, timestamp, "liquidity_breakdown", liquidity, {"liquidity_breakdown_score": liquidity}, "Liquidity score is materially below its normal range."))
        return outputs

    @staticmethod
    def _output(symbol: str, timestamp, anomaly_type: str, score: float, features: dict[str, float], explanation: str) -> AnomalyOutput:
        severity = AnomalySeverity.EXTREME if score >= 5 else AnomalySeverity.HIGH if score >= 3 else AnomalySeverity.MODERATE
        return AnomalyOutput(symbol=symbol.upper(), timestamp=timestamp, anomaly_type=anomaly_type, severity=severity, score=float(score), features=features, explanation=explanation)
