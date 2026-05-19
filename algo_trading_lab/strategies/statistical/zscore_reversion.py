from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class ZScoreMeanReversionStrategy(BaseStrategy):
    name = "Z-Score Mean Reversion"
    category = StrategyCategory.STATISTICAL

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 20):
            return self._hold(context, "Insufficient candles for z-score reversion.")
        zscore = float(context.features.iloc[-1]["zscore_20"])
        if zscore < -1.5:
            return self._signal(context, min(1.0, abs(zscore) / 3), 0.65, "Price is statistically below its rolling mean.", {"zscore": zscore})
        if zscore > 1.5:
            return self._signal(context, -min(1.0, abs(zscore) / 3), 0.65, "Price is statistically above its rolling mean.", {"zscore": zscore})
        return self._signal(context, 0.0, 0.3, "Z-score is inside the neutral band.", {"zscore": zscore})
