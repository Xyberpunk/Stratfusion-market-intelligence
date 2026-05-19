from __future__ import annotations

from dataclasses import dataclass

from chroma_manager import ChromaManager
from db import MySQLStorage
from logger import get_logger
from models import NewsItem


@dataclass(frozen=True)
class SemanticMatch:
    is_duplicate: bool
    similarity: float
    matched_article_id: int | None = None
    matched_source: str | None = None


class ExactDeduper:
    """URL and source-content exact dedupe checks backed by MySQL."""

    def __init__(self, storage: MySQLStorage) -> None:
        self.storage = storage
        self.logger = get_logger("exact_deduper")

    async def duplicate_reason(self, item: NewsItem) -> str | None:
        if await self.storage.exists_by_url_hash(item.url_hash):
            self.logger.info("exact_duplicate", layer="url", source=item.source, url=item.url)
            return "url_hash"
        if await self.storage.exists_by_content_hash(item.source, item.content_hash):
            self.logger.info("exact_duplicate", layer="content", source=item.source, url=item.url)
            return "content_hash"
        return None


class SemanticDeduper:
    """Chroma-backed semantic duplicate detection."""

    def __init__(self, chroma: ChromaManager, threshold: float = 0.92) -> None:
        self.chroma = chroma
        self.threshold = threshold
        self.logger = get_logger("semantic_deduper", threshold=threshold)

    def find_duplicate(self, embedding: list[float]) -> SemanticMatch:
        matches = self.chroma.query_similar(embedding=embedding, n_results=5)
        if not matches:
            return SemanticMatch(is_duplicate=False, similarity=0.0)
        best = max(matches, key=lambda row: float(row["similarity"]))
        similarity = float(best["similarity"])
        metadata = best.get("metadata") or {}
        article_id = metadata.get("article_id")
        matched_id = int(article_id) if article_id is not None else None
        if similarity > self.threshold:
            self.logger.info(
                "semantic_duplicate",
                similarity=similarity,
                matched_article_id=matched_id,
                matched_source=metadata.get("source"),
            )
            return SemanticMatch(
                is_duplicate=True,
                similarity=similarity,
                matched_article_id=matched_id,
                matched_source=metadata.get("source"),
            )
        return SemanticMatch(
            is_duplicate=False,
            similarity=similarity,
            matched_article_id=matched_id,
            matched_source=metadata.get("source"),
        )
