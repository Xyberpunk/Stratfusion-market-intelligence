from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class ATRSystemStrategy(BaseStrategy):
    name = "ATR Volatility System"
    category = StrategyCategory.VOLATILITY

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 15):
            return self._hold(context, "Insufficient candles for ATR system.")
        latest = context.features.iloc[-1]
        previous = context.features.iloc[-2]
        atr_pct = float(latest["atr_pct"])
        direction = 1 if latest["close"] > previous["close"] else -1 if latest["close"] < previous["close"] else 0
        score = max(-1.0, min(1.0, direction * min(0.7, atr_pct * 12)))
        return self._signal(context, score, min(0.8, 0.35 + atr_pct * 8), "ATR-adjusted volatility impulse is evaluated.", {"atr_pct": atr_pct, "direction": direction})
