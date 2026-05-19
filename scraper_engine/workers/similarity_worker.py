from __future__ import annotations

from dataclasses import dataclass

from chroma_manager import ChromaManager
from embeddings import EmbeddingGenerator
from logger import get_logger


@dataclass(frozen=True)
class SimilarityResult:
    article_id: int | None
    source: str | None
    url: str | None
    similarity: float
    document: str


class SemanticSimilarityEngine:
    """Query-time semantic search over persisted market-news embeddings."""

    def __init__(self, chroma: ChromaManager, embedder: EmbeddingGenerator) -> None:
        self.chroma = chroma
        self.embedder = embedder
        self.logger = get_logger("semantic_similarity_engine")

    async def search(self, query: str, n_results: int = 10) -> list[SimilarityResult]:
        embedding = await self.embedder.embed_text(query)
        rows = self.chroma.query_similar(embedding=embedding, n_results=n_results)
        results: list[SimilarityResult] = []
        for row in rows:
            metadata = row.get("metadata") or {}
            raw_article_id = metadata.get("article_id")
            results.append(
                SimilarityResult(
                    article_id=int(raw_article_id) if raw_article_id is not None else None,
                    source=metadata.get("source"),
                    url=metadata.get("url"),
                    similarity=float(row["similarity"]),
                    document=str(row.get("document") or ""),
                )
            )
        self.logger.info("semantic_search_completed", query=query, results=len(results))
        return results
