from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, field_validator

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None or value == "" else int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None or value == "" else float(value)


class Settings(BaseModel):
    mysql_host: str = Field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    mysql_port: int = Field(default_factory=lambda: _env_int("MYSQL_PORT", 3306))
    mysql_user: str = Field(default_factory=lambda: os.getenv("MYSQL_USER", "stock_user"))
    mysql_password: str = Field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    mysql_database: str = Field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "stock_news"))

    headless: bool = Field(default_factory=lambda: _env_bool("HEADLESS", True))
    scrape_interval_min: int = Field(default_factory=lambda: _env_int("SCRAPE_INTERVAL_MIN", 120))
    scrape_interval_max: int = Field(default_factory=lambda: _env_int("SCRAPE_INTERVAL_MAX", 300))

    max_retries: int = Field(default_factory=lambda: _env_int("MAX_RETRIES", 5))
    timeout_seconds: int = Field(default_factory=lambda: _env_int("TIMEOUT_SECONDS", 60))

    chroma_db_path: Path = Field(default_factory=lambda: Path(os.getenv("CHROMA_DB_PATH", "./chroma_db")))
    chroma_collection_name: str = "market_news_embeddings"
    semantic_duplicate_threshold: float = Field(
        default_factory=lambda: _env_float("SEMANTIC_DUPLICATE_THRESHOLD", 0.92)
    )

    playwright_viewport_width: int = Field(default_factory=lambda: _env_int("PLAYWRIGHT_VIEWPORT_WIDTH", 1366))
    playwright_viewport_height: int = Field(default_factory=lambda: _env_int("PLAYWRIGHT_VIEWPORT_HEIGHT", 768))
    max_articles_per_source: int = Field(default_factory=lambda: _env_int("MAX_ARTICLES_PER_SOURCE", 50))
    article_concurrency: int = Field(default_factory=lambda: _env_int("ARTICLE_CONCURRENCY", 3))
    source_concurrency: int = Field(default_factory=lambda: _env_int("SOURCE_CONCURRENCY", 3))
    request_delay_min_seconds: float = Field(default_factory=lambda: _env_float("REQUEST_DELAY_MIN_SECONDS", 1.0))
    request_delay_max_seconds: float = Field(default_factory=lambda: _env_float("REQUEST_DELAY_MAX_SECONDS", 4.0))
    robots_cache_ttl_seconds: int = Field(default_factory=lambda: _env_int("ROBOTS_CACHE_TTL_SECONDS", 3600))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    enable_kafka: bool = Field(default_factory=lambda: _env_bool("ENABLE_KAFKA", False))
    kafka_bootstrap_servers: str = Field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    kafka_client_id: str = Field(default_factory=lambda: os.getenv("KAFKA_CLIENT_ID", "scraper-engine"))
    kafka_consumer_group: str = Field(default_factory=lambda: os.getenv("KAFKA_CONSUMER_GROUP", "scraper-engine"))
    kafka_enable_auto_commit: bool = Field(default_factory=lambda: _env_bool("KAFKA_ENABLE_AUTO_COMMIT", False))

    @field_validator("scrape_interval_max")
    @classmethod
    def validate_interval(cls, value: int, info: object) -> int:
        data = getattr(info, "data", {})
        minimum = data.get("scrape_interval_min", 120)
        if value < minimum:
            raise ValueError("SCRAPE_INTERVAL_MAX must be >= SCRAPE_INTERVAL_MIN")
        return value

    @field_validator("semantic_duplicate_threshold")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        if not 0.0 < value <= 1.0:
            raise ValueError("SEMANTIC_DUPLICATE_THRESHOLD must be between 0 and 1")
        return value

    @property
    def mysql_pool_kwargs(self) -> dict[str, object]:
        return {
            "host": self.mysql_host,
            "port": self.mysql_port,
            "user": self.mysql_user,
            "password": self.mysql_password,
            "db": self.mysql_database,
            "charset": "utf8mb4",
            "autocommit": False,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f"Invalid environment configuration: {exc}") from exc
