from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from models.schemas import EnsembleRunRequest, GenerateSignalRequest

router = APIRouter()


@router.post("/signals/generate")
async def generate_signal(payload: GenerateSignalRequest, request: Request) -> dict[str, object]:
    try:
        return request.app.state.service.generate_signal(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ensemble/run")
async def run_ensemble(payload: EnsembleRunRequest, request: Request) -> object:
    try:
        return request.app.state.service.run_ensemble(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/regime/{symbol}")
async def get_regime(symbol: str, request: Request) -> object:
    regime = request.app.state.service.repository.get_regime(symbol.upper())
    if regime is None:
        raise HTTPException(status_code=404, detail="No regime snapshot found for symbol")
    return regime


@router.get("/risk/{symbol}")
async def get_risk(symbol: str, request: Request) -> object:
    risk = request.app.state.service.repository.get_risk(symbol.upper())
    if risk is None:
        raise HTTPException(status_code=404, detail="No risk output found for symbol")
    return risk
