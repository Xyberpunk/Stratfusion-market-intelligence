from __future__ import annotations

from models.schemas import StrategyPerformanceRecord
from memory.performance_memory import StrategyPerformanceMemory
from tests.test_features import sample_bars


def test_performance_memory_query() -> None:
    memory = StrategyPerformanceMemory()
    memory.add(
        StrategyPerformanceRecord(
            strategy_name="MACD Momentum",
            symbol="INFY",
            regime="TRENDING",
            accuracy=0.62,
            win_rate=0.6,
            avg_return=0.01,
            max_drawdown=-0.05,
            sample_size=50,
            last_updated=sample_bars()[0].timestamp,
        )
    )
    assert len(memory.query(strategy_name="MACD Momentum")) == 1
    assert memory.best_by_regime()["TRENDING"].strategy_name == "MACD Momentum"
