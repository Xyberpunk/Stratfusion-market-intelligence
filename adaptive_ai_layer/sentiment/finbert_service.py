from __future__ import annotations

from functools import cached_property

from config import Settings
from logger import get_logger
from models.enums import SentimentLabel
from models.schemas import FinBERTOutput, NewsSentimentEvent
from sentiment.event_extractor import FinancialEventExtractor
from sentiment.sentiment_calibrator import SentimentCalibrator


class FinBERTService:
    """Batch FinBERT inference service with lexical fallback when model loading is disabled."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.calibrator = SentimentCalibrator()
        self.extractor = FinancialEventExtractor()
        self.logger = get_logger("finbert_service", model=settings.finbert_model_name)

    @cached_property
    def classifier(self):
        if not self.settings.finbert_enabled:
            return None
        try:
            from transformers import pipeline
        except Exception as exc:
            raise RuntimeError("transformers is not installed") from exc
        self.logger.info("finbert_loading")
        return pipeline("text-classification", model=self.settings.finbert_model_name, tokenizer=self.settings.finbert_model_name, return_all_scores=True)

    def batch_infer(self, items: list[NewsSentimentEvent]) -> list[FinBERTOutput]:
        if not items:
            return []
        if self.classifier is None:
            return [self._lexical(item) for item in items]
        texts = [item.text for item in items]
        raw_batches = self.classifier(texts, batch_size=self.settings.finbert_batch_size, truncation=True)
        outputs: list[FinBERTOutput] = []
        for item, raw in zip(items, raw_batches, strict=False):
            scores = {entry["label"].lower(): float(entry["score"]) for entry in raw}
            sentiment, confidence, score = self.calibrator.calibrate(scores)
            outputs.append(
                FinBERTOutput(
                    text=item.text,
                    symbol=item.symbol,
                    sentiment=sentiment,
                    confidence=confidence,
                    raw_scores=scores,
                    event_type=self.extractor.extract(item.text),
                    timestamp=item.timestamp,
                )
            )
        return outputs

    def _lexical(self, item: NewsSentimentEvent) -> FinBERTOutput:
        text = item.text.lower()
        bullish = sum(token in text for token in ("beats", "rises", "surges", "growth", "profit", "wins", "raises", "bullish"))
        bearish = sum(token in text for token in ("falls", "cuts", "loss", "probe", "penalty", "warns", "misses", "bearish"))
        if bullish > bearish:
            sentiment = SentimentLabel.BULLISH
            confidence = min(0.75, 0.45 + 0.1 * (bullish - bearish))
        elif bearish > bullish:
            sentiment = SentimentLabel.BEARISH
            confidence = min(0.75, 0.45 + 0.1 * (bearish - bullish))
        else:
            sentiment = SentimentLabel.NEUTRAL
            confidence = 0.5
        raw_scores = {
            "positive": confidence if sentiment == SentimentLabel.BULLISH else 0.2,
            "negative": confidence if sentiment == SentimentLabel.BEARISH else 0.2,
            "neutral": confidence if sentiment == SentimentLabel.NEUTRAL else 0.2,
        }
        return FinBERTOutput(
            text=item.text,
            symbol=item.symbol,
            sentiment=sentiment,
            confidence=confidence,
            raw_scores=raw_scores,
            event_type=self.extractor.extract(item.text),
            timestamp=item.timestamp,
        )
