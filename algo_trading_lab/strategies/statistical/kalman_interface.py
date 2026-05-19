from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class KalmanReadyStrategy(BaseStrategy):
    name = "Kalman Trend Interface"
    category = StrategyCategory.STATISTICAL

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 20):
            return self._hold(context, "Insufficient candles for Kalman-ready trend proxy.")
        latest = context.features.iloc[-1]
        smooth_price = float(context.features["close"].ewm(alpha=0.25, adjust=False).mean().iloc[-1])
        score = max(-1.0, min(1.0, (float(latest["close"]) - smooth_price) / max(float(latest["close"]), 1e-9) * 30))
        return self._signal(context, score, min(0.65, 0.3 + abs(score) * 0.3), "Kalman-ready interface emits a smoothed-state trend proxy.", {"smooth_price": smooth_price, "close": float(latest["close"])})
