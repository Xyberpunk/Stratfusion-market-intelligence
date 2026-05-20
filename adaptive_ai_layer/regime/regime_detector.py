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
        return self._detect_from_latest(request.symbol, latest, frame)

    def _detect_from_latest(self, symbol: str, latest: pd.Series, frame: pd.DataFrame) -> RegimeOutput:
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

        high_volatility = atr_percentile >= 0.85 or realized_vol >= 0.035 or (width_median > 0 and bollinger_width > width_median * 1.8)
        trending = adx >= 25 or (abs(ema_slope) >= 0.006 and abs(macd_hist) > 0)
        sideways = adx < 18 and abs(ema_slope) < 0.003 and (width_median == 0 or bollinger_width <= width_median * 1.1)

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
            explanation=f"Market classified as {regime.value} because {reason}.",
        )
