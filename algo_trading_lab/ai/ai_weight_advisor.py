from __future__ import annotations

from models.enums import MarketRegime
from models.schemas import RegimeOutput


class AIWeightAdvisor:
    """Suggests bounded strategy-family tilts as one advisory input, never as a final decision maker."""

    def suggest_family_tilts(self, regime: RegimeOutput) -> dict[str, float]:
        if regime.regime in {MarketRegime.TRENDING, MarketRegime.BULLISH, MarketRegime.BEARISH}:
            return {"momentum": 1.15, "mean_reversion": 0.9}
        if regime.regime == MarketRegime.SIDEWAYS:
            return {"mean_reversion": 1.15, "momentum": 0.9}
        if regime.regime == MarketRegime.PANIC:
            return {"volatility": 1.1, "ai_ml": 0.95, "momentum": 0.85}
        return {"all": 1.0}
