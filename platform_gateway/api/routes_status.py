from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import PlatformStatus, utc_now

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/platform/status")
async def platform_status(request: Request) -> PlatformStatus:
    service = request.app.state.service
    return PlatformStatus(
        gateway="ok",
        adaptive_ai=await service.adaptive_ai.health(),
        algo_lab=await service.algo_lab.health(),
        scraper_news_store=await service.news.status(),
        checked_at=utc_now(),
    )


@router.get("/metrics")
async def metrics(request: Request) -> str:
    return request.app.state.service.orchestrator.metrics.render()


@router.get("/health/deep")
async def deep_health(request: Request) -> dict[str, object]:
    status = await platform_status(request)
    return {
        "status": "ok" if status.adaptive_ai == "ok" and status.algo_lab == "ok" else "degraded",
        "components": status.model_dump(mode="json"),
    }


@router.get("/pipeline/status/{correlation_id}")
async def pipeline_status(correlation_id: str, request: Request) -> object:
    state = request.app.state.service.orchestrator.status(correlation_id)
    if state is None:
        stored = request.app.state.service.pipeline_repository.get_pipeline_run(correlation_id)
        return stored or {"correlation_id": correlation_id, "status": "unknown"}
    return state
