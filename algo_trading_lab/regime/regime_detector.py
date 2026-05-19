from __future__ import annotations

from datetime import datetime, timezone

from config import Settings
from models.enums import MarketRegime
from models.schemas import RegimeOutput
from regime.liquidity_regime import LiquidityRegimeDetector
from regime.trend_regime import TrendRegimeDetector
from regime.volatility_regime import VolatilityRegimeDetector
from strategies.base import StrategyContext


class RegimeDetector:
    """Combines trend, volatility, and liquidity detectors into one regime output."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.trend = TrendRegimeDetector()
        self.volatility = VolatilityRegimeDetector()
        self.liquidity = LiquidityRegimeDetector()

    def detect(self, context: StrategyContext) -> RegimeOutput:
        features = context.features
        if features.empty:
            return RegimeOutput(
                symbol=context.symbol.upper(),
                timestamp=datetime.now(timezone.utc),
                regime=MarketRegime.NORMAL,
                confidence=0.0,
                features={},
            )
        timestamp = context.features.iloc[-1]["timestamp"]
        candidates = [
            self.trend.detect(features, self.settings.panic_drawdown_pct),
            self.volatility.detect(features, self.settings.high_volatility_atr_pct),
            self.liquidity.detect(features),
        ]
        priority = {
            MarketRegime.PANIC: 100,
            MarketRegime.LOW_LIQUIDITY: 90,
            MarketRegime.HIGH_VOLATILITY: 80,
            MarketRegime.BULLISH: 70,
            MarketRegime.BEARISH: 70,
            MarketRegime.TRENDING: 60,
            MarketRegime.SIDEWAYS: 50,
            MarketRegime.NORMAL: 10,
        }
        regime, confidence, feature_map = max(candidates, key=lambda item: (priority[item[0]], item[1]))
        merged_features: dict[str, float] = {}
        for _, _, features_part in candidates:
            merged_features.update(features_part)
        merged_features["selected_confidence"] = confidence
        return RegimeOutput(
            symbol=context.symbol.upper(),
            timestamp=timestamp,
            regime=regime,
            confidence=confidence,
            features=merged_features,
        )
