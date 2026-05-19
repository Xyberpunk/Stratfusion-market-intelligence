from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class BollingerReversionStrategy(BaseStrategy):
    name = "Bollinger Band Reversion"
    category = StrategyCategory.MEAN_REVERSION

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 20):
            return self._hold(context, "Insufficient candles for Bollinger Bands.")
        latest = context.features.iloc[-1]
        close = float(latest["close"])
        upper = float(latest["bb_upper"])
        lower = float(latest["bb_lower"])
        mid = float(latest["bb_mid"])
        width = max(upper - lower, 1e-9)
        if close < lower:
            score = min(1.0, (lower - close) / width * 4 + 0.35)
            return self._signal(context, score, min(0.85, 0.45 + score * 0.4), "Price is below the lower Bollinger Band.", {"close": close, "lower": lower, "mid": mid})
        if close > upper:
            score = -min(1.0, (close - upper) / width * 4 + 0.35)
            return self._signal(context, score, min(0.85, 0.45 + abs(score) * 0.4), "Price is above the upper Bollinger Band.", {"close": close, "upper": upper, "mid": mid})
        return self._signal(context, 0.0, 0.3, "Price is inside Bollinger Bands.", {"close": close, "upper": upper, "lower": lower})
