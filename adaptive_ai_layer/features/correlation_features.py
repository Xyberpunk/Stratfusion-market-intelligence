from __future__ import annotations

import pandas as pd

from models.schemas import MarketBar


class CorrelationFeatureBuilder:
    """Builds sector and benchmark-relative features."""

    def build(self, frame: pd.DataFrame, benchmark_data: list[MarketBar], sector_data: list[MarketBar]) -> pd.DataFrame:
        if frame.empty:
            return frame
        frame = self._merge_relative(frame, benchmark_data, "nifty")
        frame = self._merge_relative(frame, sector_data, "sector")
        frame["stock_vs_nifty_correlation"] = frame["returns"].rolling(30, min_periods=5).corr(frame.get("nifty_returns", 0.0)).fillna(0.0)
        frame["stock_vs_sector_correlation"] = frame["returns"].rolling(30, min_periods=5).corr(frame.get("sector_returns", 0.0)).fillna(0.0)
        frame["relative_strength_vs_nifty"] = frame["return_20"].fillna(0.0) - frame.get("nifty_return_20", 0.0)
        frame["sector_strength"] = frame.get("sector_return_20", 0.0)
        variance = frame.get("nifty_returns", pd.Series(0.0, index=frame.index)).rolling(60, min_periods=10).var().replace(0, pd.NA)
        covariance = frame["returns"].rolling(60, min_periods=10).cov(frame.get("nifty_returns", pd.Series(0.0, index=frame.index)))
        frame["rolling_beta"] = (covariance / variance).fillna(1.0)
        frame["correlation_breakdown"] = (frame["stock_vs_nifty_correlation"].abs() < 0.2).astype(int)
        return frame

    @staticmethod
    def _merge_relative(frame: pd.DataFrame, bars: list[MarketBar], prefix: str) -> pd.DataFrame:
        if not bars:
            frame[f"{prefix}_returns"] = 0.0
            frame[f"{prefix}_return_20"] = 0.0
            return frame
        other = pd.DataFrame([bar.model_dump() for bar in bars])
        other["timestamp"] = pd.to_datetime(other["timestamp"], utc=True)
        other = other.sort_values("timestamp")
        other[f"{prefix}_returns"] = other["close"].pct_change().fillna(0.0)
        other[f"{prefix}_return_20"] = other["close"].pct_change(20).fillna(0.0)
        other = other[["timestamp", f"{prefix}_returns", f"{prefix}_return_20"]]
        return pd.merge_asof(
            frame.sort_values("timestamp"),
            other.sort_values("timestamp"),
            on="timestamp",
            direction="backward",
        ).fillna({f"{prefix}_returns": 0.0, f"{prefix}_return_20": 0.0})
