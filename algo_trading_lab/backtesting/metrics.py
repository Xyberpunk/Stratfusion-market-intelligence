from __future__ import annotations

import numpy as np


class BacktestMetrics:
    """Calculates trading performance metrics."""

    @staticmethod
    def win_rate(returns: list[float]) -> float:
        if not returns:
            return 0.0
        wins = sum(1 for value in returns if value > 0)
        return wins / len(returns)

    @staticmethod
    def profit_factor(returns: list[float]) -> float:
        gains = sum(value for value in returns if value > 0)
        losses = abs(sum(value for value in returns if value < 0))
        if losses == 0:
            return float("inf") if gains > 0 else 0.0
        return gains / losses

    @staticmethod
    def max_drawdown(equity_curve: list[float]) -> float:
        if not equity_curve:
            return 0.0
        equity = np.array(equity_curve, dtype=float)
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak
        return float(drawdown.min())

    @staticmethod
    def average_return(returns: list[float]) -> float:
        if not returns:
            return 0.0
        return float(np.mean(returns))

    @staticmethod
    def sharpe_ready_payload(returns: list[float]) -> dict[str, float]:
        if not returns:
            return {"mean_return": 0.0, "return_std": 0.0}
        return {"mean_return": float(np.mean(returns)), "return_std": float(np.std(returns))}
