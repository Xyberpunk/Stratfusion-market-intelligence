from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import AnomalyDetectionRequest, AnomalyOutput

router = APIRouter()


@router.post("/anomaly/detect")
async def detect_anomaly(payload: AnomalyDetectionRequest, request: Request) -> list[AnomalyOutput]:
    outputs = request.app.state.service.anomaly_detector.detect(payload)
    request.app.state.service.repository.save_anomalies(outputs)
    return outputs
