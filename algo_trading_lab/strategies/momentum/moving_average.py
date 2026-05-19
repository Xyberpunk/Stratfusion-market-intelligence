from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class MovingAverageCrossoverStrategy(BaseStrategy):
    name = "Moving Average Crossover"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 20):
            return self._hold(context, "Insufficient candles for moving-average crossover.")
        latest = context.features.iloc[-1]
        spread = (float(latest["sma_10"]) - float(latest["sma_20"])) / max(float(latest["close"]), 1e-9)
        score = max(-1.0, min(1.0, spread * 25))
        reason = "Fast average is above slow average." if score > 0.15 else "Fast average is below slow average." if score < -0.15 else "Moving averages are compressed."
        return self._signal(context, score, min(0.8, 0.35 + abs(score) * 0.5), reason, {"sma_10": float(latest["sma_10"]), "sma_20": float(latest["sma_20"])})
