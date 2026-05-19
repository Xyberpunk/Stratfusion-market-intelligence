from __future__ import annotations

from models.schemas import RegimeOutput


class RegimeExplainer:
    """Creates human-readable explanations for regime outputs."""

    def explain(self, output: RegimeOutput) -> str:
        features = output.features
        return (
            f"Market classified as {output.regime.value} with {output.confidence:.0%} confidence because "
            f"trend strength is {features.get('trend_strength', 0):.2f}, volatility percentile is "
            f"{features.get('volatility_percentile', 0):.2f}, liquidity score is "
            f"{features.get('liquidity_score', 0):.2f}, and rolling sentiment is "
            f"{features.get('rolling_sentiment_mean', 0):.2f}."
        )
