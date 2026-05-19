from __future__ import annotations

from ai.explanation_engine import ExplanationEngine
from ensemble.dynamic_weighting import DynamicWeightingEngine
from ensemble.signal_aggregator import SignalAggregator
from models.enums import RiskLevel
from models.schemas import AccuracyOutput, EnsembleOutput, RegimeOutput, StrategySignal


class EnsembleEngine:
    """Combines independent strategy signals into probability-based trading intelligence."""

    def __init__(self, dynamic_weighting: DynamicWeightingEngine, explanation_engine: ExplanationEngine) -> None:
        self.dynamic_weighting = dynamic_weighting
        self.explanation_engine = explanation_engine
        self.aggregator = SignalAggregator()

    def run(
        self,
        *,
        symbol: str,
        signals: list[StrategySignal],
        regime: RegimeOutput | None,
        custom_weights: dict[str, float] | None = None,
        accuracy: list[AccuracyOutput] | None = None,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> EnsembleOutput:
        weights = self.dynamic_weighting.weights(
            signals=signals,
            regime=regime,
            custom_weights=custom_weights,
            accuracy=accuracy,
        )
        explanation = self.explanation_engine.explain(signals, regime)
        return self.aggregator.aggregate(
            symbol=symbol,
            signals=signals,
            weights=weights,
            regime=regime,
            risk_level=risk_level,
            explanation=explanation,
        )
