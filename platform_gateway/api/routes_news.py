from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request

from models.schemas import LatestNewsItem

router = APIRouter()


@router.get("/news/latest")
async def latest_news(
    request: Request,
    symbol: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[LatestNewsItem]:
    rows = await request.app.state.service.news.latest(symbol=symbol, limit=limit)
    return await _with_sentiment(request, rows, symbol)


async def _with_sentiment(request: Request, rows: list[LatestNewsItem], symbol: str | None) -> list[LatestNewsItem]:
    pending = [item for item in rows if item.sentiment is None and item.title]
    if not pending:
        return rows
    try:
        outputs = await request.app.state.service.adaptive_ai.finbert_batch(
            [
                {
                    "symbol": symbol,
                    "timestamp": item.scraped_at.isoformat(),
                    "text": item.title,
                    "source": item.source,
                }
                for item in pending[:20]
            ]
        )
    except Exception:
        return rows
    scores_by_text = {str(item.get("text", "")): item for item in outputs}
    enriched: list[LatestNewsItem] = []
    for item in rows:
        output = scores_by_text.get(item.title)
        if not output:
            enriched.append(item)
            continue
        enriched.append(
            item.model_copy(
                update={
                    "sentiment": output.get("sentiment"),
                    "sentiment_score": _sentiment_score(output),
                }
            )
        )
    return enriched


def _sentiment_score(output: dict[str, Any]) -> float | None:
    confidence = output.get("confidence")
    if confidence is None:
        return None
    label = str(output.get("sentiment", "neutral")).lower()
    value = float(confidence)
    if label == "bearish":
        return -value
    if label == "bullish":
        return value
    return 0.0
