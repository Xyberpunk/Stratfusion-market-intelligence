from __future__ import annotations

from models.enums import SentimentLabel


class SentimentCalibrator:
    """Maps FinBERT labels and scores into platform sentiment labels."""

    def calibrate(self, scores: dict[str, float]) -> tuple[SentimentLabel, float, float]:
        positive = scores.get("positive", scores.get("bullish", 0.0))
        negative = scores.get("negative", scores.get("bearish", 0.0))
        neutral = scores.get("neutral", 0.0)
        if positive >= negative and positive >= neutral:
            return SentimentLabel.BULLISH, positive, positive - negative
        if negative >= positive and negative >= neutral:
            return SentimentLabel.BEARISH, negative, positive - negative
        return SentimentLabel.NEUTRAL, neutral, positive - negative
