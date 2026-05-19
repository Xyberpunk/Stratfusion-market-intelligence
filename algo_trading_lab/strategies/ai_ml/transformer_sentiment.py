from __future__ import annotations

from data.sentiment_feed import SentimentAggregator
from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class TransformerSentimentStrategy(BaseStrategy):
    name = "Transformer Sentiment"
    category = StrategyCategory.AI_ML

    def generate(self, context: StrategyContext) -> StrategySignal:
        aggregated = SentimentAggregator.aggregate(context.symbol, context.sentiments)
        adjusted_score = max(-1.0, min(1.0, aggregated.sentiment_score * 0.9))
        return self._signal(
            context,
            adjusted_score,
            aggregated.confidence * 0.9,
            f"Transformer sentiment layer reports {aggregated.sentiment.value} bias.",
            aggregated.model_dump(mode="json"),
        )
