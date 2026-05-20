from __future__ import annotations

from datetime import datetime, timezone

from shared.data.candle_aggregator import CandleAggregator


def test_candle_aggregator_builds_1m_5m_15m() -> None:
    agg = CandleAggregator()
    base = datetime(2026, 5, 20, 9, 15, 10, tzinfo=timezone.utc)
    agg.add_tick("INFY", 1500.0, 100, base)
    agg.add_tick("INFY", 1505.0, 180, base.replace(second=40))
    agg.add_tick("INFY", 1498.0, 220, base.replace(minute=16, second=5))

    one_min = agg.build_1m("INFY")
    five_min = agg.build_5m("INFY")
    fifteen_min = agg.build_15m("INFY")

    assert len(one_min) == 2
    assert one_min[0].open == 1500.0
    assert one_min[0].high == 1505.0
    assert one_min[0].low == 1500.0
    assert one_min[0].close == 1505.0
    assert one_min[0].volume == 180
    assert len(five_min) == 1
    assert five_min[0].high == 1505.0
    assert five_min[0].low == 1498.0
    assert len(fifteen_min) == 1


def test_candle_aggregator_handles_out_of_order_ticks_without_duplicates() -> None:
    agg = CandleAggregator()
    late = datetime(2026, 5, 20, 9, 15, 50, tzinfo=timezone.utc)
    early = datetime(2026, 5, 20, 9, 15, 5, tzinfo=timezone.utc)
    agg.add_tick("INFY", 1510.0, None, late)
    agg.add_tick("INFY", 1500.0, 0, early)

    candles = agg.build_1m("INFY")
    assert len(candles) == 1
    assert candles[0].high == 1510.0
    assert candles[0].low == 1500.0
