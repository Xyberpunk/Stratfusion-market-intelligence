from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import aiomysql

from config import Settings
from logger import get_logger


SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS strategy_definitions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        strategy_name VARCHAR(150) NOT NULL UNIQUE,
        category VARCHAR(80) NOT NULL,
        enabled TINYINT DEFAULT 1,
        config_json JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_strategy_name (strategy_name),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS strategy_signals (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        strategy_name VARCHAR(150) NOT NULL,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        signal VARCHAR(20) NOT NULL,
        confidence FLOAT NOT NULL,
        score FLOAT NOT NULL,
        reason TEXT,
        metadata JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_strategy_name (strategy_name),
        INDEX idx_signal (signal),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS ensemble_signals (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        bullish_probability FLOAT NOT NULL,
        bearish_probability FLOAT NOT NULL,
        neutral_probability FLOAT NOT NULL,
        confidence VARCHAR(20) NOT NULL,
        suggested_action VARCHAR(20) NOT NULL,
        risk_level VARCHAR(20) NOT NULL,
        explanation TEXT,
        strategy_breakdown JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_signal (suggested_action),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS regime_snapshots (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        regime VARCHAR(80) NOT NULL,
        confidence FLOAT NOT NULL,
        features JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_regime (regime),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS risk_outputs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        entry_price FLOAT NOT NULL,
        stop_loss FLOAT NOT NULL,
        target FLOAT NOT NULL,
        risk_reward_ratio FLOAT NOT NULL,
        position_size FLOAT NOT NULL,
        capital_at_risk FLOAT NOT NULL,
        max_drawdown_limit FLOAT NOT NULL,
        risk_level VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS backtest_runs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        strategy_name VARCHAR(150),
        symbol VARCHAR(50) NOT NULL,
        start_date DATETIME NOT NULL,
        end_date DATETIME NOT NULL,
        parameters JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_strategy_name (strategy_name),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS backtest_results (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        run_id BIGINT,
        strategy_name VARCHAR(150) NOT NULL,
        symbol VARCHAR(50) NOT NULL,
        start_date DATETIME NOT NULL,
        end_date DATETIME NOT NULL,
        total_trades INT NOT NULL,
        win_rate FLOAT NOT NULL,
        profit_factor FLOAT NOT NULL,
        max_drawdown FLOAT NOT NULL,
        average_return FLOAT NOT NULL,
        accuracy FLOAT NOT NULL,
        metadata JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_strategy_name (strategy_name),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS strategy_accuracy (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        strategy_name VARCHAR(150) NOT NULL,
        symbol VARCHAR(50) NOT NULL,
        regime VARCHAR(80) NOT NULL,
        timeframe VARCHAR(20) NOT NULL,
        accuracy FLOAT NOT NULL,
        win_rate FLOAT NOT NULL,
        avg_return FLOAT NOT NULL,
        sample_size INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_strategy_name (strategy_name),
        INDEX idx_regime (regime),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS custom_strategies (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(180) NOT NULL UNIQUE,
        config_json JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS anomaly_events (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        anomaly_type VARCHAR(100) NOT NULL,
        severity VARCHAR(20) NOT NULL,
        score FLOAT NOT NULL,
        explanation TEXT,
        metadata JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_symbol (symbol),
        INDEX idx_timestamp (timestamp),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


class MySQLClient:
    """Async MySQL client for durable platform persistence."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pool: aiomysql.Pool | None = None
        self.logger = get_logger("mysql_client")

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
        await self.init_schema()

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    @asynccontextmanager
    async def connection(self) -> Any:
        if self.pool is None:
            raise RuntimeError("MySQL is not connected")
        async with self.pool.acquire() as conn:
            yield conn

    async def init_schema(self) -> None:
        if self.pool is None:
            return
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                for statement in SCHEMA_SQL:
                    await cursor.execute(statement)
            await conn.commit()
        self.logger.info("mysql_schema_ready")
