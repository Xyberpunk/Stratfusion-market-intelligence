from __future__ import annotations

import pandas as pd

from models.enums import AnomalySeverity
from models.schemas import AnomalyOutput


class FakeBreakoutDetector:
    """Detects failed breakout risk using breakout distance, follow-through, and volume."""

    def detect(self, symbol: str, frame: pd.DataFrame) -> list[AnomalyOutput]:
        if frame.empty:
            return []
        latest = frame.iloc[-1]
        probability = float(latest.get("fake_breakout_probability", 0.0))
        if probability < 0.5:
            return []
        return [
            AnomalyOutput(
                symbol=symbol.upper(),
                timestamp=latest["timestamp"],
                anomaly_type="fake_breakout_probability",
                severity=AnomalySeverity.MODERATE,
                score=probability,
                features={"fake_breakout_probability": probability},
                explanation="Breakout lacks confirmation from follow-through and volume.",
            )
        ]
