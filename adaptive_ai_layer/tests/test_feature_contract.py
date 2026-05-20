from __future__ import annotations

from models.schemas import FeatureBuildRequest, NewsSentimentEvent, OptionsChainSnapshot
from features.feature_builder import AdaptiveFeatureBuilder
from tests.test_features import sample_bars


def test_latest_feature_vector_contract_contains_required_groups() -> None:
    bars = sample_bars("INFY", 80)
    vector = AdaptiveFeatureBuilder().latest_vector(
        FeatureBuildRequest(
            symbol="INFY",
            market_data=bars,
            sentiment_events=[NewsSentimentEvent(symbol="INFY", text="Infosys raises guidance", sentiment_score=0.7, confidence=0.8)],
            options_chain=[OptionsChainSnapshot(symbol="INFY", timestamp=bars[-1].timestamp, pcr=1.2, iv=22, call_oi_change=100, put_oi_change=150)],
        )
    )
    required = {
        "rsi",
        "macd",
        "macd_signal",
        "macd_histogram",
        "ema_slope",
        "vwap_distance",
        "atr",
        "bollinger_width",
        "realized_volatility",
        "rolling_sentiment_mean",
        "bullish_count",
        "bearish_count",
        "neutral_count",
        "pcr_trend",
        "iv_spike",
        "oi_imbalance",
    }
    assert required.issubset(vector.features)
