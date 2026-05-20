from __future__ import annotations

from types import SimpleNamespace

import pytest

from api.routes_pipeline import _run_pipeline
from models.schemas import MarketBar, NewsSentimentEvent, OptionsChainSnapshot, UnifiedPipelineRequest
from orchestrator.signal_orchestrator import SignalOrchestrator


class FakeAdaptiveAI:
    async def finbert_batch(self, items):
        return [{"text": items[0]["text"], "symbol": "INFY", "sentiment": "bullish", "confidence": 0.82, "timestamp": items[0]["timestamp"], "raw_scores": {"positive": 0.82}}]

    async def feature_vector(self, payload):
        return {"symbol": "INFY", "features": {"rsi": 55, "macd_histogram": 1.2, "atr": 2.1}}

    async def regime_detect(self, payload):
        return {"symbol": "INFY", "timestamp": payload["market_data"][-1]["timestamp"], "regime": "TRENDING", "confidence": 0.8, "features": {"volatility_percentile": 0.4}, "explanation": "Market classified as TRENDING."}

    async def anomaly_detect(self, payload):
        return []

    async def weighting_suggest(self, payload):
        return {"symbol": "INFY", "timestamp": payload["timestamp"], "weights": {"MACD Momentum": 0.3, "VWAP": 0.25, "RSI Reversal": 0.15, "ATR Volatility System": 0.1, "FinBERT Sentiment": 0.2}, "reason": "Trending regime favors momentum.", "confidence": 0.8}


class FakeAlgoLab:
    async def generate_signal(self, payload):
        return {
            "guidance": {
                "ensemble": {"bullish_probability": 0.74, "bearish_probability": 0.16, "neutral_probability": 0.10, "strategy_breakdown": [{"strategy_name": "MACD Momentum"}]},
                "risk": {"approved": True, "final_action": "BUY", "risk_level": "MODERATE"},
                "final_action": "BUY",
                "final_explanation": "Combined market intelligence suggests bullish probability.",
            }
        }


class FakeNews:
    async def latest(self, symbol=None, limit=10):
        return []


@pytest.mark.asyncio
async def test_gateway_e2e_pipeline_response() -> None:
    bars = [
        MarketBar(symbol="INFY", timestamp=f"2026-05-{day:02d}T09:15:00Z", open=100 + day, high=102 + day, low=99 + day, close=101 + day, volume=100000 + day)
        for day in range(1, 35)
    ]
    payload = UnifiedPipelineRequest(
        symbol="INFY",
        market_data=bars,
        sentiment_events=[NewsSentimentEvent(symbol="INFY", text="Infosys raises guidance after strong revenue growth")],
        options_chain=[OptionsChainSnapshot(symbol="INFY", timestamp="2026-05-20T09:20:00Z", pcr=1.2, iv=22, call_oi_change=100, put_oi_change=150)],
    )
    service = SimpleNamespace(adaptive_ai=FakeAdaptiveAI(), algo_lab=FakeAlgoLab(), news=FakeNews(), orchestrator=SignalOrchestrator(kafka_enabled=False), latest_signals={})
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(service=service)))
    response = await _run_pipeline(payload, request)
    assert response.regime["regime"] == "TRENDING"
    assert response.trading_guidance["guidance"]["ensemble"]["bullish_probability"] > 0
    assert response.trading_guidance["guidance"]["risk"]
    assert response.trading_guidance["guidance"]["final_explanation"]
    assert response.trading_guidance["guidance"]["ensemble"]["strategy_breakdown"]
