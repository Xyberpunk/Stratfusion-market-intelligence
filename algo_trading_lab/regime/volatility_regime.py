from __future__ import annotations

import pandas as pd

from models.enums import MarketRegime


class VolatilityRegimeDetector:
    """Classifies volatility using ATR percentage and realized returns."""

    def detect(self, features: pd.DataFrame, high_volatility_atr_pct: float) -> tuple[MarketRegime, float, dict[str, float]]:
        if features.empty:
            return MarketRegime.NORMAL, 0.0, {}
        latest = features.iloc[-1]
        atr_pct = float(latest.get("atr_pct", 0.0))
        realized_vol = float(features["returns"].tail(20).std(ddof=0))
        if atr_pct >= high_volatility_atr_pct:
            confidence = min(1.0, atr_pct / max(high_volatility_atr_pct, 1e-9))
            return MarketRegime.HIGH_VOLATILITY, confidence, {"atr_pct": atr_pct, "realized_vol": realized_vol}
        return MarketRegime.NORMAL, max(0.2, 1.0 - atr_pct / max(high_volatility_atr_pct, 1e-9)), {"atr_pct": atr_pct, "realized_vol": realized_vol}
