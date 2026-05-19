from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class StochasticReversalStrategy(BaseStrategy):
    name = "Stochastic Reversal"
    category = StrategyCategory.MEAN_REVERSION

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 14):
            return self._hold(context, "Insufficient candles for stochastic reversal.")
        stoch = float(context.features.iloc[-1]["stoch_k"])
        if stoch < 20:
            return self._signal(context, (20 - stoch) / 20, 0.6, "Stochastic oscillator is oversold.", {"stoch_k": stoch})
        if stoch > 80:
            return self._signal(context, -(stoch - 80) / 20, 0.6, "Stochastic oscillator is overbought.", {"stoch_k": stoch})
        return self._signal(context, 0.0, 0.3, "Stochastic oscillator is neutral.", {"stoch_k": stoch})
