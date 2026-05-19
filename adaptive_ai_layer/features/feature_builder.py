from __future__ import annotations

import numpy as np
import pandas as pd

from features.anomaly_features import AnomalyFeatureBuilder
from features.correlation_features import CorrelationFeatureBuilder
from features.momentum_features import MomentumFeatureBuilder
from features.options_features import OptionsFeatureBuilder
from features.regime_features import RegimeFeatureBuilder
from features.sentiment_features import SentimentFeatureBuilder
from features.volatility_features import VolatilityFeatureBuilder
from models.schemas import FeatureBuildRequest, FeatureBuildResponse, MarketBar


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
        return frame.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    def build_response(self, request: FeatureBuildRequest) -> FeatureBuildResponse:
        frame = self.build_frame(request)
        latest_timestamp = None if frame.empty else pd.to_datetime(frame.iloc[-1]["timestamp"]).to_pydatetime()
        return FeatureBuildResponse(
            symbol=request.symbol.upper(),
            rows=len(frame.index),
            latest_timestamp=latest_timestamp,
            features=frame.tail(250).to_dict(orient="records"),
            explanation=(
                "Feature set includes volatility, momentum, rolling sentiment, options-chain pressure, "
                "sector correlation, regime indicators, and anomaly scores."
            ),
        )

    @staticmethod
    def _bars_to_frame(bars: list[MarketBar]) -> pd.DataFrame:
        if not bars:
            return pd.DataFrame()
        frame = pd.DataFrame([bar.model_dump() for bar in bars])
        frame["symbol"] = frame["symbol"].str.upper()
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        return frame.sort_values("timestamp").reset_index(drop=True)
