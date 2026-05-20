from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

import aiomysql
import httpx

from config import Settings
from logger import get_logger
from models.schemas import LatestNewsItem

LIVE_NEWS_URLS = [
    "https://www.moneycontrol.com/news/business/markets/",
    "https://www.moneycontrol.com/news/business/stocks/",
    "https://www.moneycontrol.com/news/stock-markets/",
    "https://www.cnbctv18.com/market/",
]


class NewsRepository:
    """Reads latest ingested news, with a local fallback for dashboard runs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("news_repository")
        self._local_items: list[LatestNewsItem] = []
        self._local_id = 1
        self._live_cache: list[LatestNewsItem] = []
        self._live_cache_at: datetime | None = None

    async def status(self) -> str:
        if not self.settings.scraper_mysql_enabled:
            return "live-fallback"
        try:
            conn = await aiomysql.connect(**self.settings.scraper_mysql_kwargs)
            conn.close()
            return "ok"
        except Exception as exc:
            self.logger.warning("scraper_news_store_unavailable", error=str(exc))
            return "unavailable"

    async def latest(self, symbol: str | None = None, limit: int = 20) -> list[LatestNewsItem]:
        if not self.settings.scraper_mysql_enabled:
            local_rows = self._latest_local(symbol=symbol, limit=limit)
            live_rows = await self._latest_live(symbol=symbol, limit=limit)
            return self._merge_news(local_rows, live_rows, limit)
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

    async def _latest_live(self, symbol: str | None, limit: int) -> list[LatestNewsItem]:
        if self._live_cache_at and (datetime.now(timezone.utc) - self._live_cache_at).total_seconds() < 300:
            return self._filter_live_cache(symbol=symbol, limit=limit)
        rows: list[LatestNewsItem] = []
        async with httpx.AsyncClient(
            timeout=12,
            headers={
                "User-Agent": "StratFusionMarketIntelligence/1.0 (+local-dashboard; ethical-rate-limited)",
                "Accept": "text/html,application/xhtml+xml",
            },
            follow_redirects=True,
        ) as client:
            for url in LIVE_NEWS_URLS:
                try:
                    response = await client.get(url)
                    if response.status_code in {403, 429}:
                        self.logger.warning("live_news_rate_limited", url=url, status=response.status_code)
                        continue
                    response.raise_for_status()
                    rows.extend(_extract_headlines(response.text, base_url=url, source=_source_name(url), start_id=100000 + len(rows)))
                except Exception as exc:
                    self.logger.warning("live_news_fetch_failed", url=url, error=str(exc))
        self._live_cache = _dedupe_news(rows)[:80]
        self._live_cache_at = datetime.now(timezone.utc)
        return self._filter_live_cache(symbol=symbol, limit=limit)

    def _filter_live_cache(self, symbol: str | None, limit: int) -> list[LatestNewsItem]:
        if not symbol:
            return self._live_cache[:limit]
        needle = symbol.upper()
        symbol_rows = [item for item in self._live_cache if needle in item.title.upper()]
        return (symbol_rows or self._live_cache)[:limit]

    @staticmethod
    def _merge_news(local_rows: list[LatestNewsItem], live_rows: list[LatestNewsItem], limit: int) -> list[LatestNewsItem]:
        seen: set[str] = set()
        merged: list[LatestNewsItem] = []
        for item in [*local_rows, *live_rows]:
            key = item.url if item.url != "#" else item.title.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
            if len(merged) >= limit:
                break
        return merged

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


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            text = data.strip()
            if text:
                self._text_parts.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._href:
            return
        text = " ".join(self._text_parts).strip()
        if text:
            self.links.append((self._href, " ".join(text.split())))
        self._href = None
        self._text_parts = []


def _extract_headlines(html: str, *, base_url: str, source: str, start_id: int) -> list[LatestNewsItem]:
    parser = _AnchorParser()
    parser.feed(html)
    now = datetime.now(timezone.utc)
    rows: list[LatestNewsItem] = []
    for href, title in parser.links:
        if not _looks_like_news_link(href, title):
            continue
        absolute_url = urljoin(base_url, href)
        rows.append(
            LatestNewsItem(
                id=start_id + len(rows),
                source=source,
                title=title,
                url=absolute_url,
                summary=None,
                published_at=None,
                scraped_at=now,
                sentiment=None,
                sentiment_score=None,
                semantic_duplicate=False,
            )
        )
    return rows


def _looks_like_news_link(href: str, title: str) -> bool:
    if len(title) < 35 or len(title) > 220:
        return False
    lowered = title.lower()
    if any(token in lowered for token in {"subscribe", "download app", "follow us", "sign in", "watch live"}):
        return False
    path = urlparse(href).path.lower()
    return "/news/" in path or "/market/" in path or path.endswith(".html")


def _source_name(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "moneycontrol" in host:
        return "Moneycontrol"
    if "cnbctv18" in host:
        return "CNBC TV18"
    return host or "live-news"


def _dedupe_news(rows: list[LatestNewsItem]) -> list[LatestNewsItem]:
    seen: set[str] = set()
    deduped: list[LatestNewsItem] = []
    for item in rows:
        key = item.url or item.title.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
