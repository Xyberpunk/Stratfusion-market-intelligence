from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiomysql

from config import Settings
from logger import get_logger


class MySQLStore:
    """Optional MySQL persistence for adaptive intelligence artifacts."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pool: aiomysql.Pool | None = None
        self.logger = get_logger("mysql_store")

    async def connect(self) -> None:
        if not self.settings.mysql_enabled:
            self.logger.info("mysql_disabled")
            return
        bootstrap = await aiomysql.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            charset="utf8mb4",
            autocommit=True,
        )
        try:
            async with bootstrap.cursor() as cursor:
                await cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.settings.mysql_database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        finally:
            bootstrap.close()
        self.pool = await aiomysql.create_pool(minsize=1, maxsize=10, **self.settings.mysql_pool_kwargs)
        await self.apply_migrations()

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    @asynccontextmanager
    async def connection(self) -> Any:
        if self.pool is None:
            raise RuntimeError("MySQL pool is not initialized")
        async with self.pool.acquire() as conn:
            yield conn

    async def apply_migrations(self) -> None:
        if self.pool is None:
            return
        sql = Path("storage/migrations.sql").read_text(encoding="utf-8")
        statements = [part.strip() for part in sql.split(";") if part.strip()]
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                for statement in statements:
                    await cursor.execute(statement)
            await conn.commit()
        self.logger.info("mysql_migrations_applied", statements=len(statements))
