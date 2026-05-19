from __future__ import annotations

from datetime import datetime, timezone

from models.enums import RiskLevel
from models.schemas import AnomalyEvent, SentimentInput
from strategies.base import StrategyContext


class AnomalyDetector:
    """Detects unusual volume, options, sentiment, price/news divergence, and volatility spikes."""

    def detect(self, context: StrategyContext) -> list[AnomalyEvent]:
        events: list[AnomalyEvent] = []
        timestamp = context.features.iloc[-1]["timestamp"] if not context.features.empty else datetime.now(timezone.utc)
        if not context.features.empty:
            latest = context.features.iloc[-1]
            volume_ratio = float(latest.get("volume_ratio", 1.0))
            atr_pct = float(latest.get("atr_pct", 0.0))
            return_1 = float(latest.get("returns", 0.0))
            if volume_ratio >= 2.5:
                events.append(self._event(context.symbol, timestamp, "unusual_volume", RiskLevel.MODERATE, volume_ratio, "Volume is more than 2.5x its rolling average.", {"volume_ratio": volume_ratio}))
            if atr_pct >= 0.04:
                events.append(self._event(context.symbol, timestamp, "volatility_spike", RiskLevel.HIGH, atr_pct, "ATR percentage indicates an elevated volatility spike.", {"atr_pct": atr_pct}))
            sentiment_score = self._combined_sentiment(context.sentiments)
            if abs(sentiment_score) >= 0.65 and return_1 * sentiment_score < 0:
                events.append(self._event(context.symbol, timestamp, "price_news_divergence", RiskLevel.MODERATE, abs(sentiment_score), "Price action diverges from current news sentiment.", {"return": return_1, "sentiment_score": sentiment_score}))
        if context.options_chain:
            chain = context.options_chain
            total_oi_shift = abs(chain.call_oi_change) + abs(chain.put_oi_change)
            if total_oi_shift >= 1_000_000:
                events.append(self._event(context.symbol, chain.timestamp, "unusual_options_activity", RiskLevel.MODERATE, total_oi_shift, "Options open-interest change is unusually large.", chain.model_dump()))
        return events

    @staticmethod
    def _combined_sentiment(sentiments: list[SentimentInput]) -> float:
        if not sentiments:
            return 0.0
        confidence = sum(item.confidence for item in sentiments) or 1.0
        return sum(item.sentiment_score * item.confidence for item in sentiments) / confidence

    @staticmethod
    def _event(symbol: str, timestamp, anomaly_type: str, severity: RiskLevel, score: float, explanation: str, metadata: dict[str, object]) -> AnomalyEvent:
        return AnomalyEvent(symbol=symbol.upper(), timestamp=timestamp, anomaly_type=anomaly_type, severity=severity, score=float(abs(score)), explanation=explanation, metadata=metadata)
