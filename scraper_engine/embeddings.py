from __future__ import annotations

import asyncio
from functools import cached_property

from sentence_transformers import SentenceTransformer

from logger import get_logger


class EmbeddingGenerator:
    """Lazy sentence-transformer wrapper isolated from scraper execution."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.logger = get_logger("embedding_generator", model=model_name)

    @cached_property
    def model(self) -> SentenceTransformer:
        self.logger.info("embedding_model_loading")
        model = SentenceTransformer(self.model_name)
        self.logger.info("embedding_model_loaded")
        return model

    async def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Cannot embed empty text")
        vector = await asyncio.to_thread(
            self.model.encode,
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [float(value) for value in vector.tolist()]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = await asyncio.to_thread(
            self.model.encode,
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [[float(value) for value in vector.tolist()] for vector in vectors]
