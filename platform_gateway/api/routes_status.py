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
