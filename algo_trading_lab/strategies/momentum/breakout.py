from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class BreakoutStrategy(BaseStrategy):
    name = "Breakout"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 20):
            return self._hold(context, "Insufficient candles for 20-period breakout.")
        latest = context.features.iloc[-1]
        previous_high = context.features["high"].iloc[-21:-1].max()
        previous_low = context.features["low"].iloc[-21:-1].min()
        volume_ratio = float(latest.get("volume_ratio", 1.0))
        if latest["close"] > previous_high:
            score = min(1.0, 0.45 + 0.15 * min(volume_ratio, 3.0))
            return self._signal(context, score, min(0.9, 0.45 + 0.15 * volume_ratio), "Price closed above the 20-period range high.", {"previous_high": previous_high, "volume_ratio": volume_ratio})
        if latest["close"] < previous_low:
            score = -min(1.0, 0.45 + 0.15 * min(volume_ratio, 3.0))
            return self._signal(context, score, min(0.9, 0.45 + 0.15 * volume_ratio), "Price closed below the 20-period range low.", {"previous_low": previous_low, "volume_ratio": volume_ratio})
        return self._signal(context, 0.0, 0.35, "Price remains inside the 20-period range.", {"previous_high": previous_high, "previous_low": previous_low})
