from __future__ import annotations

from models.schemas import AccuracyOutput, BacktestResult


class AccuracyTracker:
    """Converts realized backtest performance into weighting-ready accuracy records."""

    def from_backtest(self, *, result: BacktestResult, regime: str = "unknown", timeframe: str = "1d") -> AccuracyOutput:
        return AccuracyOutput(
            strategy_name=result.strategy_name,
            symbol=result.symbol,
            regime=regime,
            timeframe=timeframe,
            accuracy=result.accuracy,
            win_rate=result.win_rate,
            avg_return=result.average_return,
            sample_size=result.total_trades,
        )
