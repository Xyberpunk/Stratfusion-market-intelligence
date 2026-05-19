from __future__ import annotations

from datetime import datetime, timedelta, timezone

from data.feature_builder import FeatureBuilder
from models.schemas import MarketDataPoint
from strategies.base import StrategyContext
from strategies.momentum.moving_average import MovingAverageCrossoverStrategy


def sample_market_data(symbol: str = "RELIANCE", rows: int = 40) -> list[MarketDataPoint]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    points: list[MarketDataPoint] = []
    price = 100.0
    for idx in range(rows):
        price += 1.0
        points.append(
            MarketDataPoint(
                symbol=symbol,
                timestamp=base + timedelta(days=idx),
                open=price - 0.5,
                high=price + 1.0,
                low=price - 1.0,
                close=price,
                volume=100000 + idx * 1000,
                source="test",
            )
        )
    return points


def test_moving_average_strategy_emits_signal() -> None:
    features = FeatureBuilder().build(sample_market_data())
    context = StrategyContext(symbol="RELIANCE", features=features, sentiments=[])
    signal = MovingAverageCrossoverStrategy().generate(context)
    assert signal.strategy_name == "Moving Average Crossover"
    assert signal.confidence >= 0.0
    assert signal.symbol == "RELIANCE"
