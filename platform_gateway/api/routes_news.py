from __future__ import annotations

from fastapi import APIRouter, Query, Request

from models.schemas import LatestNewsItem

router = APIRouter()


@router.get("/news/latest")
async def latest_news(
    request: Request,
    symbol: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[LatestNewsItem]:
    return await request.app.state.service.news.latest(symbol=symbol, limit=limit)
