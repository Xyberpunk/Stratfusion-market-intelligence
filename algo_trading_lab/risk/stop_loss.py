from __future__ import annotations

from models.enums import TradingSignal


class StopLossCalculator:
    """ATR-aware stop-loss calculator."""

    def calculate(self, *, entry_price: float, atr: float, action: TradingSignal, fallback_pct: float = 0.02) -> float:
        distance = max(atr * 1.5, entry_price * fallback_pct)
        if action == TradingSignal.SELL:
            return round(entry_price + distance, 2)
        return round(entry_price - distance, 2)
