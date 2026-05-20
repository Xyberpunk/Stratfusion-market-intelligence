from __future__ import annotations

import json
from typing import Any

import aiomysql

from config import Settings
from logger import get_logger
from models.schemas import UnifiedPipelineResponse

SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS pipeline_runs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        correlation_id VARCHAR(80) NOT NULL UNIQUE,
        symbol VARCHAR(50) NOT NULL,
        status VARCHAR(40) NOT NULL,
        payload JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_correlation_id (correlation_id),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS final_signals (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        correlation_id VARCHAR(80) NOT NULL,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        final_action VARCHAR(20) NOT NULL,
        bullish_probability DOUBLE,
        bearish_probability DOUBLE,
        neutral_probability DOUBLE,
        risk_level VARCHAR(20),
        explanation TEXT,
        payload JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_correlation_id (correlation_id),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


class PipelineRepository:
    """Optional MySQL persistence with in-memory fallback for final pipeline outputs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("pipeline_repository")
        self._signals: dict[str, UnifiedPipelineResponse] = {}
        self._runs: dict[str, dict[str, Any]] = {}
        self._pool: aiomysql.Pool | None = None

    async def start(self) -> None:
        if not self.settings.pipeline_mysql_enabled:
            return
        try:
            bootstrap = await aiomysql.connect(
                host=self.settings.scraper_mysql_host,
                port=self.settings.scraper_mysql_port,
                user=self.settings.scraper_mysql_user,
                password=self.settings.scraper_mysql_password,
                charset="utf8mb4",
                autocommit=True,
            )
            async with bootstrap.cursor() as cursor:
                await cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.settings.pipeline_mysql_database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            bootstrap.close()
            self._pool = await aiomysql.create_pool(minsize=1, maxsize=4, **self.settings.pipeline_mysql_kwargs)
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    for statement in SCHEMA_SQL:
                        await cursor.execute(statement)
                await conn.commit()
        except Exception as exc:
            self.logger.warning("pipeline_mysql_unavailable", error=str(exc))
            self._pool = None

    async def close(self) -> None:
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    async def save_final_signal(self, correlation_id: str, response: UnifiedPipelineResponse) -> None:
        self._signals[response.symbol.upper()] = response
        self._runs[correlation_id] = {"correlation_id": correlation_id, "symbol": response.symbol, "status": "FINALIZED", "response": response.model_dump(mode="json")}
        if not self._pool:
            return
        guidance = response.trading_guidance.get("guidance", response.trading_guidance)
        ensemble = guidance.get("ensemble", {}) if isinstance(guidance, dict) else {}
        risk = guidance.get("risk", {}) if isinstance(guidance, dict) else {}
        final_action = guidance.get("final_action") or risk.get("final_action") or ensemble.get("suggested_action") or "HOLD"
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO pipeline_runs (correlation_id, symbol, status, payload) VALUES (%s, %s, %s, CAST(%s AS JSON)) "
                    "ON DUPLICATE KEY UPDATE status=VALUES(status), payload=VALUES(payload)",
                    (correlation_id, response.symbol, "FINALIZED", json.dumps(response.model_dump(mode="json"), default=str)),
                )
                await cursor.execute(
                    """
                    INSERT INTO final_signals (
                        correlation_id, symbol, timestamp, final_action, bullish_probability, bearish_probability,
                        neutral_probability, risk_level, explanation, payload
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CAST(%s AS JSON))
                    """,
                    (
                        correlation_id,
                        response.symbol,
                        response.timestamp.replace(tzinfo=None),
                        final_action,
                        ensemble.get("bullish_probability"),
                        ensemble.get("bearish_probability"),
                        ensemble.get("neutral_probability"),
                        risk.get("risk_level"),
                        response.explanation,
                        json.dumps(response.model_dump(mode="json"), default=str),
                    ),
                )
            await conn.commit()

    def get_latest_signal(self, symbol: str) -> UnifiedPipelineResponse | None:
        return self._signals.get(symbol.upper())

    def get_pipeline_run(self, correlation_id: str) -> dict[str, Any] | None:
        return self._runs.get(correlation_id)
