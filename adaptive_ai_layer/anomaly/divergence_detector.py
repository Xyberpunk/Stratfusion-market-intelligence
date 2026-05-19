from __future__ import annotations

import pandas as pd

from models.enums import AnomalySeverity
from models.schemas import AnomalyOutput


class DivergenceDetector:
    """Detects price/news and price-volume divergences."""

    def detect(self, symbol: str, frame: pd.DataFrame) -> list[AnomalyOutput]:
        if frame.empty:
            return []
        latest = frame.iloc[-1]
        outputs: list[AnomalyOutput] = []
        sentiment_div = abs(float(latest.get("sentiment_price_divergence_score", 0.0)))
        if sentiment_div >= 0.35:
            outputs.append(
                AnomalyOutput(
                    symbol=symbol.upper(),
                    timestamp=latest["timestamp"],
                    anomaly_type="price_news_divergence",
                    severity=AnomalySeverity.MODERATE if sentiment_div < 0.65 else AnomalySeverity.HIGH,
                    score=sentiment_div,
                    features={"sentiment_price_divergence_score": sentiment_div},
                    explanation="News sentiment and recent price direction are diverging.",
                )
            )
        pv = abs(float(latest.get("price_volume_divergence", 0.0)))
        if pv >= 0.08:
            outputs.append(
                AnomalyOutput(
                    symbol=symbol.upper(),
                    timestamp=latest["timestamp"],
                    anomaly_type="price_volume_divergence",
                    severity=AnomalySeverity.MODERATE,
                    score=pv,
                    features={"price_volume_divergence": pv},
                    explanation="Recent price movement conflicts with abnormal volume behavior.",
                )
            )
        return outputs
