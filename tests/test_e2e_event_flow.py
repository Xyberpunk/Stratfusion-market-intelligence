from __future__ import annotations

from shared.events.schemas import (
    AnomalyDetectedEvent,
    EnsembleSignalGeneratedEvent,
    FeaturesGeneratedEvent,
    FinalSignalGeneratedEvent,
    MarketOHLCVRawEvent,
    MarketOptionsRawEvent,
    NewsCleanedEvent,
    NewsRawEvent,
    RegimeDetectedEvent,
    RiskEvaluatedEvent,
    SentimentCompletedEvent,
    StrategySignalGeneratedEvent,
)


def test_e2e_event_correlation_flow() -> None:
    news = NewsRawEvent(source="test", symbol="INFY", payload={"title": "Infosys raises guidance"})
    correlation_id = news.correlation_id
    events = [
        news,
        NewsCleanedEvent(source="test", symbol="INFY", correlation_id=correlation_id, payload={"title": "Infosys raises guidance"}),
        SentimentCompletedEvent(source="adaptive_ai_layer", symbol="INFY", correlation_id=correlation_id, payload={"sentiment": "bullish"}),
        MarketOHLCVRawEvent(source="test", symbol="INFY", correlation_id=correlation_id, payload={"open": 1, "high": 2, "low": 1, "close": 2, "volume": 10}),
        MarketOptionsRawEvent(source="test", symbol="INFY", correlation_id=correlation_id, payload={"pcr": 1.2}),
        FeaturesGeneratedEvent(source="adaptive_ai_layer", symbol="INFY", correlation_id=correlation_id, payload={"features": {"rsi": 55}}),
        RegimeDetectedEvent(source="adaptive_ai_layer", symbol="INFY", correlation_id=correlation_id, payload={"regime": "TRENDING"}),
        AnomalyDetectedEvent(source="adaptive_ai_layer", symbol="INFY", correlation_id=correlation_id, payload={"anomalies": []}),
        StrategySignalGeneratedEvent(source="algo_trading_lab", symbol="INFY", correlation_id=correlation_id, payload={"signal": "BUY"}),
        EnsembleSignalGeneratedEvent(source="algo_trading_lab", symbol="INFY", correlation_id=correlation_id, payload={"bullish_probability": 0.7}),
        RiskEvaluatedEvent(source="algo_trading_lab", symbol="INFY", correlation_id=correlation_id, payload={"approved": True}),
        FinalSignalGeneratedEvent(source="platform_gateway", symbol="INFY", correlation_id=correlation_id, payload={"final_action": "BUY", "explanation": "Combined market intelligence suggests bullish probability."}),
    ]
    assert all(event.correlation_id == correlation_id for event in events)
    assert [event.event_type for event in events][-1] == "final.signal.generated"
    assert events[-1].payload["explanation"]
    assert "approved" in events[-2].payload
