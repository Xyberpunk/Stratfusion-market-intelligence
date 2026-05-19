from __future__ import annotations

import numpy as np
import pandas as pd

from data.market_data import MarketDataNormalizer
from models.schemas import MarketDataPoint


class FeatureBuilder:
    """Builds technical features used by strategy, regime, and risk engines."""

    def build(self, points: list[MarketDataPoint]) -> pd.DataFrame:
        frame = MarketDataNormalizer.to_dataframe(points)
        if frame.empty:
            return frame
        frame["returns"] = frame["close"].pct_change().fillna(0.0)
        frame["sma_10"] = frame["close"].rolling(10, min_periods=1).mean()
        frame["sma_20"] = frame["close"].rolling(20, min_periods=1).mean()
        frame["sma_50"] = frame["close"].rolling(50, min_periods=1).mean()
        frame["ema_12"] = frame["close"].ewm(span=12, adjust=False).mean()
        frame["ema_26"] = frame["close"].ewm(span=26, adjust=False).mean()
        frame["macd"] = frame["ema_12"] - frame["ema_26"]
        frame["macd_signal"] = frame["macd"].ewm(span=9, adjust=False).mean()
        frame["rsi_14"] = self.rsi(frame["close"], 14)
        frame["atr_14"] = self.atr(frame, 14)
        frame["atr_pct"] = frame["atr_14"] / frame["close"].replace(0, np.nan)
        frame["vwap"] = self.vwap(frame)
        frame["bb_mid"] = frame["close"].rolling(20, min_periods=1).mean()
        frame["bb_std"] = frame["close"].rolling(20, min_periods=1).std(ddof=0).fillna(0.0)
        frame["bb_upper"] = frame["bb_mid"] + 2 * frame["bb_std"]
        frame["bb_lower"] = frame["bb_mid"] - 2 * frame["bb_std"]
        frame["stoch_k"] = self.stochastic_k(frame, 14)
        frame["zscore_20"] = self.zscore(frame["close"], 20)
        frame["volume_sma_20"] = frame["volume"].rolling(20, min_periods=1).mean()
        frame["volume_ratio"] = frame["volume"] / frame["volume_sma_20"].replace(0, np.nan)
        frame["donchian_high_20"] = frame["high"].rolling(20, min_periods=1).max()
        frame["donchian_low_20"] = frame["low"].rolling(20, min_periods=1).min()
        frame["supertrend_direction"] = self.supertrend_direction(frame)
        return frame.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    @staticmethod
    def rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        return (100 - (100 / (1 + rs))).fillna(50.0)

    @staticmethod
    def atr(frame: pd.DataFrame, period: int) -> pd.Series:
        previous_close = frame["close"].shift(1)
        ranges = pd.concat(
            [
                frame["high"] - frame["low"],
                (frame["high"] - previous_close).abs(),
                (frame["low"] - previous_close).abs(),
            ],
            axis=1,
        )
        return ranges.max(axis=1).rolling(period, min_periods=1).mean()

    @staticmethod
    def vwap(frame: pd.DataFrame) -> pd.Series:
        typical_price = (frame["high"] + frame["low"] + frame["close"]) / 3
        cumulative_volume = frame["volume"].replace(0, np.nan).cumsum()
        return (typical_price * frame["volume"]).cumsum() / cumulative_volume

    @staticmethod
    def stochastic_k(frame: pd.DataFrame, period: int) -> pd.Series:
        low_min = frame["low"].rolling(period, min_periods=1).min()
        high_max = frame["high"].rolling(period, min_periods=1).max()
        return 100 * (frame["close"] - low_min) / (high_max - low_min).replace(0, np.nan)

    @staticmethod
    def zscore(series: pd.Series, period: int) -> pd.Series:
        mean = series.rolling(period, min_periods=1).mean()
        std = series.rolling(period, min_periods=1).std(ddof=0)
        return (series - mean) / std.replace(0, np.nan)

    @staticmethod
    def supertrend_direction(frame: pd.DataFrame, multiplier: float = 3.0) -> pd.Series:
        atr = FeatureBuilder.atr(frame, 10)
        hl2 = (frame["high"] + frame["low"]) / 2
        upper = hl2 + multiplier * atr
        lower = hl2 - multiplier * atr
        direction = np.where(frame["close"] > upper.shift(1).fillna(upper), 1, 0)
        direction = np.where(frame["close"] < lower.shift(1).fillna(lower), -1, direction)
        return pd.Series(direction, index=frame.index).replace(0, method="ffill").fillna(0)
