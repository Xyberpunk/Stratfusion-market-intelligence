from __future__ import annotations

import pandas as pd

from models.enums import MarketRegime


class LiquidityRegimeDetector:
    """Detects low-liquidity conditions from relative volume."""

    def detect(self, features: pd.DataFrame) -> tuple[MarketRegime, float, dict[str, float]]:
        if features.empty:
            return MarketRegime.NORMAL, 0.0, {}
        volume_ratio = float(features.iloc[-1].get("volume_ratio", 1.0))
        if volume_ratio < 0.45:
            return MarketRegime.LOW_LIQUIDITY, min(1.0, 1.0 - volume_ratio), {"volume_ratio": volume_ratio}
        return MarketRegime.NORMAL, min(0.7, volume_ratio / 2), {"volume_ratio": volume_ratio}
