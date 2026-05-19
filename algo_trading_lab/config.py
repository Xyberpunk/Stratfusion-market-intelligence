from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "127.0.0.1"))
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8080")))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    mysql_host: str = Field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    mysql_port: int = Field(default_factory=lambda: int(os.getenv("MYSQL_PORT", "3306")))
    mysql_user: str = Field(default_factory=lambda: os.getenv("MYSQL_USER", "trading_user"))
    mysql_password: str = Field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    mysql_database: str = Field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "algo_trading_lab"))
    mysql_enabled: bool = Field(default_factory=lambda: _bool_env("MYSQL_ENABLED", False))

    default_capital: float = Field(default_factory=lambda: float(os.getenv("DEFAULT_CAPITAL", "1000000")))
    default_risk_per_trade: float = Field(default_factory=lambda: float(os.getenv("DEFAULT_RISK_PER_TRADE", "0.01")))
    max_strategy_weight: float = Field(default_factory=lambda: float(os.getenv("MAX_STRATEGY_WEIGHT", "0.35")))
    min_ensemble_confidence: float = Field(default_factory=lambda: float(os.getenv("MIN_ENSEMBLE_CONFIDENCE", "0.55")))
    max_drawdown_limit: float = Field(default_factory=lambda: float(os.getenv("MAX_DRAWDOWN_LIMIT", "0.15")))
    high_volatility_atr_pct: float = Field(default_factory=lambda: float(os.getenv("HIGH_VOLATILITY_ATR_PCT", "0.03")))
    panic_drawdown_pct: float = Field(default_factory=lambda: float(os.getenv("PANIC_DRAWDOWN_PCT", "-0.04")))

    @field_validator("max_strategy_weight")
    @classmethod
    def validate_weight_cap(cls, value: float) -> float:
        if not 0.05 <= value <= 1.0:
            raise ValueError("MAX_STRATEGY_WEIGHT must be between 0.05 and 1.0")
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
    return Settings()
