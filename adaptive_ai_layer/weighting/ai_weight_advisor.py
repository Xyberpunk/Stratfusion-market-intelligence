from __future__ import annotations

from models.enums import AnomalySeverity, RegimeLabel
from models.schemas import WeightingOutput, WeightingRequest


class AIWeightAdvisor:
    """Transparent AI-assisted weighting advisor using regime, sentiment, volatility, anomalies, and memory."""

    def suggest(self, request: WeightingRequest, weights: dict[str, float]) -> WeightingOutput:
        adjusted = dict(weights)
        reasons: list[str] = []
        if request.regime.regime in {RegimeLabel.TRENDING, RegimeLabel.BULLISH_REGIME} and request.sentiment_score > 0.1 and request.volatility_score < 0.75:
            adjusted = self._tilt(adjusted, ("momentum", "breakout", "vwap", "macd"), 1.15)
            reasons.append("momentum strategies increased because regime is trending, sentiment is supportive, and volatility is not extreme")
        if request.regime.regime == RegimeLabel.SIDEWAYS:
            adjusted = self._tilt(adjusted, ("rsi", "reversion", "bollinger"), 1.15)
            reasons.append("mean-reversion strategies increased because market is classified as sideways")
        if request.regime.regime in {RegimeLabel.PANIC, RegimeLabel.RISK_OFF} or any(item.severity in {AnomalySeverity.HIGH, AnomalySeverity.EXTREME} for item in request.anomalies):
            adjusted = self._tilt(adjusted, ("risk", "volatility", "atr", "sentiment"), 1.2)
            adjusted = self._tilt(adjusted, ("breakout", "momentum"), 0.75)
            reasons.append("risk-control and volatility-aware strategies increased because stress or high-severity anomalies are present")
        confidence = min(0.9, 0.45 + request.regime.confidence * 0.35 + min(abs(request.sentiment_score), 0.5) * 0.2)
        return WeightingOutput(
            symbol=request.symbol.upper(),
            timestamp=request.timestamp,
            weights=self._normalize(adjusted),
            reason=". ".join(reasons) or "Weights preserved because no strong adaptive adjustment condition was triggered.",
            confidence=confidence,
        )

    @staticmethod
    def _tilt(weights: dict[str, float], tokens: tuple[str, ...], multiplier: float) -> dict[str, float]:
        return {name: value * multiplier if any(token in name.lower() for token in tokens) else value for name, value in weights.items()}

    @staticmethod
    def _normalize(weights: dict[str, float]) -> dict[str, float]:
        total = sum(max(value, 0.0) for value in weights.values())
        if total <= 0:
            equal = 1 / len(weights) if weights else 0.0
            return {name: equal for name in weights}
        return {name: max(value, 0.0) / total for name, value in weights.items()}
