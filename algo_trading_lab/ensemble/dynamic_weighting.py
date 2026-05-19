from __future__ import annotations

from models.schemas import AccuracyOutput, RegimeOutput, StrategySignal
from ensemble.weight_manager import WeightManager


class DynamicWeightingEngine:
    """Composes all dynamic weighting inputs into final strategy weights."""

    def __init__(self, weight_manager: WeightManager) -> None:
        self.weight_manager = weight_manager

    def weights(
        self,
        *,
        signals: list[StrategySignal],
        regime: RegimeOutput | None,
        custom_weights: dict[str, float] | None = None,
        accuracy: list[AccuracyOutput] | None = None,
    ) -> dict[str, float]:
        weights = self.weight_manager.base_weights(signals, custom_weights)
        weights = self.weight_manager.apply_regime(weights, regime)
        weights = self.weight_manager.apply_accuracy(weights, accuracy or [])
        return self.weight_manager.apply_confidence(weights, signals)
