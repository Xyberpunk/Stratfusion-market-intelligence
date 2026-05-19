from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from models.enums import AnomalySeverity
from models.schemas import AnomalyOutput


class IsolationForestDetector:
    """Feature-based anomaly detector using Isolation Forest."""

    columns = [
        "unusual_volume_score",
        "sentiment_price_divergence_score",
        "options_anomaly_score",
        "volatility_shock_score",
        "liquidity_breakdown_score",
        "return_5",
    ]

    def detect(self, symbol: str, frame: pd.DataFrame) -> list[AnomalyOutput]:
        if len(frame.index) < 40:
            return []
        numeric = frame[[column for column in self.columns if column in frame.columns]].fillna(0.0)
        scaled = StandardScaler().fit_transform(numeric)
        model = IsolationForest(n_estimators=120, contamination=0.05, random_state=42)
        labels = model.fit_predict(scaled)
        scores = -model.decision_function(scaled)
        if labels[-1] != -1:
            return []
        score = float(max(scores[-1], 0.0))
        latest = frame.iloc[-1]
        return [
            AnomalyOutput(
                symbol=symbol.upper(),
                timestamp=latest["timestamp"],
                anomaly_type="isolation_forest_market_anomaly",
                severity=AnomalySeverity.HIGH if score > 0.15 else AnomalySeverity.MODERATE,
                score=score,
                features={column: float(latest.get(column, 0.0)) for column in numeric.columns},
                explanation="Isolation Forest found the latest market state unusual relative to recent engineered features.",
            )
        ]
