from __future__ import annotations

import pandas as pd

from models.enums import SentimentLabel
from models.schemas import NewsSentimentEvent


class SentimentFeatureBuilder:
    """Builds rolling sentiment features from news events."""

    def build(self, frame: pd.DataFrame, events: list[NewsSentimentEvent]) -> pd.DataFrame:
        if frame.empty:
            return frame
        if not events:
            frame["rolling_sentiment_mean"] = 0.0
            frame["rolling_sentiment_volatility"] = 0.0
            frame["sentiment_momentum"] = 0.0
            frame["bullish_headline_count"] = 0
            frame["bearish_headline_count"] = 0
            frame["sentiment_price_divergence"] = 0.0
            frame["sentiment_shock_score"] = 0.0
            frame["sector_sentiment"] = 0.0
            return frame
        sentiment_frame = pd.DataFrame([self._event_row(event) for event in events])
        sentiment_frame["timestamp"] = pd.to_datetime(sentiment_frame["timestamp"], utc=True)
        daily = sentiment_frame.set_index("timestamp").resample("1D").agg(
            sentiment_score=("sentiment_score", "mean"),
            sentiment_count=("sentiment_score", "count"),
            bullish_count=("bullish", "sum"),
            bearish_count=("bearish", "sum"),
            sector_sentiment=("sector_score", "mean"),
        )
        frame = frame.copy()
        frame["date"] = pd.to_datetime(frame["timestamp"], utc=True).dt.floor("D")
        joined = frame.merge(daily, how="left", left_on="date", right_index=True)
        joined[["sentiment_score", "sector_sentiment"]] = joined[["sentiment_score", "sector_sentiment"]].fillna(0.0)
        joined[["sentiment_count", "bullish_count", "bearish_count"]] = joined[["sentiment_count", "bullish_count", "bearish_count"]].fillna(0)
        joined["rolling_sentiment_mean"] = joined["sentiment_score"].rolling(5, min_periods=1).mean()
        joined["rolling_sentiment_volatility"] = joined["sentiment_score"].rolling(10, min_periods=2).std(ddof=0).fillna(0.0)
        joined["sentiment_momentum"] = joined["rolling_sentiment_mean"].diff(3).fillna(0.0)
        joined["bullish_headline_count"] = joined["bullish_count"].rolling(5, min_periods=1).sum()
        joined["bearish_headline_count"] = joined["bearish_count"].rolling(5, min_periods=1).sum()
        joined["sentiment_price_divergence"] = joined["rolling_sentiment_mean"] - joined["return_5"].fillna(0.0)
        joined["sentiment_shock_score"] = joined["sentiment_score"].abs() * joined["sentiment_count"].clip(upper=10) / 10
        return joined.drop(columns=["date"])

    @staticmethod
    def _event_row(event: NewsSentimentEvent) -> dict[str, object]:
        score = event.sentiment_score
        if score is None:
            if event.sentiment == SentimentLabel.BULLISH:
                score = 0.5
            elif event.sentiment == SentimentLabel.BEARISH:
                score = -0.5
            else:
                score = 0.0
        return {
            "timestamp": event.timestamp,
            "sentiment_score": float(score),
            "bullish": 1 if score > 0.15 else 0,
            "bearish": 1 if score < -0.15 else 0,
            "sector_score": float(score) if event.sector else 0.0,
        }
