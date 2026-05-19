from __future__ import annotations

import pandas as pd


class RegimeFeatureBuilder:
    """Builds interpretable regime indicator features."""

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        frame["trend_strength"] = frame["adx_14"].fillna(0.0) / 100
        frame["volatility_strength"] = frame["volatility_percentile"].fillna(0.0)
        frame["liquidity_score"] = (frame["volume"] / frame["volume"].rolling(20, min_periods=1).mean().replace(0, pd.NA)).clip(0, 3) / 3
        frame["breadth_score"] = ((frame["return_5"].fillna(0.0) > 0).astype(int).rolling(20, min_periods=1).mean())
        frame["market_stress_score"] = (
            frame["volatility_strength"].fillna(0.0) * 0.4
            + (frame["return_5"].fillna(0.0) < -0.03).astype(float) * 0.4
            + (1 - frame["liquidity_score"].fillna(0.5)) * 0.2
        )
        frame["risk_on_score"] = (
            (frame["return_20"].fillna(0.0) > 0).astype(float) * 0.35
            + (frame["trend_strength"] > 0.25).astype(float) * 0.25
            + (frame["rolling_sentiment_mean"].fillna(0.0) > 0).astype(float) * 0.2
            + (frame["volatility_strength"].fillna(0.0) < 0.7).astype(float) * 0.2
        )
        frame["risk_off_score"] = (
            (frame["return_20"].fillna(0.0) < 0).astype(float) * 0.3
            + (frame["market_stress_score"].fillna(0.0) > 0.55).astype(float) * 0.4
            + (frame["rolling_sentiment_mean"].fillna(0.0) < -0.15).astype(float) * 0.3
        )
        return frame
