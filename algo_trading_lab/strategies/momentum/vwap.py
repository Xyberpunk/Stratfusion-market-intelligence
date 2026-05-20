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
        vwap = float(latest.get("vwap", 0.0))
        close = float(latest["close"])
        if vwap <= 0:
            return self._hold(context, "VWAP is unavailable due to missing volume.")
        distance = (close - vwap) / vwap
        momentum = float(latest.get("return_3", latest.get("returns", 0.0)))
        if distance > 0 and momentum > 0:
            score = max(0.2, min(1.0, distance * 16 + momentum * 8))
            reason = "Price is above VWAP with positive short-term momentum."
        elif distance < 0 and momentum < 0:
            score = -max(0.2, min(1.0, abs(distance) * 16 + abs(momentum) * 8))
            reason = "Price is below VWAP with negative short-term momentum."
        else:
            score = 0.0
            reason = "VWAP and momentum are not aligned."
        confidence = min(0.85, 0.35 + abs(score) * 0.5)
        return self._signal(context, score, confidence, reason, {"close": close, "vwap": vwap, "distance": distance, "momentum": momentum})
