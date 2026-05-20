from __future__ import annotations

from datetime import datetime, timedelta, timezone

from features.feature_builder import AdaptiveFeatureBuilder
from models.schemas import FeatureBuildRequest, NewsSentimentEvent, OptionsChainSnapshot
from tests.test_features import sample_bars


def test_feature_quality_enough_data_scores_high() -> None:
    bars = sample_bars("INFY", 80)
    request = FeatureBuildRequest(
        symbol="INFY",
        market_data=bars,
        sentiment_events=[NewsSentimentEvent(symbol="INFY", text="Infosys raises guidance", sentiment_score=0.7, confidence=0.8)],
        options_chain=[OptionsChainSnapshot(symbol="INFY", timestamp=bars[-1].timestamp, pcr=1.1, iv=20, call_oi_change=100, put_oi_change=140)],
    )
    report = AdaptiveFeatureBuilder().latest_vector(request).quality_report
    assert report is not None
    assert report.enough_history is True
    assert report.quality_score >= 0.65


def test_feature_quality_flags_insufficient_history_missing_inputs_and_stale_data() -> None:
    old_bars = sample_bars("INFY", 12)
    stale_time = datetime.now(timezone.utc) - timedelta(days=30)
    for bar in old_bars:
        bar.timestamp = stale_time
    request = FeatureBuildRequest(symbol="INFY", market_data=old_bars)
    report = AdaptiveFeatureBuilder().build_response(request).quality_report
    assert report is not None
    assert report.enough_history is False
    assert report.stale_inputs is True
    assert report.quality_score < 0.7
    assert any("Sentiment" in warning for warning in report.warnings)
