from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from chroma_manager import ChromaManager
from db import MySQLStorage
from dedupe import SemanticDeduper
from embeddings import EmbeddingGenerator
from logger import get_logger
from utils.normalization import compact_for_embedding


class EmbeddingWorker:
    """Pulls pending MySQL rows, generates embeddings, and writes non-duplicates to ChromaDB."""

    def __init__(
        self,
        *,
        storage: MySQLStorage,
        chroma: ChromaManager,
        embedder: EmbeddingGenerator,
        deduper: SemanticDeduper,
        batch_size: int = 50,
        idle_sleep_seconds: float = 10.0,
    ) -> None:
        self.storage = storage
        self.chroma = chroma
        self.embedder = embedder
        self.deduper = deduper
        self.batch_size = batch_size
        self.idle_sleep_seconds = idle_sleep_seconds
        self.logger = get_logger("embedding_worker")

    async def run_forever(self, stop_event: asyncio.Event) -> None:
        reset = await self.storage.reset_stale_processing()
        if reset:
            self.logger.warning("stale_embeddings_reset", count=reset)
        self.logger.info("embedding_worker_started")
        while not stop_event.is_set():
            try:
                processed = await self.process_batch()
                if processed == 0:
                    await asyncio.wait_for(stop_event.wait(), timeout=self.idle_sleep_seconds)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                self.logger.exception("embedding_worker_batch_failed", error=str(exc))
                await asyncio.sleep(self.idle_sleep_seconds)
        self.logger.info("embedding_worker_stopped")

    async def process_batch(self) -> int:
        rows = await self.storage.fetch_pending_embeddings(limit=self.batch_size)
        if not rows:
            return 0
        processed = 0
        for row in rows:
            article_id = int(row["id"])
            try:
                await self.storage.mark_embedding_status(article_id, 1)
                await self.process_row(row)
                processed += 1
            except Exception as exc:
                self.logger.exception("embedding_row_failed", article_id=article_id, error=str(exc))
                await self.storage.mark_embedding_failed(article_id)
        return processed

    async def process_row(self, row: dict[str, Any]) -> None:
        article_id = int(row["id"])
        document = compact_for_embedding(
            str(row.get("title") or ""),
            row.get("summary"),
            row.get("content"),
        )
        if not document:
            await self.storage.mark_embedding_failed(article_id)
            return
        embedding = await self.embedder.embed_text(document)
        semantic_match = self.deduper.find_duplicate(embedding)
        if semantic_match.is_duplicate:
            await self.storage.mark_semantic_duplicate(article_id)
            self.logger.info(
                "embedding_skipped_semantic_duplicate",
                article_id=article_id,
                similarity=semantic_match.similarity,
                matched_article_id=semantic_match.matched_article_id,
            )
            return
        timestamp = row.get("published_at") or row.get("scraped_at") or datetime.utcnow().isoformat()
        self.chroma.add_article_embedding(
            article_id=article_id,
            embedding=embedding,
            document=document,
            metadata={
                "source": row.get("source"),
                "timestamp": timestamp,
                "url": row.get("url"),
                "language": row.get("language") or "en",
                "sentiment": "pending",
                "sentiment_score": 0.0,
            },
        )
        await self.storage.mark_embedded(article_id)
        self.logger.info("embedding_completed", article_id=article_id)
