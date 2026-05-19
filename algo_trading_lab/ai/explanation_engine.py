from __future__ import annotations

from collections import Counter

from models.enums import TradingSignal
from models.schemas import RegimeOutput, StrategySignal


class ExplanationEngine:
    """Builds compliant probability-based explanations without guarantee language."""

    def explain(self, signals: list[StrategySignal], regime: RegimeOutput | None) -> str:
        counts = Counter(signal.signal for signal in signals)
        buy = counts.get(TradingSignal.BUY, 0)
        sell = counts.get(TradingSignal.SELL, 0)
        hold = counts.get(TradingSignal.HOLD, 0)
        bullish_names = [signal.strategy_name for signal in signals if signal.signal == TradingSignal.BUY]
        bearish_names = [signal.strategy_name for signal in signals if signal.signal == TradingSignal.SELL]
        parts = [
            f"Combined market intelligence is based on {len(signals)} independent engines: {buy} bullish, {sell} bearish, and {hold} neutral.",
        ]
        if bullish_names:
            parts.append(f"Bullish support comes from {', '.join(bullish_names[:4])}.")
        if bearish_names:
            parts.append(f"Bearish pressure comes from {', '.join(bearish_names[:4])}.")
        if regime:
            parts.append(f"Regime-aware weighting adjusted the strategy mix for a {regime.regime.value} environment.")
        return " ".join(parts)
