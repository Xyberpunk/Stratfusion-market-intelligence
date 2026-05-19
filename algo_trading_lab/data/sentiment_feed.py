from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from models.enums import SentimentLabel
from models.schemas import SentimentInput


class SentimentAggregator:
    """Aggregates news intelligence signals into symbol-level sentiment."""

    @staticmethod
    def aggregate(symbol: str, sentiments: list[SentimentInput]) -> SentimentInput:
        relevant = [item for item in sentiments if item.symbol.upper() == symbol.upper()]
        if not relevant:
            return SentimentInput(
                symbol=symbol.upper(),
                timestamp=datetime.now(timezone.utc),
                sentiment=SentimentLabel.NEUTRAL,
                sentiment_score=0.0,
                source="sentiment_aggregator",
                confidence=0.0,
            )
        weighted_score = sum(item.sentiment_score * item.confidence for item in relevant)
        confidence_sum = sum(item.confidence for item in relevant) or 1.0
        score = max(-1.0, min(1.0, weighted_score / confidence_sum))
        label = SentimentLabel.BULLISH if score > 0.15 else SentimentLabel.BEARISH if score < -0.15 else SentimentLabel.NEUTRAL
        return SentimentInput(
            symbol=symbol.upper(),
            timestamp=max(item.timestamp for item in relevant),
            sentiment=label,
            sentiment_score=score,
            source="sentiment_aggregator",
            confidence=min(1.0, confidence_sum / max(1, len(relevant))),
        )

    @staticmethod
    def by_symbol(sentiments: list[SentimentInput]) -> dict[str, SentimentInput]:
        grouped: dict[str, list[SentimentInput]] = defaultdict(list)
        for item in sentiments:
            grouped[item.symbol.upper()].append(item)
        return {symbol: SentimentAggregator.aggregate(symbol, items) for symbol, items in grouped.items()}
