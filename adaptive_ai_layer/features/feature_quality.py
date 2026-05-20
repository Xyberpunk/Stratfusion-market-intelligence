from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from models.schemas import FeatureBuildRequest, FeatureQualityReport

REQUIRED_FEATURES = [
    "rsi",
    "macd",
    "macd_signal",
    "macd_histogram",
    "ema_slope",
    "vwap_distance",
    "atr",
    "bollinger_width",
    "realized_volatility",
]


class FeatureQualityValidator:
    """Validates feature readiness before regime, strategy, and risk decisions."""

    def validate(self, request: FeatureBuildRequest, frame: pd.DataFrame) -> FeatureQualityReport:
        now = datetime.now(timezone.utc)
        if frame.empty:
            return FeatureQualityReport(
                symbol=request.symbol.upper(),
                timestamp=now,
                rows=0,
                missing_features=REQUIRED_FEATURES,
                stale_inputs=True,
                enough_history=False,
                quality_score=0.0,
                warnings=["No OHLCV data was provided."],
            )
        latest = frame.iloc[-1]
        latest_timestamp = pd.to_datetime(latest["timestamp"], utc=True).to_pydatetime()
        missing = [name for name in REQUIRED_FEATURES if name not in frame.columns or pd.isna(latest.get(name))]
        warnings: list[str] = []
        enough_history = len(frame.index) >= 30
        if not enough_history:
            warnings.append("Fewer than 30 candles are available.")
        stale_inputs = (now - latest_timestamp).total_seconds() > 60 * 30
        if stale_inputs:
            warnings.append("Latest candle is stale.")
        if not request.sentiment_events:
            warnings.append("Sentiment input is missing.")
        if not request.options_chain:
            warnings.append("Options-chain input is missing.")
        elif request.options_chain[-1].timestamp < latest_timestamp:
            warnings.append("Options-chain snapshot is older than the latest market candle.")
        if float(frame["volume"].tail(10).sum()) <= 0:
            warnings.append("Recent candles have zero volume.")
        if "atr" in frame and float(latest.get("atr", 0.0) or 0.0) <= 0:
            warnings.append("ATR is zero or unavailable.")
        if "realized_volatility" in frame and float(latest.get("realized_volatility", 0.0) or 0.0) <= 0:
            warnings.append("Realized volatility is zero or unavailable.")

        numeric = frame.select_dtypes(include=[np.number]).tail(5)
        nan_ratio = float(numeric.isna().sum().sum() / max(numeric.size, 1))
        score = 1.0
        if not enough_history:
            score -= 0.25
        if stale_inputs:
            score -= 0.25
        score -= min(0.25, nan_ratio)
        score -= min(0.25, len(missing) * 0.03)
        if warnings:
            score -= min(0.15, len(warnings) * 0.03)
        return FeatureQualityReport(
            symbol=request.symbol.upper(),
            timestamp=latest_timestamp,
            rows=len(frame.index),
            missing_features=missing,
            stale_inputs=stale_inputs,
            enough_history=enough_history,
            quality_score=round(max(0.0, min(1.0, score)), 4),
            warnings=warnings,
        )
