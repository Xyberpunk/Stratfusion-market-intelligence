from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class LSTMReadyStrategy(BaseStrategy):
    name = "LSTM Interface"
    category = StrategyCategory.AI_ML

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 30):
            return self._hold(context, "Insufficient candles for LSTM-ready sequence scoring.")
        sequence_momentum = float(context.features["returns"].tail(10).sum())
        volatility = float(context.features["returns"].tail(20).std(ddof=0))
        score = max(-1.0, min(1.0, sequence_momentum / max(volatility * 5, 1e-9))) * 0.35
        return self._signal(context, score, min(0.55, 0.3 + abs(score)), "LSTM-ready interface scored recent return sequence behavior.", {"sequence_momentum": sequence_momentum, "volatility": volatility})
