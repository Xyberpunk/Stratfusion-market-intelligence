from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureDefinition(BaseModel):
    feature_name: str
    description: str
    owner: str = "adaptive_ai_layer"
    version: str = "1.0"
    dtype: str = "float"
    active: bool = True


DEFAULT_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(feature_name="atr_14", description="14-period average true range"),
    FeatureDefinition(feature_name="realized_vol_20", description="20-period realized volatility"),
    FeatureDefinition(feature_name="macd_histogram", description="MACD minus signal line"),
    FeatureDefinition(feature_name="rsi_14", description="14-period relative strength index"),
    FeatureDefinition(feature_name="rolling_sentiment_mean", description="Rolling mean of symbol-level news sentiment"),
    FeatureDefinition(feature_name="pcr", description="Options put-call ratio"),
    FeatureDefinition(feature_name="trend_strength", description="ADX-normalized trend strength"),
    FeatureDefinition(feature_name="market_stress_score", description="Composite stress score"),
)
