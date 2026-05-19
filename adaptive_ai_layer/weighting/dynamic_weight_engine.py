from __future__ import annotations

from config import Settings
from models.schemas import WeightingOutput, WeightingRequest
from weighting.accuracy_based_weighting import AccuracyBasedWeighting
from weighting.ai_weight_advisor import AIWeightAdvisor
from weighting.rule_based_weighting import RuleBasedWeighting


class DynamicWeightEngine:
    """Combines rule-based, accuracy-based, confidence/risk-adjusted, and AI-assisted weighting."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.rules = RuleBasedWeighting()
        self.accuracy = AccuracyBasedWeighting()
        self.advisor = AIWeightAdvisor()

    def suggest(self, request: WeightingRequest) -> WeightingOutput:
        weights = self._cap_and_normalize(request.base_weights)
        weights = self.rules.apply(weights, request.regime)
        weights = self.accuracy.apply(weights, request.historical_performance, request.regime.regime.value)
        if request.risk_level.upper() == "HIGH":
            weights = {name: value * (1.15 if "risk" in name.lower() or "volatility" in name.lower() else 0.9) for name, value in weights.items()}
        weights = self._cap_and_normalize(weights)
        output = self.advisor.suggest(request, weights)
        capped = self._cap_and_normalize(output.weights)
        return output.model_copy(update={"weights": capped})

    def _cap_and_normalize(self, weights: dict[str, float]) -> dict[str, float]:
        capped = {name: min(max(value, 0.0), self.settings.max_strategy_weight) for name, value in weights.items()}
        total = sum(capped.values())
        if total <= 0 and capped:
            equal = 1 / len(capped)
            return {name: equal for name in capped}
        return {name: value / total for name, value in capped.items()} if total > 0 else {}
