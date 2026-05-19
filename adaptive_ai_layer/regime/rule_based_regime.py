from __future__ import annotations

import pandas as pd

from config import Settings
from models.enums import RegimeLabel
from models.schemas import RegimeOutput


class RuleBasedRegimeClassifier:
    """Transparent initial regime classifier using engineered market features."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def classify(self, symbol: str, frame: pd.DataFrame) -> RegimeOutput:
        if frame.empty:
            raise ValueError("Cannot classify regime without features")
        latest = frame.iloc[-1]
        candidates: list[tuple[RegimeLabel, float, str]] = []
        return_5 = float(latest.get("return_5", 0.0))
        trend_strength = float(latest.get("trend_strength", 0.0))
        vol_pct = float(latest.get("volatility_percentile", 0.0))
        liquidity = float(latest.get("liquidity_score", 0.5))
        risk_on = float(latest.get("risk_on_score", 0.0))
        risk_off = float(latest.get("risk_off_score", 0.0))
        sentiment = float(latest.get("rolling_sentiment_mean", 0.0))
        if return_5 <= self.settings.panic_return_threshold:
            candidates.append((RegimeLabel.PANIC, min(1.0, abs(return_5 / self.settings.panic_return_threshold)), "sharp negative five-period return"))
        if liquidity <= self.settings.low_liquidity_volume_ratio / 3:
            candidates.append((RegimeLabel.LOW_LIQUIDITY, min(1.0, 1 - liquidity), "liquidity score is depressed"))
        if vol_pct >= self.settings.high_volatility_percentile:
            candidates.append((RegimeLabel.HIGH_VOLATILITY, min(1.0, vol_pct), "volatility percentile is elevated"))
        if trend_strength >= 0.3 and return_5 > 0 and sentiment >= -0.1:
            candidates.append((RegimeLabel.BULLISH_REGIME, min(0.95, 0.45 + trend_strength), "trend strength is high with positive returns"))
        if trend_strength >= 0.3 and return_5 < 0 and sentiment <= 0.1:
            candidates.append((RegimeLabel.BEARISH_REGIME, min(0.95, 0.45 + trend_strength), "trend strength is high with negative returns"))
        if risk_on > 0.65:
            candidates.append((RegimeLabel.RISK_ON, min(0.9, risk_on), "risk-on score is dominant"))
        if risk_off > 0.65:
            candidates.append((RegimeLabel.RISK_OFF, min(0.9, risk_off), "risk-off score is dominant"))
        if trend_strength >= 0.25:
            candidates.append((RegimeLabel.TRENDING, min(0.85, 0.35 + trend_strength), "ADX-derived trend strength is above threshold"))
        candidates.append((RegimeLabel.SIDEWAYS, max(self.settings.regime_confidence_floor, 1 - trend_strength), "trend strength is low and price action is range-like"))
        priority = {
            RegimeLabel.PANIC: 100,
            RegimeLabel.LOW_LIQUIDITY: 90,
            RegimeLabel.HIGH_VOLATILITY: 80,
            RegimeLabel.RISK_OFF: 75,
            RegimeLabel.RISK_ON: 70,
            RegimeLabel.BULLISH_REGIME: 65,
            RegimeLabel.BEARISH_REGIME: 65,
            RegimeLabel.TRENDING: 55,
            RegimeLabel.SIDEWAYS: 40,
        }
        regime, confidence, reason = max(candidates, key=lambda item: (priority[item[0]], item[1]))
        return RegimeOutput(
            symbol=symbol.upper(),
            timestamp=latest["timestamp"],
            regime=regime,
            confidence=max(self.settings.regime_confidence_floor, min(1.0, confidence)),
            features={
                "return_5": return_5,
                "trend_strength": trend_strength,
                "volatility_percentile": vol_pct,
                "liquidity_score": liquidity,
                "risk_on_score": risk_on,
                "risk_off_score": risk_off,
                "rolling_sentiment_mean": sentiment,
            },
            explanation=f"Market classified as {regime.value} because {reason}.",
        )
