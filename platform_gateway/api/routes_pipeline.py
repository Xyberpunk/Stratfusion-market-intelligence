from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from clients.service_client import UpstreamServiceError
from models.schemas import UnifiedPipelineRequest, UnifiedPipelineResponse, utc_now

router = APIRouter()


@router.get("/strategies")
async def strategies(request: Request) -> list[dict[str, str]]:
    try:
        return await request.app.state.service.algo_lab.strategies()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Algo Lab unavailable: {exc}") from exc


@router.post("/pipeline/run")
async def run_pipeline(payload: UnifiedPipelineRequest, request: Request) -> UnifiedPipelineResponse:
    service = request.app.state.service
    adaptive_payload = _adaptive_payload(payload)
    try:
        sentiment_outputs = await service.adaptive_ai.finbert_batch(
            [item.model_dump(mode="json") for item in payload.sentiment_events]
        )
        enriched_sentiments = _sentiments_for_services(payload, sentiment_outputs)
        adaptive_payload["sentiment_events"] = enriched_sentiments
        regime = await service.adaptive_ai.regime_detect(adaptive_payload)
        anomalies = await service.adaptive_ai.anomaly_detect(adaptive_payload)
        weighting = await service.adaptive_ai.weighting_suggest(
            {
                "symbol": payload.symbol,
                "timestamp": utc_now().isoformat(),
                "base_weights": payload.base_weights,
                "regime": regime,
                "sentiment_score": _aggregate_sentiment_score(sentiment_outputs),
                "volatility_score": float(regime.get("features", {}).get("volatility_percentile", 0.0)),
                "anomalies": anomalies,
                "historical_performance": [],
                "risk_level": _risk_level_from_anomalies(anomalies),
            }
        )
        trading_guidance = await service.algo_lab.generate_signal(
            {
                "symbol": payload.symbol,
                "market_data": [bar.model_dump(mode="json") for bar in payload.market_data],
                "sentiments": _algo_sentiments(payload.symbol, sentiment_outputs),
                "options_chain": payload.options_chain[-1].model_dump(mode="json") if payload.options_chain else None,
                "strategy_names": payload.strategy_names,
                "custom_weights": weighting.get("weights", {}),
                "capital": payload.capital,
                "risk_per_trade": payload.risk_per_trade,
            }
        )
        latest_news = await service.news.latest(symbol=payload.symbol, limit=10)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
    return UnifiedPipelineResponse(
        symbol=payload.symbol.upper(),
        timestamp=utc_now(),
        sentiment_outputs=sentiment_outputs,
        regime=regime,
        anomalies=anomalies,
        weighting=weighting,
        trading_guidance=trading_guidance,
        latest_news=latest_news,
        explanation=(
            "Unified pipeline completed: news sentiment was processed by Adaptive AI, market regime and anomalies "
            "were detected, dynamic strategy weights were suggested, and Algo Trading Lab generated risk-aware "
            "probability guidance. AI is one input layer, not the sole decision maker."
        ),
    )


def _adaptive_payload(payload: UnifiedPipelineRequest) -> dict[str, Any]:
    return {
        "symbol": payload.symbol,
        "market_data": [bar.model_dump(mode="json") for bar in payload.market_data],
        "sentiment_events": [item.model_dump(mode="json") for item in payload.sentiment_events],
        "options_chain": [item.model_dump(mode="json") for item in payload.options_chain],
        "benchmark_data": [bar.model_dump(mode="json") for bar in payload.benchmark_data],
        "sector_data": [bar.model_dump(mode="json") for bar in payload.sector_data],
    }


def _sentiments_for_services(payload: UnifiedPipelineRequest, outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not outputs:
        return [item.model_dump(mode="json") for item in payload.sentiment_events]
    events: list[dict[str, Any]] = []
    for output in outputs:
        confidence = float(output.get("confidence", 0.0))
        sentiment = str(output.get("sentiment", "neutral"))
        score = confidence if sentiment == "bullish" else -confidence if sentiment == "bearish" else 0.0
        events.append(
            {
                "symbol": output.get("symbol") or payload.symbol,
                "timestamp": output.get("timestamp"),
                "text": output.get("text", ""),
                "sentiment": sentiment,
                "sentiment_score": score,
                "confidence": confidence,
                "source": "platform_gateway_finbert",
            }
        )
    return events


def _algo_sentiments(symbol: str, outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sentiments: list[dict[str, Any]] = []
    for output in outputs:
        confidence = float(output.get("confidence", 0.0))
        label = str(output.get("sentiment", "neutral"))
        score = confidence if label == "bullish" else -confidence if label == "bearish" else 0.0
        sentiments.append(
            {
                "symbol": output.get("symbol") or symbol,
                "timestamp": output.get("timestamp"),
                "sentiment": label,
                "sentiment_score": score,
                "source": "adaptive_ai_finbert",
                "confidence": confidence,
            }
        )
    return sentiments


def _aggregate_sentiment_score(outputs: list[dict[str, Any]]) -> float:
    if not outputs:
        return 0.0
    numerator = 0.0
    denominator = 0.0
    for output in outputs:
        confidence = float(output.get("confidence", 0.0))
        label = str(output.get("sentiment", "neutral"))
        score = confidence if label == "bullish" else -confidence if label == "bearish" else 0.0
        numerator += score * max(confidence, 0.1)
        denominator += max(confidence, 0.1)
    return max(-1.0, min(1.0, numerator / denominator if denominator else 0.0))


def _risk_level_from_anomalies(anomalies: list[dict[str, Any]]) -> str:
    severities = {str(item.get("severity", "LOW")).upper() for item in anomalies}
    if "EXTREME" in severities or "HIGH" in severities:
        return "HIGH"
    if "MODERATE" in severities:
        return "MODERATE"
    return "LOW"
