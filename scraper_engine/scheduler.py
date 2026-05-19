from __future__ import annotations

import asyncio
import random
from collections.abc import Iterable

from config import Settings
from db import MySQLStorage
from dedupe import ExactDeduper
from logger import get_logger
from models import NewsItem
from sources.base import BaseScraper


class ScrapeScheduler:
    """Continuous source-isolated scraping scheduler with randomized polling."""

    def __init__(
        self,
        *,
        settings: Settings,
        storage: MySQLStorage,
        scrapers: Iterable[BaseScraper],
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.scrapers = list(scrapers)
        self.exact_deduper = ExactDeduper(storage)
        self.logger = get_logger("scheduler")

    async def run_forever(self, stop_event: asyncio.Event) -> None:
        self.logger.info("scheduler_started", sources=[scraper.source_name for scraper in self.scrapers])
        while not stop_event.is_set():
            await self.run_once()
            delay = random.uniform(self.settings.scrape_interval_min, self.settings.scrape_interval_max)
            self.logger.info("scheduler_sleep", seconds=round(delay, 2))
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=delay)
            except asyncio.TimeoutError:
                continue
        await self.close_scrapers()
        self.logger.info("scheduler_stopped")

    async def run_once(self) -> None:
        semaphore = asyncio.Semaphore(self.settings.source_concurrency)

        async def run_scraper(scraper: BaseScraper) -> None:
            async with semaphore:
                await self._run_source_with_retries(scraper)

        await asyncio.gather(*(run_scraper(scraper) for scraper in self.scrapers), return_exceptions=True)

    async def _run_source_with_retries(self, scraper: BaseScraper) -> None:
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                items = await scraper.scrape()
                await self._persist_items(items)
                self.logger.info("source_cycle_completed", source=scraper.source_name, articles=len(items))
                return
            except Exception as exc:
                backoff = min(300.0, (2**attempt) + random.uniform(0, 5))
                self.logger.exception(
                    "source_cycle_failed",
                    source=scraper.source_name,
                    attempt=attempt,
                    max_retries=self.settings.max_retries,
                    backoff_seconds=round(backoff, 2),
                    error=str(exc),
                )
                await asyncio.sleep(backoff)
        self.logger.error("source_cycle_exhausted", source=scraper.source_name)

    async def _persist_items(self, items: list[NewsItem]) -> None:
        inserted = 0
        skipped = 0
        for item in items:
            try:
                reason = await self.exact_deduper.duplicate_reason(item)
                if reason:
                    skipped += 1
                    continue
                result = await self.storage.insert_news_item(item)
                if result.inserted:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as exc:
                self.logger.exception("item_persist_failed", source=item.source, url=item.url, error=str(exc))
        self.logger.info("items_persisted", inserted=inserted, skipped=skipped)

    async def close_scrapers(self) -> None:
        await asyncio.gather(*(scraper.close() for scraper in self.scrapers), return_exceptions=True)
