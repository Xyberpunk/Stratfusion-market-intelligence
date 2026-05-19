from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class SuperTrendStrategy(BaseStrategy):
    name = "SuperTrend"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 15):
            return self._hold(context, "Insufficient candles for SuperTrend.")
        direction = float(context.features.iloc[-1]["supertrend_direction"])
        score = 0.55 if direction > 0 else -0.55 if direction < 0 else 0.0
        reason = "SuperTrend direction is bullish." if score > 0 else "SuperTrend direction is bearish." if score < 0 else "SuperTrend direction is neutral."
        return self._signal(context, score, 0.62 if score else 0.3, reason, {"supertrend_direction": direction})
