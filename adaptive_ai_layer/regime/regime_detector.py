from __future__ import annotations

from config import Settings
from features.feature_builder import AdaptiveFeatureBuilder
from models.schemas import RegimeDetectionRequest, RegimeOutput
from regime.regime_explainer import RegimeExplainer
from regime.rule_based_regime import RuleBasedRegimeClassifier


class RegimeDetectionEngine:
    """Regime intelligence engine using transparent rules first, model interfaces second."""

    def __init__(self, settings: Settings) -> None:
        self.feature_builder = AdaptiveFeatureBuilder()
        self.rule_based = RuleBasedRegimeClassifier(settings)
        self.explainer = RegimeExplainer()

    def detect(self, request: RegimeDetectionRequest) -> RegimeOutput:
        frame = self.feature_builder.build_frame(request)
        output = self.rule_based.classify(request.symbol, frame)
        return output.model_copy(update={"explanation": self.explainer.explain(output)})
