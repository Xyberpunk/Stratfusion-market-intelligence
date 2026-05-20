from __future__ import annotations

from collections import Counter

from models.enums import TradingSignal
from models.schemas import EnsembleOutput, RiskOutput, StrategySignal


class FinalExplanationEngine:
    """Builds non-generic explanations for final probability-based signals."""

    def explain(
        self,
        *,
        ensemble: EnsembleOutput,
        risk: RiskOutput,
        strategy_signals: list[StrategySignal],
        sentiment_score: float | None = None,
        options_summary: dict[str, float | None] | None = None,
        regime_explanation: str | None = None,
    ) -> str:
        counts = Counter(signal.signal for signal in strategy_signals)
        bullish = [signal.strategy_name for signal in strategy_signals if signal.signal == TradingSignal.BUY]
        bearish = [signal.strategy_name for signal in strategy_signals if signal.signal == TradingSignal.SELL]
        neutral = [signal.strategy_name for signal in strategy_signals if signal.signal == TradingSignal.HOLD]
        parts = [
            f"Combined market intelligence suggests {ensemble.bullish_probability:.0%} bullish probability, "
            f"{ensemble.bearish_probability:.0%} bearish probability, and {ensemble.neutral_probability:.0%} neutral probability.",
            f"The current regime is {ensemble.regime or 'unknown'}.",
        ]
        if regime_explanation:
            parts.append(regime_explanation)
        parts.append(
            f"Strategy agreement is {counts.get(TradingSignal.BUY, 0)} BUY, "
            f"{counts.get(TradingSignal.SELL, 0)} SELL, and {counts.get(TradingSignal.HOLD, 0)} HOLD."
        )
        if bullish:
            parts.append(f"Bullish support comes from {', '.join(bullish)}.")
        if bearish:
            parts.append(f"Bearish pressure comes from {', '.join(bearish)}.")
        if neutral:
            parts.append(f"Neutral or non-confirming strategies include {', '.join(neutral[:3])}.")
        if sentiment_score is not None:
            label = "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral"
            parts.append(f"News sentiment contribution is {label} with score {sentiment_score:.2f}.")
        if options_summary:
            pcr = options_summary.get("pcr")
            iv = options_summary.get("iv")
            parts.append(f"Options context includes PCR {pcr if pcr is not None else 'unavailable'} and IV {iv if iv is not None else 'unavailable'}.")
        parts.append(f"Risk engine final action is {risk.final_action}: {risk.reason}")
        return " ".join(parts)
