from __future__ import annotations

from backtesting.backtester import Backtester
from strategies.momentum.moving_average import MovingAverageCrossoverStrategy
from tests.test_strategies import sample_market_data


def test_backtester_runs_single_strategy() -> None:
    result = Backtester().run_single_strategy(
        strategy=MovingAverageCrossoverStrategy(),
        symbol="RELIANCE",
        market_data=sample_market_data(rows=80),
    )
    assert result.strategy_name == "Moving Average Crossover"
    assert result.total_trades >= 0
    assert 0.0 <= result.win_rate <= 1.0
