from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from models.schemas import BacktestRunRequest

router = APIRouter()


@router.post("/backtest/run")
async def run_backtest(payload: BacktestRunRequest, request: Request) -> dict[str, object]:
    try:
        return request.app.state.service.run_backtest(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/backtest/results/{run_id}")
async def get_backtest_result(run_id: int, request: Request) -> object:
    result = request.app.state.service.repository.get_backtest(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    return result
