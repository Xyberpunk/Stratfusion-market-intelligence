from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from models.schemas import ModelRegistryItem, TrainingRunOutput, TrainingRunRequest

router = APIRouter()


@router.post("/training/run")
async def run_training(payload: TrainingRunRequest, request: Request) -> TrainingRunOutput:
    try:
        output = request.app.state.service.trainer.run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    request.app.state.service.repository.save_training_run(output)
    for item in request.app.state.service.model_registry.list_models():
        request.app.state.service.repository.save_model(item)
    return output


@router.get("/models")
async def list_models(request: Request) -> list[ModelRegistryItem]:
    return request.app.state.service.model_registry.list_models()
