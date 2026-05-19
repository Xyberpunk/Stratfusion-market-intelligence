from __future__ import annotations

from execution.mode import ExecutionMode
from execution.signal_context import UnifiedSignalContext
from execution.strategy_runner import StrategyRunner
from tests.test_strategies import sample_market_data


def test_strategy_runner_uses_same_strategy_in_backtest_mode() -> None:
    context = UnifiedSignalContext(symbol="INFY", mode=ExecutionMode.BACKTEST, market_data=sample_market_data("INFY", 50), sentiments=[])
    signals = StrategyRunner().run(context, ["Moving Average Crossover"])
    assert len(signals) == 1
    assert signals[0].strategy_name == "Moving Average Crossover"
