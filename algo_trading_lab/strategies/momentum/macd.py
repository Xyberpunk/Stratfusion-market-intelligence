from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class MACDMomentumStrategy(BaseStrategy):
    name = "MACD Momentum"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 26):
            return self._hold(context, "Insufficient candles for MACD.")
        latest = context.features.iloc[-1]
        histogram = float(latest["macd"] - latest["macd_signal"])
        normalized = histogram / max(float(latest["close"]), 1e-9)
        score = max(-1.0, min(1.0, normalized * 80))
        reason = "MACD momentum is positive." if score > 0.15 else "MACD momentum is negative." if score < -0.15 else "MACD is near its signal line."
        return self._signal(context, score, min(0.82, 0.35 + abs(score) * 0.55), reason, {"macd": float(latest["macd"]), "macd_signal": float(latest["macd_signal"]), "histogram": histogram})
