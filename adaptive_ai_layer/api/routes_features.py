from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import FeatureBuildRequest, FeatureBuildResponse

router = APIRouter()


@router.post("/features/build")
async def build_features(payload: FeatureBuildRequest, request: Request) -> FeatureBuildResponse:
    return request.app.state.service.feature_builder.build_response(payload)
