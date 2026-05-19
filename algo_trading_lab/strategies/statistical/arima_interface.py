from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class ARIMAReadyStrategy(BaseStrategy):
    name = "ARIMA Forecast Interface"
    category = StrategyCategory.STATISTICAL

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 30):
            return self._hold(context, "Insufficient candles for ARIMA-ready forecast proxy.")
        recent_return = float(context.features["returns"].tail(5).mean())
        volatility = float(context.features["returns"].tail(20).std(ddof=0))
        score = 0.0 if volatility == 0 else max(-1.0, min(1.0, recent_return / volatility))
        return self._signal(context, score * 0.35, min(0.55, 0.25 + abs(score) * 0.2), "ARIMA-ready interface emits a conservative return-autocorrelation proxy.", {"recent_return": recent_return, "volatility": volatility})
