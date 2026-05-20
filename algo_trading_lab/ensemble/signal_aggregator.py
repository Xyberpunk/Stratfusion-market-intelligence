from __future__ import annotations

from models.enums import ConfidenceLabel, RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, RegimeOutput, StrategyBreakdown, StrategySignal


class SignalAggregator:
    """Converts weighted strategy signals into probability-based guidance."""

    def aggregate(
        self,
        *,
        symbol: str,
        signals: list[StrategySignal],
        weights: dict[str, float],
        regime: RegimeOutput | None,
        risk_level: RiskLevel,
        explanation: str,
    ) -> EnsembleOutput:
        if not signals:
            raise ValueError("At least one strategy signal is required")
        bullish = 0.0
        bearish = 0.0
        neutral = 0.0
        breakdown: list[StrategyBreakdown] = []
        for signal in signals:
            weight = weights.get(signal.strategy_name, 0.0)
            conviction = weight * max(0.05, signal.confidence)
            if signal.signal == TradingSignal.BUY:
                bullish += conviction * (0.5 + max(signal.score, 0.0) / 2)
            elif signal.signal == TradingSignal.SELL:
                bearish += conviction * (0.5 + abs(min(signal.score, 0.0)) / 2)
            else:
                neutral += conviction
            contribution = conviction * signal.score
            breakdown.append(
                StrategyBreakdown(
                    strategy_name=signal.strategy_name,
                    signal=signal.signal,
                    raw_weight=weight,
                    adjusted_weight=weight,
                    confidence=signal.confidence,
                    score=signal.score,
                    contribution=contribution,
                    reason=signal.reason,
                )
            )
        total = bullish + bearish + neutral
        if total <= 0:
            bullish_probability = bearish_probability = 0.0
            neutral_probability = 1.0
        else:
            bullish_probability = bullish / total
            bearish_probability = bearish / total
            neutral_probability = neutral / total
        suggested_action = self._suggest_action(bullish_probability, bearish_probability)
        confidence = self._confidence_label(max(bullish_probability, bearish_probability, neutral_probability))
        timestamp = max(signal.timestamp for signal in signals)
        if regime:
            explanation = f"{explanation} Current regime is {regime.regime.value} with {regime.confidence:.0%} confidence."
        return EnsembleOutput(
            symbol=symbol.upper(),
            timestamp=timestamp,
            bullish_probability=round(bullish_probability, 4),
            bearish_probability=round(bearish_probability, 4),
            neutral_probability=round(neutral_probability, 4),
            confidence=confidence,
            suggested_action=suggested_action,
            risk_level=risk_level,
            explanation=explanation,
            strategy_breakdown=breakdown,
            regime=regime.regime.value if regime else None,
            weights_used=weights,
        )

    @staticmethod
    def _suggest_action(bullish: float, bearish: float) -> TradingSignal:
        if bullish >= 0.58 and bullish - bearish >= 0.12:
            return TradingSignal.BUY
        if bearish >= 0.58 and bearish - bullish >= 0.12:
            return TradingSignal.SELL
        return TradingSignal.HOLD

    @staticmethod
    def _confidence_label(probability: float) -> ConfidenceLabel:
        if probability >= 0.7:
            return ConfidenceLabel.HIGH
        if probability >= 0.55:
            return ConfidenceLabel.MODERATE
        return ConfidenceLabel.LOW
