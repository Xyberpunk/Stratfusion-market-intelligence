from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/strategies")
async def get_strategies(request: Request) -> list[dict[str, str]]:
    return request.app.state.service.list_strategies()


@router.get("/accuracy/strategy/{strategy_name}")
async def get_strategy_accuracy(strategy_name: str, request: Request) -> list[object]:
    return request.app.state.service.repository.get_accuracy(strategy_name)
