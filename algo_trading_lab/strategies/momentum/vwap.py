from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class VWAPStrategy(BaseStrategy):
    name = "VWAP"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context):
            return self._hold(context, "Insufficient candles for VWAP.")
        latest = context.features.iloc[-1]
        vwap = float(latest["vwap"])
        close = float(latest["close"])
        if vwap <= 0:
            return self._hold(context, "VWAP is unavailable due to missing volume.")
        distance = (close - vwap) / vwap
        score = max(-1.0, min(1.0, distance * 18))
        confidence = min(0.85, 0.35 + abs(score) * 0.5)
        reason = "Price is above VWAP." if score > 0.15 else "Price is below VWAP." if score < -0.15 else "Price is close to VWAP."
        return self._signal(context, score, confidence, reason, {"close": close, "vwap": vwap, "distance": distance})
