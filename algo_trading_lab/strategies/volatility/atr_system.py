from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class ATRSystemStrategy(BaseStrategy):
    name = "ATR Volatility System"
    category = StrategyCategory.VOLATILITY

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 15):
            return self._hold(context, "Insufficient candles for ATR system.")
        latest = context.features.iloc[-1]
        atr = float(latest.get("atr", latest.get("atr_14", 0.0)))
        close = float(latest.get("close", 0.0))
        if atr <= 0 or close <= 0:
            return self._hold(context, "ATR breakout cannot run because ATR or close is unavailable.")
        recent_high = float(context.features["high"].iloc[-15:-1].max())
        recent_low = float(context.features["low"].iloc[-15:-1].min())
        threshold = 0.35 * atr
        if close > recent_high + threshold:
            score = min(1.0, (close - recent_high) / max(atr, 1e-9))
            return self._signal(context, score, min(0.88, 0.45 + score * 0.3), "Price broke above recent high by an ATR-adjusted threshold.", {"atr": atr, "recent_high": recent_high, "threshold": threshold})
        if close < recent_low - threshold:
            score = -min(1.0, (recent_low - close) / max(atr, 1e-9))
            return self._signal(context, score, min(0.88, 0.45 + abs(score) * 0.3), "Price broke below recent low by an ATR-adjusted threshold.", {"atr": atr, "recent_low": recent_low, "threshold": threshold})
        return self._signal(context, 0.0, 0.35, "No ATR-adjusted breakout is present.", {"atr": atr, "recent_high": recent_high, "recent_low": recent_low, "threshold": threshold})
