from __future__ import annotations

from data.feature_builder import FeatureBuilder
from models.enums import TradingSignal
from models.schemas import BacktestResult, MarketDataPoint
from strategies.base import BaseStrategy, StrategyContext
from backtesting.metrics import BacktestMetrics


class Backtester:
    """Runs single-strategy or externally composed strategy backtests."""

    def __init__(self, feature_builder: FeatureBuilder | None = None) -> None:
        self.feature_builder = feature_builder or FeatureBuilder()
        self.metrics = BacktestMetrics()

    def run_single_strategy(self, *, strategy: BaseStrategy, symbol: str, market_data: list[MarketDataPoint]) -> BacktestResult:
        ordered = sorted(market_data, key=lambda point: point.timestamp)
        if len(ordered) < 25:
            raise ValueError("At least 25 candles are required for backtesting")
        trade_returns: list[float] = []
        equity_curve = [1.0]
        for idx in range(20, len(ordered) - 1):
            window = ordered[: idx + 1]
            features = self.feature_builder.build(window)
            context = StrategyContext(symbol=symbol, features=features, sentiments=[], options_chain=None)
            signal = strategy.generate(context)
            next_return = (ordered[idx + 1].close - ordered[idx].close) / max(ordered[idx].close, 1e-9)
            if signal.signal == TradingSignal.BUY:
                realized = next_return
            elif signal.signal == TradingSignal.SELL:
                realized = -next_return
            else:
                continue
            trade_returns.append(realized)
            equity_curve.append(equity_curve[-1] * (1 + realized))
        win_rate = self.metrics.win_rate(trade_returns)
        return BacktestResult(
            strategy_name=strategy.name,
            symbol=symbol.upper(),
            start_date=ordered[0].timestamp,
            end_date=ordered[-1].timestamp,
            total_trades=len(trade_returns),
            win_rate=round(win_rate, 4),
            profit_factor=round(self.metrics.profit_factor(trade_returns), 4),
            max_drawdown=round(self.metrics.max_drawdown(equity_curve), 4),
            average_return=round(self.metrics.average_return(trade_returns), 6),
            accuracy=round(win_rate, 4),
            metadata=self.metrics.sharpe_ready_payload(trade_returns),
        )
