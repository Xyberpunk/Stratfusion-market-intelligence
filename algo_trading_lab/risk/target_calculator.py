from __future__ import annotations

from models.enums import TradingSignal


class TargetCalculator:
    """Calculates profit target from stop distance and desired reward multiple."""

    def calculate(self, *, entry_price: float, stop_loss: float, action: TradingSignal, reward_multiple: float = 2.0) -> float:
        stop_distance = abs(entry_price - stop_loss)
        if action == TradingSignal.SELL:
            return round(entry_price - reward_multiple * stop_distance, 2)
        return round(entry_price + reward_multiple * stop_distance, 2)
