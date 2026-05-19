from __future__ import annotations

import json
from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Any

import aiomysql

from config import Settings
from logger import get_logger
from models import InsertResult, NewsItem
from utils.normalization import db_datetime

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS news_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    source VARCHAR(100) NOT NULL,

    title TEXT NOT NULL,

    url TEXT NOT NULL,

    url_hash CHAR(64) NOT NULL,

    content_hash CHAR(64) NOT NULL,

    semantic_hash CHAR(64),

    summary TEXT,

    content LONGTEXT,

    author VARCHAR(255),

    published_at DATETIME NULL,

    scraped_at DATETIME NOT NULL,

    language VARCHAR(20),

    sentiment VARCHAR(50),

    sentiment_score FLOAT,

    embedding_status TINYINT DEFAULT 0,

    semantic_duplicate TINYINT DEFAULT 0,

    raw_json JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_url_hash (url_hash),

    UNIQUE KEY uq_source_content_hash (source, content_hash),

    INDEX idx_source (source),

    INDEX idx_published_at (published_at),

    INDEX idx_embedding_status (embedding_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


class MySQLStorage:
    """Async MySQL storage layer with duplicate-safe inserts."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pool: aiomysql.Pool | None = None
        self.logger = get_logger("mysql_storage")

    async def create_database_if_missing(self) -> None:
        conn = await aiomysql.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            charset="utf8mb4",
            autocommit=True,
        )
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.settings.mysql_database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        finally:
            conn.close()

    async def connect(self) -> None:
        await self.create_database_if_missing()
        self.pool = await aiomysql.create_pool(
            minsize=1,
            maxsize=10,
            **self.settings.mysql_pool_kwargs,
        )
        await self.init_schema()
        self.logger.info("mysql_connected", database=self.settings.mysql_database)

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.logger.info("mysql_closed")

    @asynccontextmanager
    async def connection(self) -> Any:
        if self.pool is None:
            raise RuntimeError("MySQL pool is not initialized")
        async with self.pool.acquire() as conn:
            yield conn

    async def init_schema(self) -> None:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(SCHEMA_SQL)
            await conn.commit()
        self.logger.info("mysql_schema_ready")

    async def exists_by_url_hash(self, url_hash: str) -> bool:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1 FROM news_items WHERE url_hash=%s LIMIT 1", (url_hash,))
                return await cursor.fetchone() is not None

    async def exists_by_content_hash(self, source: str, content_hash: str) -> bool:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT 1 FROM news_items WHERE source=%s AND content_hash=%s LIMIT 1",
                    (source, content_hash),
                )
                return await cursor.fetchone() is not None

    async def insert_news_item(self, item: NewsItem) -> InsertResult:
        sql = """
        INSERT INTO news_items (
            source, title, url, url_hash, content_hash, semantic_hash, summary, content,
            author, published_at, scraped_at, language, raw_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CAST(%s AS JSON))
        """
        params = (
            item.source,
            item.title,
            item.url,
            item.url_hash,
            item.content_hash,
            item.semantic_hash,
            item.summary,
            item.content,
            item.author,
            db_datetime(item.published_at),
            db_datetime(item.scraped_at),
            item.language,
            json.dumps(item.raw_json(), ensure_ascii=False),
        )
        async with self.connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, params)
                    article_id = int(cursor.lastrowid)
                await conn.commit()
                self.logger.info("news_inserted", source=item.source, article_id=article_id, url=item.url)
                return InsertResult(inserted=True, article_id=article_id)
            except aiomysql.IntegrityError as exc:
                await conn.rollback()
                message = str(exc).lower()
                if "uq_url_hash" in message:
                    reason = "url_hash"
                elif "uq_source_content_hash" in message:
                    reason = "content_hash"
                else:
                    reason = "integrity_error"
                self.logger.info("duplicate_skipped", source=item.source, reason=reason, url=item.url)
                return InsertResult(inserted=False, duplicate_reason=reason)
            except Exception:
                await conn.rollback()
                self.logger.exception("news_insert_failed", source=item.source, url=item.url)
                raise

    async def fetch_pending_embeddings(self, limit: int = 100) -> list[dict[str, Any]]:
        sql = """
        SELECT id, source, title, summary, content, url, published_at, scraped_at, language
        FROM news_items
        WHERE embedding_status = 0 AND semantic_duplicate = 0
        ORDER BY COALESCE(published_at, scraped_at) ASC, id ASC
        LIMIT %s
        """
        async with self.connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, (limit,))
                rows = await cursor.fetchall()
                return list(rows)

    async def mark_embedding_status(self, article_id: int, status: int) -> None:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE news_items SET embedding_status=%s WHERE id=%s", (status, article_id))
            await conn.commit()

    async def mark_semantic_duplicate(self, article_id: int) -> None:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE news_items SET semantic_duplicate=1, embedding_status=3 WHERE id=%s",
                    (article_id,),
                )
            await conn.commit()
        self.logger.info("semantic_duplicate_marked", article_id=article_id)

    async def mark_embedded(self, article_id: int) -> None:
        await self.mark_embedding_status(article_id, 2)

    async def mark_embedding_failed(self, article_id: int) -> None:
        await self.mark_embedding_status(article_id, 4)

    async def reset_stale_processing(self) -> int:
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE news_items SET embedding_status=0 WHERE embedding_status=1")
                affected = int(cursor.rowcount)
            await conn.commit()
        return affected

    async def bulk_insert_news_items(self, items: Sequence[NewsItem]) -> list[InsertResult]:
        results: list[InsertResult] = []
        for item in items:
            results.append(await self.insert_news_item(item))
        return results
