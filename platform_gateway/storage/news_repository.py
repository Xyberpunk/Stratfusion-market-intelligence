from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import aiomysql

from config import Settings
from logger import get_logger
from models.schemas import LatestNewsItem


class NewsRepository:
    """Reads latest ingested news, with a local fallback for dashboard runs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("news_repository")
        self._local_items: list[LatestNewsItem] = []
        self._local_id = 1

    async def status(self) -> str:
        if not self.settings.scraper_mysql_enabled:
            return "local-memory"
        try:
            conn = await aiomysql.connect(**self.settings.scraper_mysql_kwargs)
            conn.close()
            return "ok"
        except Exception as exc:
            self.logger.warning("scraper_news_store_unavailable", error=str(exc))
            return "unavailable"

    async def latest(self, symbol: str | None = None, limit: int = 20) -> list[LatestNewsItem]:
        if not self.settings.scraper_mysql_enabled:
            return self._latest_local(symbol=symbol, limit=limit)
        conn = await aiomysql.connect(**self.settings.scraper_mysql_kwargs)
        try:
            query = """
            SELECT id, source, title, url, summary, published_at, scraped_at,
                   sentiment, sentiment_score, semantic_duplicate
            FROM news_items
            WHERE (%s IS NULL OR title LIKE %s OR summary LIKE %s OR content LIKE %s)
            ORDER BY COALESCE(published_at, scraped_at) DESC, id DESC
            LIMIT %s
            """
            like = None if not symbol else f"%{symbol.upper()}%"
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (symbol, like, like, like, limit))
                rows: list[dict[str, Any]] = list(await cursor.fetchall())
            return [
                LatestNewsItem(
                    id=int(row["id"]),
                    source=str(row["source"]),
                    title=str(row["title"]),
                    url=str(row["url"]),
                    summary=row.get("summary"),
                    published_at=row.get("published_at"),
                    scraped_at=row["scraped_at"],
                    sentiment=row.get("sentiment"),
                    sentiment_score=row.get("sentiment_score"),
                    semantic_duplicate=bool(row.get("semantic_duplicate")),
                )
                for row in rows
            ]
        finally:
            conn.close()

    def record_dashboard_headlines(self, events: list[dict[str, Any]], sentiment_outputs: list[dict[str, Any]]) -> None:
        """Stores dashboard-submitted headlines when scraper MySQL is not enabled."""
        if self.settings.scraper_mysql_enabled:
            return
        sentiments_by_text = {str(item.get("text", "")): item for item in sentiment_outputs}
        now = datetime.now(timezone.utc)
        for event in events:
            text = str(event.get("text", "")).strip()
            if not text:
                continue
            sentiment = sentiments_by_text.get(text, {})
            self._local_items.append(
                LatestNewsItem(
                    id=self._local_id,
                    source=str(event.get("source") or "dashboard"),
                    title=text,
                    url="#",
                    summary=None,
                    published_at=event.get("timestamp") or now,
                    scraped_at=now,
                    sentiment=sentiment.get("sentiment"),
                    sentiment_score=self._score_from_sentiment(sentiment),
                    semantic_duplicate=False,
                )
            )
            self._local_id += 1
        self._local_items = self._local_items[-200:]

    def _latest_local(self, symbol: str | None, limit: int) -> list[LatestNewsItem]:
        if not symbol:
            return list(reversed(self._local_items[-limit:]))
        needle = symbol.upper()
        rows = [item for item in self._local_items if needle in item.title.upper()]
        return list(reversed(rows[-limit:]))

    @staticmethod
    def _score_from_sentiment(sentiment: dict[str, Any]) -> float | None:
        label = str(sentiment.get("sentiment", "neutral")).lower()
        confidence = sentiment.get("confidence")
        if confidence is None:
            return None
        value = float(confidence)
        if label == "bearish":
            return -value
        if label == "bullish":
            return value
        return 0.0
