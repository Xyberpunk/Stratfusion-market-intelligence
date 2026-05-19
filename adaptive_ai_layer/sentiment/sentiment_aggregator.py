from __future__ import annotations

from collections import defaultdict

from models.enums import SentimentLabel
from models.schemas import FinBERTOutput


class SentimentAggregator:
    """Aggregates FinBERT outputs by symbol and sector-ready groups."""

    def by_symbol(self, outputs: list[FinBERTOutput]) -> dict[str, dict[str, float | str]]:
        grouped: dict[str, list[FinBERTOutput]] = defaultdict(list)
        for output in outputs:
            if output.symbol:
                grouped[output.symbol.upper()].append(output)
        result: dict[str, dict[str, float | str]] = {}
        for symbol, items in grouped.items():
            score = sum(self._score(item) * item.confidence for item in items) / (sum(item.confidence for item in items) or 1.0)
            result[symbol] = {
                "sentiment_score": score,
                "sentiment": SentimentLabel.BULLISH.value if score > 0.15 else SentimentLabel.BEARISH.value if score < -0.15 else SentimentLabel.NEUTRAL.value,
                "confidence": min(1.0, sum(item.confidence for item in items) / len(items)),
                "count": len(items),
            }
        return result

    @staticmethod
    def _score(output: FinBERTOutput) -> float:
        if output.sentiment == SentimentLabel.BULLISH:
            return output.confidence
        if output.sentiment == SentimentLabel.BEARISH:
            return -output.confidence
        return 0.0
