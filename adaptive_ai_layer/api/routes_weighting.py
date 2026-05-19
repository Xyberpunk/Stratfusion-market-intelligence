from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import PaperTradeFeedback, StrategyPerformanceRecord, WeightingOutput, WeightingRequest

router = APIRouter()


@router.post("/weighting/suggest")
async def suggest_weighting(payload: WeightingRequest, request: Request) -> WeightingOutput:
    output = request.app.state.service.weight_engine.suggest(payload)
    request.app.state.service.repository.save_weighting(output)
    return output


@router.get("/memory/strategy/{strategy_name}")
async def get_strategy_memory(strategy_name: str, request: Request) -> list[StrategyPerformanceRecord]:
    return request.app.state.service.performance_memory.query(strategy_name=strategy_name)


@router.post("/feedback/paper-trade")
async def paper_trade_feedback(payload: PaperTradeFeedback, request: Request) -> dict[str, float | str]:
    request.app.state.service.repository.save_feedback(payload)
    return request.app.state.service.feedback_loop.record(payload)
