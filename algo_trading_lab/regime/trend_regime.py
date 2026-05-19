from __future__ import annotations

import pandas as pd

from models.enums import MarketRegime


class TrendRegimeDetector:
    """Classifies directional regime from moving averages and rolling returns."""

    def detect(self, features: pd.DataFrame, panic_drawdown_pct: float) -> tuple[MarketRegime, float, dict[str, float]]:
        if len(features.index) < 5:
            return MarketRegime.NORMAL, 0.0, {}
        latest = features.iloc[-1]
        rolling_return = float(features["close"].pct_change(5).iloc[-1])
        ma_spread = (float(latest["sma_20"]) - float(latest["sma_50"])) / max(float(latest["close"]), 1e-9)
        if rolling_return <= panic_drawdown_pct:
            return MarketRegime.PANIC, min(1.0, abs(rolling_return / panic_drawdown_pct)), {"rolling_return_5": rolling_return, "ma_spread": ma_spread}
        if ma_spread > 0.01 and rolling_return > 0:
            return MarketRegime.BULLISH, min(0.95, 0.5 + abs(ma_spread) * 12), {"rolling_return_5": rolling_return, "ma_spread": ma_spread}
        if ma_spread < -0.01 and rolling_return < 0:
            return MarketRegime.BEARISH, min(0.95, 0.5 + abs(ma_spread) * 12), {"rolling_return_5": rolling_return, "ma_spread": ma_spread}
        if abs(ma_spread) > 0.006:
            return MarketRegime.TRENDING, min(0.8, 0.4 + abs(ma_spread) * 15), {"rolling_return_5": rolling_return, "ma_spread": ma_spread}
        return MarketRegime.SIDEWAYS, 0.55, {"rolling_return_5": rolling_return, "ma_spread": ma_spread}
