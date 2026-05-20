from __future__ import annotations

from typing import Any

import chromadb

from config import Settings
from logger import get_logger


class ChromaManager:
    """Persistent ChromaDB adapter for market-news embeddings."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("chroma_manager")
        self.client = chromadb.PersistentClient(path=str(settings.chroma_db_path))
        self.collection: Any = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.logger.info(
            "chroma_collection_ready",
            path=str(settings.chroma_db_path),
            collection=settings.chroma_collection_name,
        )

    def add_article_embedding(
        self,
        *,
        article_id: int,
        embedding: list[float],
        document: str,
        metadata: dict[str, Any],
    ) -> None:
        chroma_id = f"article:{article_id}"
        payload = {
            "article_id": article_id,
            "source": metadata.get("source", ""),
            "timestamp": str(metadata.get("timestamp") or ""),
            "sentiment": metadata.get("sentiment") or "pending",
            "sentiment_score": metadata.get("sentiment_score") or 0.0,
            "url": metadata.get("url", ""),
            "language": metadata.get("language", "en"),
        }
        self.collection.upsert(
            ids=[chroma_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[payload],
        )
        self.logger.info("chroma_embedding_upserted", article_id=article_id)

    def query_similar(self, *, embedding: list[float], n_results: int = 5) -> list[dict[str, Any]]:
        count = self.collection.count()
        if count == 0:
            return []
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, count),
            include=["metadatas", "documents", "distances"],
        )
        rows: list[dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for idx, chroma_id in enumerate(ids):
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            rows.append(
                {
                    "id": chroma_id,
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                    "document": documents[idx] if idx < len(documents) else "",
                    "distance": distance,
                    "similarity": round(max(0.0, min(1.0, 1.0 - distance)), 6),
                }
            )
        return rows
