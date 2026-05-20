from __future__ import annotations

import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def module_path(name: str):
    path = str(ROOT / name)
    sys.path.insert(0, path)
    try:
        yield
    finally:
        while path in sys.path:
            sys.path.remove(path)


def purge_platform_modules() -> None:
    prefixes = (
        "config",
        "models",
        "features",
        "sentiment",
        "regime",
        "data",
        "strategies",
        "ensemble",
        "risk",
        "accuracy",
        "ai",
        "explanation",
        "custom_builder",
        "backtesting",
        "storage",
    )
    for name in list(sys.modules):
        if name in prefixes or any(name.startswith(f"{prefix}.") for prefix in prefixes):
            sys.modules.pop(name, None)


def sample_market_data(symbol: str = "INFY", rows: int = 90) -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    close = 1480.0
    data: list[dict[str, object]] = []
    for index in range(rows):
        wave = 0.8 if index % 5 else -0.25
        change = 1.2 + wave
        open_price = close
        close = close + change
        data.append(
            {
                "symbol": symbol,
                "timestamp": now - timedelta(minutes=rows - index),
                "open": round(open_price, 2),
                "high": round(max(open_price, close) + 2.0, 2),
                "low": round(min(open_price, close) - 1.8, 2),
                "close": round(close, 2),
                "volume": 180000 + index * 1500,
                "source": "local_e2e",
            }
        )
    return data


def test_real_local_intelligence_pipeline_without_fake_internal_services() -> None:
    correlation_id = "local-e2e-INFY-001"
    headline = "Infosys raises guidance after strong revenue growth and resilient deal wins"
    raw_bars = sample_market_data()
    options = {
        "symbol": "INFY",
        "timestamp": raw_bars[-1]["timestamp"],
        "pcr": 1.18,
        "max_pain": 1510.0,
        "iv": 22.4,
        "call_oi_change": 820000,
        "put_oi_change": 1180000,
        "options_volume_call": 450000,
        "options_volume_put": 610000,
    }

    with module_path("adaptive_ai_layer"):
        from config import Settings as AdaptiveSettings
        from features.feature_builder import AdaptiveFeatureBuilder
        from models.schemas import FeatureBuildRequest, MarketBar, NewsSentimentEvent, OptionsChainSnapshot, RegimeDetectionRequest
        from regime.regime_detector import RegimeDetectionEngine
        from sentiment.finbert_service import FinBERTService

        bars = [MarketBar.model_validate(item) for item in raw_bars]
        sentiment_input = NewsSentimentEvent(symbol="INFY", timestamp=raw_bars[-1]["timestamp"], text=headline, source="local_e2e")
        sentiment = FinBERTService(AdaptiveSettings(finbert_enabled=False)).batch_infer([sentiment_input])[0]
        sentiment_event = NewsSentimentEvent(
            symbol="INFY",
            timestamp=sentiment.timestamp,
            text=headline,
            sentiment=sentiment.sentiment,
            sentiment_score=sentiment.confidence,
            confidence=sentiment.confidence,
            source="local_e2e",
        )
        options_snapshot = OptionsChainSnapshot.model_validate(options)
        feature_request = FeatureBuildRequest(symbol="INFY", market_data=bars, sentiment_events=[sentiment_event], options_chain=[options_snapshot])
        feature_vector = AdaptiveFeatureBuilder().latest_vector(feature_request)
        regime = RegimeDetectionEngine(AdaptiveSettings()).detect(RegimeDetectionRequest(**feature_request.model_dump()))

    purge_platform_modules()

    with module_path("algo_trading_lab"):
        from api.app import AlgoTradingLabService
        from config import Settings as AlgoSettings
        from models.enums import TradingSignal
        from models.schemas import GenerateSignalRequest, MarketDataPoint, OptionsChainInput, SentimentInput

        service = AlgoTradingLabService(AlgoSettings(mysql_enabled=False))
        request = GenerateSignalRequest(
            symbol="INFY",
            market_data=[MarketDataPoint.model_validate(item) for item in raw_bars],
            sentiments=[
                SentimentInput(
                    symbol="INFY",
                    timestamp=sentiment.timestamp,
                    sentiment=sentiment.sentiment.value,
                    sentiment_score=sentiment.confidence,
                    source="local_e2e",
                    confidence=sentiment.confidence,
                )
            ],
            options_chain=OptionsChainInput(symbol="INFY", timestamp=options["timestamp"], pcr=1.18, max_pain=1510.0, iv=22.4, call_oi_change=820000, put_oi_change=1180000),
            capital=1_000_000,
            risk_per_trade=0.01,
        )
        result = service.generate_signal(request)
        guidance = result["guidance"]

    assert correlation_id == "local-e2e-INFY-001"
    assert feature_vector.quality_report is not None
    assert regime.regime.value in {"TRENDING", "SIDEWAYS", "HIGH_VOLATILITY"}
    assert guidance.ensemble.bullish_probability is not None
    assert guidance.ensemble.bearish_probability is not None
    assert guidance.ensemble.neutral_probability is not None
    assert guidance.final_action in {TradingSignal.BUY, TradingSignal.SELL, TradingSignal.HOLD, TradingSignal.AVOID}
    assert guidance.risk is not None
    assert guidance.ensemble.strategy_breakdown
    assert "Combined market intelligence" in guidance.final_explanation
    assert len(guidance.final_explanation) > 120
