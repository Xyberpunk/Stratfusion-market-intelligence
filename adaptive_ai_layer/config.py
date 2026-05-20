from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

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
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8090")))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    mysql_enabled: bool = Field(default_factory=lambda: _bool_env("MYSQL_ENABLED", False))
    mysql_host: str = Field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    mysql_port: int = Field(default_factory=lambda: int(os.getenv("MYSQL_PORT", "3306")))
    mysql_user: str = Field(default_factory=lambda: os.getenv("MYSQL_USER", "adaptive_ai_user"))
    mysql_password: str = Field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    mysql_database: str = Field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "adaptive_ai_layer"))

    model_dir: Path = Field(default_factory=lambda: Path(os.getenv("MODEL_DIR", "./model_artifacts")))
    finbert_model_name: str = Field(default_factory=lambda: os.getenv("FINBERT_MODEL_NAME", "ProsusAI/finbert"))
    finbert_enabled: bool = Field(default_factory=lambda: _bool_env("FINBERT_ENABLED", False))
    finbert_batch_size: int = Field(default_factory=lambda: int(os.getenv("FINBERT_BATCH_SIZE", "16")))

    regime_confidence_floor: float = Field(default_factory=lambda: float(os.getenv("REGIME_CONFIDENCE_FLOOR", "0.35")))
    high_volatility_percentile: float = Field(default_factory=lambda: float(os.getenv("HIGH_VOLATILITY_PERCENTILE", "0.8")))
    regime_adx_trending: float = Field(default_factory=lambda: float(os.getenv("REGIME_ADX_TRENDING", "25")))
    regime_adx_sideways: float = Field(default_factory=lambda: float(os.getenv("REGIME_ADX_SIDEWAYS", "18")))
    regime_atr_high_vol_percentile: float = Field(default_factory=lambda: float(os.getenv("REGIME_ATR_HIGH_VOL_PERCENTILE", "0.85")))
    regime_realized_vol_high: float = Field(default_factory=lambda: float(os.getenv("REGIME_REALIZED_VOL_HIGH", "0.035")))
    regime_bollinger_compression_threshold: float = Field(default_factory=lambda: float(os.getenv("REGIME_BOLLINGER_COMPRESSION_THRESHOLD", "0.04")))
    regime_ema_slope_trend_threshold: float = Field(default_factory=lambda: float(os.getenv("REGIME_EMA_SLOPE_TREND_THRESHOLD", "0.001")))
    panic_return_threshold: float = Field(default_factory=lambda: float(os.getenv("PANIC_RETURN_THRESHOLD", "-0.04")))
    low_liquidity_volume_ratio: float = Field(default_factory=lambda: float(os.getenv("LOW_LIQUIDITY_VOLUME_RATIO", "0.45")))
    max_strategy_weight: float = Field(default_factory=lambda: float(os.getenv("MAX_STRATEGY_WEIGHT", "0.35")))
    anomaly_zscore_threshold: float = Field(default_factory=lambda: float(os.getenv("ANOMALY_ZSCORE_THRESHOLD", "3.0")))
    enable_feature_store: bool = Field(default_factory=lambda: _bool_env("ENABLE_FEATURE_STORE", True))
    enable_model_registry: bool = Field(default_factory=lambda: _bool_env("ENABLE_MODEL_REGISTRY", True))
    enable_observability: bool = Field(default_factory=lambda: _bool_env("ENABLE_OBSERVABILITY", True))
    enable_kafka: bool = Field(default_factory=lambda: _bool_env("ENABLE_KAFKA", False))
    kafka_bootstrap_servers: str = Field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    kafka_client_id: str = Field(default_factory=lambda: os.getenv("KAFKA_CLIENT_ID", "adaptive-ai-layer"))
    kafka_consumer_group: str = Field(default_factory=lambda: os.getenv("KAFKA_CONSUMER_GROUP", "adaptive-ai-layer"))
    kafka_enable_auto_commit: bool = Field(default_factory=lambda: _bool_env("KAFKA_ENABLE_AUTO_COMMIT", False))

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
    settings = Settings()
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    return settings
