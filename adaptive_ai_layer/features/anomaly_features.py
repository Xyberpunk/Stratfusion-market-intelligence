from __future__ import annotations

import pandas as pd


class AnomalyFeatureBuilder:
    """Builds feature columns used by anomaly detectors."""

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        volume_mean = frame["volume"].rolling(20, min_periods=3).mean()
        volume_std = frame["volume"].rolling(20, min_periods=3).std(ddof=0)
        frame["unusual_volume_score"] = ((frame["volume"] - volume_mean) / volume_std.replace(0, pd.NA)).fillna(0.0)
        frame["price_volume_divergence"] = frame["return_5"].fillna(0.0) * -frame["unusual_volume_score"].clip(lower=0)
        frame["sentiment_price_divergence_score"] = frame["sentiment_price_divergence"].abs().fillna(0.0)
        frame["options_anomaly_score"] = frame["unusual_oi_activity"].fillna(0.0).clip(lower=0)
        frame["volatility_shock_score"] = frame["range_expansion"].fillna(0.0).clip(lower=0)
        frame["fake_breakout_probability"] = (
            (frame["breakout_distance"].fillna(0.0) > 0).astype(float)
            * (frame["volume"] < volume_mean).astype(float)
            * (frame["return_3"].fillna(0.0) < 0).astype(float)
        )
        frame["liquidity_breakdown_score"] = (1 - frame["liquidity_score"].fillna(0.5)).clip(0, 1)
        return frame
