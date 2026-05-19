from __future__ import annotations

import pandas as pd


class DrawdownControl:
    """Computes rolling drawdown and breach state."""

    def max_drawdown(self, close: pd.Series) -> float:
        if close.empty:
            return 0.0
        equity = close / close.iloc[0]
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        return float(drawdown.min())

    def breached(self, close: pd.Series, limit: float) -> bool:
        return abs(self.max_drawdown(close)) >= limit
