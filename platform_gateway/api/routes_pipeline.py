from __future__ import annotations

import math
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from clients.service_client import UpstreamServiceError
from models.schemas import UnifiedPipelineRequest, UnifiedPipelineResponse, utc_now
from orchestrator.pipeline_state import SignalLifecycleState

router = APIRouter()


@router.get("/strategies")
async def strategies(request: Request) -> list[dict[str, str]]:
    try:
        return await request.app.state.service.algo_lab.strategies()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Algo Lab unavailable: {exc}") from exc


@router.post("/pipeline/run")
async def run_pipeline(payload: UnifiedPipelineRequest, request: Request) -> UnifiedPipelineResponse:
    return await _run_pipeline(payload, request)


@router.post("/api/pipeline/run")
async def run_api_pipeline(payload: UnifiedPipelineRequest, request: Request) -> UnifiedPipelineResponse:
    return await _run_pipeline(payload, request)


async def _run_pipeline(payload: UnifiedPipelineRequest, request: Request) -> UnifiedPipelineResponse:
    service = request.app.state.service
    pipeline_state = service.orchestrator.create_pipeline(payload)
    correlation_id = pipeline_state.correlation_id
    adaptive_payload = _adaptive_payload(payload)
    try:
        service.orchestrator.record_state(
            correlation_id,
            SignalLifecycleState.DATA_COLLECTED,
            "pipeline.data_collected",
            {"market_rows": len(payload.market_data), "sentiment_rows": len(payload.sentiment_events)},
        )
        sentiment_outputs = await service.adaptive_ai.finbert_batch(
            [item.model_dump(mode="json") for item in payload.sentiment_events]
        )
        service.news.record_dashboard_headlines(
            [item.model_dump(mode="json") for item in payload.sentiment_events],
            sentiment_outputs,
        )
        enriched_sentiments = _sentiments_for_services(payload, sentiment_outputs)
        adaptive_payload["sentiment_events"] = enriched_sentiments
        feature_vector = await service.adaptive_ai.feature_vector(adaptive_payload)
        service.orchestrator.record_state(correlation_id, SignalLifecycleState.FEATURES_READY, "features.generated", {"source": "adaptive_ai_layer", "features": feature_vector.get("features", {})})
        regime = await service.adaptive_ai.regime_detect(adaptive_payload)
        service.orchestrator.record_state(correlation_id, SignalLifecycleState.REGIME_READY, "regime.detected", {"regime": regime.get("regime")})
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
        service.orchestrator.record_state(correlation_id, SignalLifecycleState.STRATEGIES_READY, "strategy.weights.ready", {"weights": weighting.get("weights", {})})
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
        service.orchestrator.record_state(correlation_id, SignalLifecycleState.ENSEMBLE_READY, "ensemble.signal.generated", {"source": "algo_trading_lab"})
        service.orchestrator.record_state(correlation_id, SignalLifecycleState.RISK_READY, "risk.evaluated", {"source": "algo_trading_lab"})
        latest_news = await service.news.latest(symbol=payload.symbol, limit=10)
    except UpstreamServiceError as exc:
        service.orchestrator.fail(correlation_id, str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        service.orchestrator.fail(correlation_id, str(exc))
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
    response = UnifiedPipelineResponse(
        symbol=payload.symbol.upper(),
        timestamp=utc_now(),
        sentiment_outputs=sentiment_outputs,
        feature_vector=feature_vector,
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
    await service.orchestrator.finalize(correlation_id, response)
    service.latest_signals[payload.symbol.upper()] = response
    return response


@router.get("/api/overview")
async def api_overview(request: Request) -> dict[str, object]:
    status = await request.app.state.service.news.status()
    return {
        "platform": "StratFusion Market Intelligence",
        "modules": ["scraper_engine", "adaptive_ai_layer", "algo_trading_lab", "platform_gateway", "dashboard_web"],
        "news_store": status,
        "external_api_layer": "platform_gateway",
    }


@router.get("/api/symbol/{symbol}/snapshot")
async def symbol_snapshot(symbol: str, request: Request) -> dict[str, object]:
    news = await request.app.state.service.news.latest(symbol=symbol, limit=10)
    latest = request.app.state.service.latest_signals.get(symbol.upper())
    return {"symbol": symbol.upper(), "latest_news": news, "latest_signal": latest, "timestamp": utc_now()}


@router.get("/api/symbol/{symbol}/signal")
async def symbol_signal(symbol: str, request: Request) -> dict[str, object]:
    latest = request.app.state.service.latest_signals.get(symbol.upper())
    return {"symbol": symbol.upper(), "signal": latest.trading_guidance if latest else None, "status": "ready" if latest else "no signal yet"}


@router.get("/api/symbol/{symbol}/regime")
async def symbol_regime(symbol: str, request: Request) -> dict[str, object]:
    latest = request.app.state.service.latest_signals.get(symbol.upper())
    return {"symbol": symbol.upper(), "regime": latest.regime if latest else None}


@router.get("/api/symbol/{symbol}/risk")
async def symbol_risk(symbol: str, request: Request) -> dict[str, object]:
    latest = request.app.state.service.latest_signals.get(symbol.upper())
    risk = None
    if latest:
        guidance = latest.trading_guidance.get("guidance", latest.trading_guidance)
        risk = guidance.get("risk") if isinstance(guidance, dict) else None
    return {"symbol": symbol.upper(), "risk": risk}


@router.get("/api/symbol/{symbol}/sentiment")
async def symbol_sentiment(symbol: str, request: Request) -> dict[str, object]:
    news = await request.app.state.service.news.latest(symbol=symbol, limit=20)
    latest = request.app.state.service.latest_signals.get(symbol.upper())
    return {"symbol": symbol.upper(), "latest_news_count": len(news), "latest_news": news, "sentiment": latest.sentiment_outputs if latest else []}


@router.get("/api/symbol/{symbol}/market-data")
async def symbol_market_data(
    symbol: str,
    request: Request,
    timeframe: str = Query(default="1m", pattern="^(1m|5m|15m)$"),
    points: int = Query(default=90, ge=20, le=240),
) -> dict[str, object]:
    result = await request.app.state.service.market_data.fetch_live_ohlcv(symbol=symbol, timeframe=timeframe)
    if result.ok and result.data:
        live_bar = result.data.model_dump(mode="json")
        return {
            "symbol": symbol.upper(),
            "source": "NSEPython live quote",
            "timeframe": timeframe,
            "is_live": True,
            "bars": _display_bars_from_live(live_bar, points),
            "live_bar": live_bar,
        }
    return {
        "symbol": symbol.upper(),
        "source": "dashboard fallback",
        "timeframe": timeframe,
        "is_live": False,
        "error": result.error,
        "bars": _fallback_market_bars(symbol.upper(), points),
    }


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


def _display_bars_from_live(live_bar: dict[str, Any], points: int) -> list[dict[str, Any]]:
    """Builds a stable chart path anchored to the latest NSE quote."""
    close = max(float(live_bar.get("close") or 1.0), 1.0)
    start_price = close * 0.985
    now = utc_now()
    rows: list[dict[str, Any]] = []
    for index in range(points):
        progress = index / max(points - 1, 1)
        wave = math.sin(index / 6.0) * close * 0.0018
        bar_close = start_price + ((close - start_price) * progress) + wave
        if index == points - 1:
            bar_close = close
        open_price = rows[-1]["close"] if rows else bar_close
        spread = max(abs(bar_close - open_price), close * 0.0015)
        timestamp = now - timedelta(minutes=points - index - 1)
        rows.append(
            {
                "symbol": str(live_bar.get("symbol", "")).upper(),
                "timestamp": timestamp.isoformat(),
                "open": round(float(open_price), 4),
                "high": round(max(float(open_price), float(bar_close)) + spread, 4),
                "low": round(max(min(float(open_price), float(bar_close)) - spread, 0.01), 4),
                "close": round(float(bar_close), 4),
                "volume": float(live_bar.get("volume") or 0.0),
                "source": "NSEPython_live_seeded",
            }
        )
    return rows


def _fallback_market_bars(symbol: str, points: int) -> list[dict[str, Any]]:
    now = utc_now()
    close = 22000.0 if symbol == "NIFTY" else 1500.0
    rows: list[dict[str, Any]] = []
    for index in range(points):
        wave = math.sin(index / 6.0) * 0.45
        change = 0.22 + wave
        open_price = close
        close = max(10.0, close + change)
        timestamp = now - timedelta(minutes=points - index - 1)
        rows.append(
            {
                "symbol": symbol,
                "timestamp": timestamp.isoformat(),
                "open": round(open_price, 4),
                "high": round(max(open_price, close) + 1.2, 4),
                "low": round(min(open_price, close) - 1.1, 4),
                "close": round(close, 4),
                "volume": 120000 + index * 1700,
                "source": "dashboard_fallback",
            }
        )
    return rows
