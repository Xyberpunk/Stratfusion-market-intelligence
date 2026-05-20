from __future__ import annotations

from memory.strategy_performance_memory import StrategyOutcomeRecord, StrategyPerformanceMemoryStore


def test_strategy_performance_memory_records_and_queries() -> None:
    store = StrategyPerformanceMemoryStore()
    store.record_signal_outcome(
        StrategyOutcomeRecord(
            strategy_name="MACD Momentum",
            symbol="INFY",
            regime="TRENDING",
            signal="BUY",
            result="WIN",
            pnl=1200,
            drawdown=-200,
            volatility=0.02,
        )
    )
    assert len(store.get_strategy_performance_by_regime("MACD Momentum", "TRENDING")) == 1
    assert len(store.get_strategy_performance_by_symbol("MACD Momentum", "INFY")) == 1
    assert store.get_recent_strategy_accuracy("MACD Momentum") == 1.0
