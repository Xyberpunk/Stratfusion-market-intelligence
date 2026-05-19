from __future__ import annotations

from models.enums import RegimeLabel
from models.schemas import RegimeOutput


class RuleBasedWeighting:
    """Stable initial dynamic weighting rules by market regime."""

    def apply(self, weights: dict[str, float], regime: RegimeOutput) -> dict[str, float]:
        multipliers = {name: 1.0 for name in weights}
        for name in weights:
            lowered = name.lower()
            if regime.regime in {RegimeLabel.TRENDING, RegimeLabel.BULLISH_REGIME, RegimeLabel.RISK_ON}:
                if any(token in lowered for token in ("momentum", "breakout", "vwap", "macd")):
                    multipliers[name] *= 1.25
                if any(token in lowered for token in ("rsi", "reversion", "bollinger")):
                    multipliers[name] *= 0.8
            if regime.regime == RegimeLabel.SIDEWAYS:
                if any(token in lowered for token in ("rsi", "reversion", "bollinger")):
                    multipliers[name] *= 1.25
                if "breakout" in lowered:
                    multipliers[name] *= 0.75
            if regime.regime in {RegimeLabel.PANIC, RegimeLabel.RISK_OFF, RegimeLabel.HIGH_VOLATILITY}:
                if any(token in lowered for token in ("volatility", "atr", "sentiment", "risk")):
                    multipliers[name] *= 1.2
                if any(token in lowered for token in ("normal", "trend", "breakout")):
                    multipliers[name] *= 0.75
        return {name: weights[name] * multipliers[name] for name in weights}
