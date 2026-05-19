from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import RegimeDetectionRequest, RegimeOutput

router = APIRouter()


@router.post("/regime/detect")
async def detect_regime(payload: RegimeDetectionRequest, request: Request) -> RegimeOutput:
    output = request.app.state.service.regime_detector.detect(payload)
    request.app.state.service.repository.save_regime(output)
    request.app.state.service.regime_memory.add(output)
    return output
