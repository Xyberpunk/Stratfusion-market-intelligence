from __future__ import annotations

from datetime import datetime, timedelta, timezone

from features.feature_builder import AdaptiveFeatureBuilder
from models.enums import SentimentLabel
from models.schemas import FeatureBuildRequest, MarketBar, NewsSentimentEvent, OptionsChainSnapshot


def sample_bars(symbol: str = "INFY", rows: int = 80) -> list[MarketBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    price = 100.0
    bars: list[MarketBar] = []
    for idx in range(rows):
        price += 0.4 + (idx % 5) * 0.05
        bars.append(
            MarketBar(
                symbol=symbol,
                timestamp=base + timedelta(days=idx),
                open=price - 0.4,
                high=price + 1.0,
                low=price - 1.0,
                close=price,
                volume=100000 + idx * 1500,
                source="test",
            )
        )
    return bars


def test_feature_builder_computes_required_columns() -> None:
    request = FeatureBuildRequest(
        symbol="INFY",
        market_data=sample_bars(),
        sentiment_events=[
            NewsSentimentEvent(symbol="INFY", text="Infosys raises guidance after strong revenue growth", sentiment=SentimentLabel.BULLISH, sentiment_score=0.7, confidence=0.8)
        ],
        options_chain=[
            OptionsChainSnapshot(symbol="INFY", timestamp=sample_bars()[10].timestamp, pcr=1.2, max_pain=105, iv=22, call_oi_change=1000, put_oi_change=1500)
        ],
    )
    frame = AdaptiveFeatureBuilder().build_frame(request)
    for column in ("atr_14", "macd_histogram", "rolling_sentiment_mean", "pcr", "trend_strength", "unusual_volume_score"):
        assert column in frame.columns
    assert len(frame.index) == 80
