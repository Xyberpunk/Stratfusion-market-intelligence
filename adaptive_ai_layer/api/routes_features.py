from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import FeatureBuildRequest, FeatureBuildResponse

router = APIRouter()


@router.post("/features/build")
async def build_features(payload: FeatureBuildRequest, request: Request) -> FeatureBuildResponse:
    response = request.app.state.service.feature_builder.build_response(payload)
    if response.features:
        latest = response.features[-1]
        timestamp = response.latest_timestamp
        if timestamp is not None:
            numeric = {key: value for key, value in latest.items() if isinstance(value, (int, float))}
            request.app.state.service.feature_store.write_snapshot(payload.symbol, timestamp, numeric)
    return response


@router.get("/features/latest/{symbol}")
async def latest_features(symbol: str, request: Request) -> dict[str, float]:
    return request.app.state.service.feature_serving.latest_values(symbol)
