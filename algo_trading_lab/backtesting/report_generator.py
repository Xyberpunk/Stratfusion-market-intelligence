from __future__ import annotations

from models.schemas import BacktestResult


class ReportGenerator:
    """Generates dashboard-ready backtest summaries."""

    def summary(self, result: BacktestResult) -> dict[str, object]:
        return {
            "strategy_name": result.strategy_name,
            "symbol": result.symbol,
            "period": {"start": result.start_date, "end": result.end_date},
            "trades": result.total_trades,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "max_drawdown": result.max_drawdown,
            "average_return": result.average_return,
            "accuracy": result.accuracy,
            "metadata": result.metadata,
        }
