from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class RSIReversalStrategy(BaseStrategy):
    name = "RSI Reversal"
    category = StrategyCategory.MEAN_REVERSION

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 14):
            return self._hold(context, "Insufficient candles for RSI.")
        rsi = float(context.features.iloc[-1]["rsi_14"])
        if rsi < 30:
            return self._signal(context, (30 - rsi) / 30, min(0.9, 0.45 + (30 - rsi) / 40), "RSI is oversold and mean-reversion risk/reward is improving.", {"rsi": rsi})
        if rsi > 70:
            return self._signal(context, -(rsi - 70) / 30, min(0.9, 0.45 + (rsi - 70) / 40), "RSI is overbought and reversal risk is elevated.", {"rsi": rsi})
        return self._signal(context, 0.0, 0.35, "RSI is in the neutral zone.", {"rsi": rsi})
