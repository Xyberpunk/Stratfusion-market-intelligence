from __future__ import annotations

import numpy as np
import pandas as pd


class MomentumFeatureBuilder:
    """Builds momentum, trend, oscillator, and breakout features."""

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return frame
        for window in (1, 3, 5, 10, 20):
            frame[f"return_{window}"] = frame["close"].pct_change(window)
        frame["ema_12"] = frame["close"].ewm(span=12, adjust=False).mean()
        frame["ema_26"] = frame["close"].ewm(span=26, adjust=False).mean()
        frame["ema_slope_12"] = frame["ema_12"].pct_change(5)
        frame["sma_20"] = frame["close"].rolling(20, min_periods=1).mean()
        frame["sma_50"] = frame["close"].rolling(50, min_periods=1).mean()
        frame["sma_slope_20"] = frame["sma_20"].pct_change(5)
        frame["macd"] = frame["ema_12"] - frame["ema_26"]
        frame["macd_signal"] = frame["macd"].ewm(span=9, adjust=False).mean()
        frame["macd_histogram"] = frame["macd"] - frame["macd_signal"]
        frame["rsi_14"] = self._rsi(frame["close"], 14)
        frame["adx_14"] = self._adx(frame, 14)
        frame["roc_10"] = frame["close"].pct_change(10)
        frame["vwap"] = self._vwap(frame)
        frame["distance_from_vwap"] = (frame["close"] - frame["vwap"]) / frame["vwap"].replace(0, np.nan)
        frame["distance_from_sma20"] = (frame["close"] - frame["sma_20"]) / frame["sma_20"].replace(0, np.nan)
        high_20 = frame["high"].rolling(20, min_periods=1).max()
        low_20 = frame["low"].rolling(20, min_periods=1).min()
        frame["breakout_distance"] = (frame["close"] - high_20.shift(1)) / frame["close"].replace(0, np.nan)
        frame["breakdown_distance"] = (low_20.shift(1) - frame["close"]) / frame["close"].replace(0, np.nan)
        return frame

    @staticmethod
    def _rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        return (100 - (100 / (1 + rs))).fillna(50.0)

    @staticmethod
    def _adx(frame: pd.DataFrame, period: int) -> pd.Series:
        up_move = frame["high"].diff()
        down_move = -frame["low"].diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        tr = pd.concat(
            [
                frame["high"] - frame["low"],
                (frame["high"] - frame["close"].shift(1)).abs(),
                (frame["low"] - frame["close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = tr.rolling(period, min_periods=1).mean().replace(0, np.nan)
        plus_di = 100 * pd.Series(plus_dm, index=frame.index).rolling(period, min_periods=1).mean() / atr
        minus_di = 100 * pd.Series(minus_dm, index=frame.index).rolling(period, min_periods=1).mean() / atr
        dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
        return dx.rolling(period, min_periods=1).mean().fillna(0.0)

    @staticmethod
    def _vwap(frame: pd.DataFrame) -> pd.Series:
        typical = (frame["high"] + frame["low"] + frame["close"]) / 3
        cumulative_volume = frame["volume"].replace(0, np.nan).cumsum()
        return (typical * frame["volume"]).cumsum() / cumulative_volume
