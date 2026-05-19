from __future__ import annotations

from data.sentiment_feed import SentimentAggregator
from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class FinBERTSentimentStrategy(BaseStrategy):
    name = "FinBERT Sentiment"
    category = StrategyCategory.AI_ML

    def generate(self, context: StrategyContext) -> StrategySignal:
        aggregated = SentimentAggregator.aggregate(context.symbol, context.sentiments)
        return self._signal(
            context,
            aggregated.sentiment_score,
            aggregated.confidence,
            f"Financial-news sentiment is {aggregated.sentiment.value}.",
            aggregated.model_dump(mode="json"),
        )
