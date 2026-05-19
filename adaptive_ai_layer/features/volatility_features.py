from __future__ import annotations

import numpy as np
import pandas as pd


class VolatilityFeatureBuilder:
    """Builds volatility and range-expansion features."""

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        previous_close = frame["close"].shift(1)
        true_range = pd.concat(
            [
                frame["high"] - frame["low"],
                (frame["high"] - previous_close).abs(),
                (frame["low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        frame["atr_14"] = true_range.rolling(14, min_periods=1).mean()
        frame["realized_vol_10"] = frame["returns"].rolling(10, min_periods=2).std(ddof=0)
        frame["realized_vol_20"] = frame["returns"].rolling(20, min_periods=2).std(ddof=0)
        rolling_mid = frame["close"].rolling(20, min_periods=1).mean()
        rolling_std = frame["close"].rolling(20, min_periods=2).std(ddof=0).fillna(0.0)
        frame["bb_width"] = ((rolling_mid + 2 * rolling_std) - (rolling_mid - 2 * rolling_std)) / frame["close"].replace(0, np.nan)
        frame["volatility_percentile"] = frame["realized_vol_20"].rolling(100, min_periods=5).rank(pct=True)
        frame["volatility_regime_score"] = (frame["atr_14"] / frame["close"].replace(0, np.nan)).fillna(0.0)
        frame["high_low_range_pct"] = (frame["high"] - frame["low"]) / frame["close"].replace(0, np.nan)
        frame["range_expansion"] = frame["high_low_range_pct"] / frame["high_low_range_pct"].rolling(20, min_periods=1).mean().replace(0, np.nan)
        frame["gap_pct"] = (frame["open"] - previous_close) / previous_close.replace(0, np.nan)
        frame["gap_up"] = (frame["gap_pct"] > 0.01).astype(int)
        frame["gap_down"] = (frame["gap_pct"] < -0.01).astype(int)
        return frame
