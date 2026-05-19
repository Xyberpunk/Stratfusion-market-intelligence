from __future__ import annotations

import asyncio
import signal

from chroma_manager import ChromaManager
from config import get_settings
from db import MySQLStorage
from dedupe import SemanticDeduper
from embeddings import EmbeddingGenerator
from logger import configure_logging, get_logger
from scheduler import ScrapeScheduler
from sources.cnbcawaaz import CnbcAwaazScraper
from sources.cnbctv18 import CnbcTv18Scraper
from sources.etmarkets import EtMarketsScraper
from sources.moneycontrol import MoneycontrolScraper
from sources.ndtvprofit import NdtvProfitScraper
from workers.embedding_worker import EmbeddingWorker


async def async_main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("main")
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    storage = MySQLStorage(settings)
    await storage.connect()
    chroma = ChromaManager(settings)
    embedder = EmbeddingGenerator()
    semantic_deduper = SemanticDeduper(chroma, threshold=settings.semantic_duplicate_threshold)
    embedding_worker = EmbeddingWorker(
        storage=storage,
        chroma=chroma,
        embedder=embedder,
        deduper=semantic_deduper,
    )
    scheduler = ScrapeScheduler(
        settings=settings,
        storage=storage,
        scrapers=[
            MoneycontrolScraper(settings),
            CnbcTv18Scraper(settings),
            EtMarketsScraper(settings),
            NdtvProfitScraper(settings),
            CnbcAwaazScraper(settings),
        ],
    )

    logger.info("platform_started")
    try:
        await asyncio.gather(
            scheduler.run_forever(stop_event),
            embedding_worker.run_forever(stop_event),
        )
    finally:
        stop_event.set()
        await scheduler.close_scrapers()
        await storage.close()
        logger.info("platform_stopped")


if __name__ == "__main__":
    asyncio.run(async_main())
