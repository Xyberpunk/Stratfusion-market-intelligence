from __future__ import annotations

import numpy as np
import pandas as pd

from features.anomaly_features import AnomalyFeatureBuilder
from features.correlation_features import CorrelationFeatureBuilder
from features.momentum_features import MomentumFeatureBuilder
from features.options_features import OptionsFeatureBuilder
from features.feature_quality import FeatureQualityValidator
from features.regime_features import RegimeFeatureBuilder
from features.sentiment_features import SentimentFeatureBuilder
from features.volatility_features import VolatilityFeatureBuilder
from models.schemas import FeatureBuildRequest, FeatureBuildResponse, FeatureVectorOutput, MarketBar


class AdaptiveFeatureBuilder:
    """Composes all adaptive intelligence feature groups into one dataset."""

    def __init__(self) -> None:
        self.volatility = VolatilityFeatureBuilder()
        self.momentum = MomentumFeatureBuilder()
        self.sentiment = SentimentFeatureBuilder()
        self.options = OptionsFeatureBuilder()
        self.correlation = CorrelationFeatureBuilder()
        self.regime = RegimeFeatureBuilder()
        self.anomaly = AnomalyFeatureBuilder()
        self.quality = FeatureQualityValidator()

    def build_frame(self, request: FeatureBuildRequest) -> pd.DataFrame:
        frame = self._bars_to_frame(request.market_data)
        if frame.empty:
            return frame
        frame["returns"] = frame["close"].pct_change().fillna(0.0)
        frame = self.volatility.build(frame)
        frame = self.momentum.build(frame)
        frame = self.sentiment.build(frame, request.sentiment_events)
        frame = self.options.build(frame, request.options_chain)
        frame = self.correlation.build(frame, request.benchmark_data, request.sector_data)
        frame = self.regime.build(frame)
        frame = self.anomaly.build(frame)
        frame = self._add_contract_aliases(frame)
        return frame.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    def build_response(self, request: FeatureBuildRequest) -> FeatureBuildResponse:
        frame = self.build_frame(request)
        latest_timestamp = None if frame.empty else pd.to_datetime(frame.iloc[-1]["timestamp"]).to_pydatetime()
        quality_report = self.quality.validate(request, frame)
        return FeatureBuildResponse(
            symbol=request.symbol.upper(),
            rows=len(frame.index),
            latest_timestamp=latest_timestamp,
            features=frame.tail(250).to_dict(orient="records"),
            explanation=(
                "Feature set includes volatility, momentum, rolling sentiment, options-chain pressure, "
                "sector correlation, regime indicators, and anomaly scores."
            ),
            quality_report=quality_report,
        )

    def latest_vector(self, request: FeatureBuildRequest, timeframe: str = "1m") -> FeatureVectorOutput:
        frame = self.build_frame(request)
        if frame.empty:
            raise ValueError("Cannot build feature vector without OHLCV data")
        latest = frame.iloc[-1]
        quality_report = self.quality.validate(request, frame)
        return FeatureVectorOutput(
            symbol=request.symbol.upper(),
            timestamp=pd.to_datetime(latest["timestamp"]).to_pydatetime(),
            timeframe=timeframe,
            features={
                "rsi": self._optional_float(latest.get("rsi")),
                "macd": self._optional_float(latest.get("macd")),
                "macd_signal": self._optional_float(latest.get("macd_signal")),
                "macd_histogram": self._optional_float(latest.get("macd_histogram")),
                "ema_slope": self._optional_float(latest.get("ema_slope")),
                "vwap_distance": self._optional_float(latest.get("vwap_distance")),
                "atr": self._optional_float(latest.get("atr")),
                "bollinger_width": self._optional_float(latest.get("bollinger_width")),
                "realized_volatility": self._optional_float(latest.get("realized_volatility")),
                "rolling_sentiment_mean": self._optional_float(latest.get("rolling_sentiment_mean")),
                "bullish_count": int(latest.get("bullish_count", 0)),
                "bearish_count": int(latest.get("bearish_count", 0)),
                "neutral_count": int(latest.get("neutral_count", 0)),
                "sentiment_momentum": self._optional_float(latest.get("sentiment_momentum")),
                "pcr_trend": self._optional_float(latest.get("pcr_trend")),
                "iv_spike": self._optional_float(latest.get("iv_spike")),
                "oi_imbalance": self._optional_float(latest.get("oi_imbalance")),
            },
            quality_report=quality_report,
        )

    @staticmethod
    def _bars_to_frame(bars: list[MarketBar]) -> pd.DataFrame:
        if not bars:
            return pd.DataFrame()
        frame = pd.DataFrame([bar.model_dump() for bar in bars])
        frame["symbol"] = frame["symbol"].str.upper()
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame.sort_values("timestamp").reset_index(drop=True)

    @staticmethod
    def _add_contract_aliases(frame: pd.DataFrame) -> pd.DataFrame:
        frame = frame.copy()
        frame["rsi"] = frame.get("rsi_14", 50.0)
        frame["ema_slope"] = frame.get("ema_slope_12", 0.0)
        frame["vwap_distance"] = frame.get("distance_from_vwap", 0.0)
        frame["atr"] = frame.get("atr_14", 0.0)
        frame["bollinger_width"] = frame.get("bb_width", 0.0)
        frame["realized_volatility"] = frame.get("realized_vol_20", 0.0)
        frame["bullish_count"] = frame.get("bullish_headline_count", 0).astype(int)
        frame["bearish_count"] = frame.get("bearish_headline_count", 0).astype(int)
        neutral_proxy = frame.get("sentiment_count", 0) - frame["bullish_count"] - frame["bearish_count"]
        frame["neutral_count"] = neutral_proxy.clip(lower=0).astype(int)
        oi_total = frame.get("call_oi_change", 0).abs() + frame.get("put_oi_change", 0).abs()
        frame["oi_imbalance"] = (frame.get("put_oi_change", 0) - frame.get("call_oi_change", 0)) / oi_total.replace(0, np.nan)
        return frame

    @staticmethod
    def _optional_float(value: object) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if np.isnan(numeric) or np.isinf(numeric):
            return None
        return numeric
