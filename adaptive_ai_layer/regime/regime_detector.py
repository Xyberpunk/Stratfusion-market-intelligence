from __future__ import annotations

import pandas as pd

from config import Settings
from features.feature_builder import AdaptiveFeatureBuilder
from models.enums import RegimeLabel
from models.schemas import RegimeDetectionRequest, RegimeOutput


class RegimeDetectionEngine:
    """Simple deterministic regime detector for the live intelligence path."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.feature_builder = AdaptiveFeatureBuilder()

    def detect(self, request: RegimeDetectionRequest) -> RegimeOutput:
        frame = self.feature_builder.build_frame(request)
        if frame.empty:
            raise ValueError("Cannot detect regime without OHLCV data")
        latest = frame.iloc[-1]
        quality = self.feature_builder.quality.validate(request, frame)
        return self._detect_from_latest(request.symbol, latest, frame, quality.quality_score)

    def _detect_from_latest(self, symbol: str, latest: pd.Series, frame: pd.DataFrame, quality_score: float = 1.0) -> RegimeOutput:
        ema_slope = float(latest.get("ema_slope", 0.0))
        macd_hist = float(latest.get("macd_histogram", 0.0))
        adx = float(latest.get("adx_14", 0.0))
        bollinger_width = float(latest.get("bollinger_width", 0.0))
        atr = float(latest.get("atr", 0.0))
        close = max(float(latest.get("close", 0.0)), 1e-9)
        atr_pct = atr / close
        realized_vol = float(latest.get("realized_volatility", 0.0))
        width_median = float(frame["bollinger_width"].tail(40).median()) if "bollinger_width" in frame else 0.0
        atr_percentile = float((frame["atr"].rank(pct=True).iloc[-1]) if "atr" in frame and len(frame.index) > 5 else 0.0)

        high_volatility = (
            atr_percentile >= self.settings.regime_atr_high_vol_percentile
            or realized_vol >= self.settings.regime_realized_vol_high
            or atr_pct >= 0.03
            or (width_median > 0 and bollinger_width > width_median * 1.8)
        )
        sideways = (
            adx < self.settings.regime_adx_sideways
            and abs(ema_slope) < self.settings.regime_ema_slope_trend_threshold
            and (width_median == 0 or bollinger_width <= max(width_median * 1.1, self.settings.regime_bollinger_compression_threshold))
        )
        compressed = bollinger_width <= max(width_median * 1.1, self.settings.regime_bollinger_compression_threshold)
        trending = not sideways and (
            (adx >= self.settings.regime_adx_trending and not compressed)
            or (abs(ema_slope) >= self.settings.regime_ema_slope_trend_threshold and abs(macd_hist) > 0)
        )

        if high_volatility:
            confidence = min(0.95, 0.55 + max(atr_percentile - 0.75, realized_vol * 5, atr_pct * 10))
            regime = RegimeLabel.HIGH_VOLATILITY
            reason = "volatility is elevated from ATR percentile, realized volatility, or Bollinger width expansion"
        elif trending:
            confidence = min(0.9, 0.45 + min(adx / 100, 0.35) + min(abs(ema_slope) * 20, 0.2) + (0.1 if abs(macd_hist) > 0 else 0))
            regime = RegimeLabel.TRENDING
            reason = "trend strength is clear from ADX or EMA slope and MACD histogram confirmation"
        else:
            confidence = 0.72 if sideways else 0.58
            regime = RegimeLabel.SIDEWAYS
            reason = "trend strength is weak and Bollinger width is compressed or neutral"

        quality_adjusted = quality_score < 0.75
        if quality_adjusted:
            confidence = max(self.settings.regime_confidence_floor, confidence * max(quality_score, 0.35))

        features_used = {
            "adx": adx,
            "ema_slope": ema_slope,
            "macd_histogram": macd_hist,
            "atr_percentile": atr_percentile,
            "realized_volatility": realized_vol,
            "bollinger_width": bollinger_width,
        }
        return RegimeOutput(
            symbol=symbol.upper(),
            timestamp=latest["timestamp"],
            regime=regime,
            confidence=round(confidence, 4),
            features={"features_used": features_used, **features_used},
            features_used=features_used,
            quality_adjusted=quality_adjusted,
            explanation=f"Market classified as {regime.value} because {reason}." + (" Confidence was reduced due to low feature quality." if quality_adjusted else ""),
        )
