from __future__ import annotations

from datetime import datetime, timedelta, timezone

from config import Settings
from models.enums import RegimeLabel
from models.schemas import MarketBar, RegimeDetectionRequest
from regime.regime_detector import RegimeDetectionEngine


def _bars(kind: str, rows: int = 80) -> list[MarketBar]:
    now = datetime.now(timezone.utc)
    close = 1500.0
    out: list[MarketBar] = []
    for index in range(rows):
        if kind == "trend":
            change = 2.0
            spread = 3.0
        elif kind == "volatile":
            change = 8.0 if index % 2 == 0 else -7.0
            spread = 25.0
        else:
            change = 0.05 if index % 2 == 0 else -0.04
            spread = 1.0
        open_price = close
        close = max(10, close + change)
        out.append(
            MarketBar(
                symbol="INFY",
                timestamp=now - timedelta(minutes=rows - index),
                open=open_price,
                high=max(open_price, close) + spread,
                low=min(open_price, close) - spread,
                close=close,
                volume=150000 + index,
            )
        )
    return out


def test_regime_detects_trending_sideways_and_high_volatility() -> None:
    engine = RegimeDetectionEngine(Settings())
    assert engine.detect(RegimeDetectionRequest(symbol="INFY", market_data=_bars("trend"))).regime == RegimeLabel.TRENDING
    assert engine.detect(RegimeDetectionRequest(symbol="INFY", market_data=_bars("flat"))).regime == RegimeLabel.SIDEWAYS
    assert engine.detect(RegimeDetectionRequest(symbol="INFY", market_data=_bars("volatile"))).regime == RegimeLabel.HIGH_VOLATILITY


def test_low_feature_quality_reduces_regime_confidence() -> None:
    engine = RegimeDetectionEngine(Settings())
    good = engine.detect(RegimeDetectionRequest(symbol="INFY", market_data=_bars("trend", 80)))
    poor = engine.detect(RegimeDetectionRequest(symbol="INFY", market_data=_bars("trend", 12)))
    assert poor.quality_adjusted is True
    assert poor.confidence < good.confidence
