from __future__ import annotations

import pandas as pd

from models.enums import DirectionalTarget, RegimeLabel, StrategyCategory


class TargetEngineer:
    """Creates directional, regime, and strategy-suitability targets."""

    def directional(self, frame: pd.DataFrame, horizon: int, threshold: float = 0.005) -> pd.Series:
        future_return = frame["close"].shift(-horizon) / frame["close"] - 1
        return future_return.apply(
            lambda value: DirectionalTarget.UP.value
            if value > threshold
            else DirectionalTarget.DOWN.value
            if value < -threshold
            else DirectionalTarget.SIDEWAYS.value
        )

    def regime(self, frame: pd.DataFrame) -> pd.Series:
        def classify(row: pd.Series) -> str:
            if row.get("return_5", 0.0) <= -0.04:
                return RegimeLabel.PANIC.value
            if row.get("volatility_percentile", 0.0) >= 0.8:
                return RegimeLabel.HIGH_VOLATILITY.value
            if row.get("liquidity_score", 0.5) <= 0.25:
                return RegimeLabel.LOW_LIQUIDITY.value
            if row.get("trend_strength", 0.0) >= 0.3 and row.get("return_20", 0.0) > 0:
                return RegimeLabel.BULLISH_REGIME.value
            if row.get("trend_strength", 0.0) >= 0.3 and row.get("return_20", 0.0) < 0:
                return RegimeLabel.BEARISH_REGIME.value
            if row.get("trend_strength", 0.0) >= 0.25:
                return RegimeLabel.TRENDING.value
            return RegimeLabel.SIDEWAYS.value

        return frame.apply(classify, axis=1)

    def strategy_suitability(self, frame: pd.DataFrame) -> pd.Series:
        def classify(row: pd.Series) -> str:
            if row.get("market_stress_score", 0.0) > 0.65:
                return StrategyCategory.RISK_OFF.value
            if row.get("volatility_percentile", 0.0) > 0.75:
                return StrategyCategory.VOLATILITY.value
            if row.get("trend_strength", 0.0) > 0.3:
                return StrategyCategory.MOMENTUM.value
            if abs(row.get("zscore", 0.0)) > 1.2 or row.get("trend_strength", 0.0) < 0.2:
                return StrategyCategory.MEAN_REVERSION.value
            if abs(row.get("rolling_sentiment_mean", 0.0)) > 0.25:
                return StrategyCategory.SENTIMENT.value
            return StrategyCategory.MOMENTUM.value

        frame = frame.copy()
        rolling_mean = frame["close"].rolling(20, min_periods=2).mean()
        rolling_std = frame["close"].rolling(20, min_periods=2).std(ddof=0)
        frame["zscore"] = (frame["close"] - rolling_mean) / rolling_std.replace(0, pd.NA)
        return frame.apply(classify, axis=1)
