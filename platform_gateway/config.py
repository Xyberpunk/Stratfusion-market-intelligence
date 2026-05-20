from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "127.0.0.1"))
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8070")))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    adaptive_ai_url: str = Field(default_factory=lambda: os.getenv("ADAPTIVE_AI_URL", "http://127.0.0.1:8090"))
    algo_lab_url: str = Field(default_factory=lambda: os.getenv("ALGO_LAB_URL", "http://127.0.0.1:8080"))
    request_timeout_seconds: float = Field(default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT_SECONDS", "45")))
    enable_kafka: bool = Field(default_factory=lambda: _bool_env("ENABLE_KAFKA", False))
    kafka_bootstrap_servers: str = Field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    kafka_client_id: str = Field(default_factory=lambda: os.getenv("KAFKA_CLIENT_ID", "platform-gateway"))
    kafka_consumer_group: str = Field(default_factory=lambda: os.getenv("KAFKA_CONSUMER_GROUP", "platform-gateway"))
    kafka_enable_auto_commit: bool = Field(default_factory=lambda: _bool_env("KAFKA_ENABLE_AUTO_COMMIT", False))

    scraper_mysql_enabled: bool = Field(default_factory=lambda: _bool_env("SCRAPER_MYSQL_ENABLED", False))
    scraper_mysql_host: str = Field(default_factory=lambda: os.getenv("SCRAPER_MYSQL_HOST", "localhost"))
    scraper_mysql_port: int = Field(default_factory=lambda: int(os.getenv("SCRAPER_MYSQL_PORT", "3306")))
    scraper_mysql_user: str = Field(default_factory=lambda: os.getenv("SCRAPER_MYSQL_USER", "stock_user"))
    scraper_mysql_password: str = Field(default_factory=lambda: os.getenv("SCRAPER_MYSQL_PASSWORD", ""))
    scraper_mysql_database: str = Field(default_factory=lambda: os.getenv("SCRAPER_MYSQL_DATABASE", "stock_news"))
    pipeline_mysql_enabled: bool = Field(default_factory=lambda: _bool_env("PIPELINE_MYSQL_ENABLED", False))
    pipeline_mysql_database: str = Field(default_factory=lambda: os.getenv("PIPELINE_MYSQL_DATABASE", "stratfusion_pipeline"))

    @property
    def scraper_mysql_kwargs(self) -> dict[str, object]:
        return {
            "host": self.scraper_mysql_host,
            "port": self.scraper_mysql_port,
            "user": self.scraper_mysql_user,
            "password": self.scraper_mysql_password,
            "db": self.scraper_mysql_database,
            "charset": "utf8mb4",
            "autocommit": True,
        }

    @property
    def pipeline_mysql_kwargs(self) -> dict[str, object]:
        kwargs = self.scraper_mysql_kwargs.copy()
        kwargs["db"] = self.pipeline_mysql_database
        return kwargs


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
