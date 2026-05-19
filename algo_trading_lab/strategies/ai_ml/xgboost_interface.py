from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class XGBoostReadyStrategy(BaseStrategy):
    name = "XGBoost Interface"
    category = StrategyCategory.AI_ML

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 30):
            return self._hold(context, "Insufficient candles for XGBoost-ready feature scoring.")
        latest = context.features.iloc[-1]
        feature_score = (
            0.35 * (1 if latest["sma_10"] > latest["sma_20"] else -1)
            + 0.25 * (1 if latest["macd"] > latest["macd_signal"] else -1)
            + 0.20 * (1 if latest["rsi_14"] < 65 else -1)
            + 0.20 * max(-1.0, min(1.0, float(latest["volume_ratio"]) - 1.0))
        )
        return self._signal(context, feature_score * 0.45, 0.55, "XGBoost-ready interface scored engineered market features.", {"feature_score": feature_score})
