from __future__ import annotations

from typing import Any

import aiomysql

from config import Settings
from logger import get_logger
from models.schemas import LatestNewsItem


class NewsRepository:
    """Reads latest ingested news from scraper_engine MySQL storage when enabled."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("news_repository")

    async def status(self) -> str:
        if not self.settings.scraper_mysql_enabled:
            return "disabled"
        try:
            conn = await aiomysql.connect(**self.settings.scraper_mysql_kwargs)
            conn.close()
            return "ok"
        except Exception as exc:
            self.logger.warning("scraper_news_store_unavailable", error=str(exc))
            return "unavailable"

    async def latest(self, symbol: str | None = None, limit: int = 20) -> list[LatestNewsItem]:
        if not self.settings.scraper_mysql_enabled:
            return []
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
