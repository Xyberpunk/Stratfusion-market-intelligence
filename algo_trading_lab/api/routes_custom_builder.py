from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from models.schemas import CustomStrategyConfig

router = APIRouter()


@router.post("/strategies/custom")
async def create_custom_strategy(payload: CustomStrategyConfig, request: Request) -> CustomStrategyConfig:
    try:
        config = request.app.state.service.custom_builder.build(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    request.app.state.service.repository.save_custom_strategy(config)
    return config


@router.get("/strategies/custom")
async def list_custom_strategies(request: Request) -> list[CustomStrategyConfig]:
    return request.app.state.service.repository.list_custom_strategies()
