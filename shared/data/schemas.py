from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NormalizedOHLCV(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=utc_now)
    timeframe: Literal["1m", "5m", "15m"]
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: Literal["NSEPython"] = "NSEPython"


class NormalizedOptionsChain(BaseModel):
    symbol: str
    timestamp: datetime = Field(default_factory=utc_now)
    pcr: float | None = None
    call_oi: float | None = None
    put_oi: float | None = None
    call_oi_change: float | None = None
    put_oi_change: float | None = None
    iv: float | None = None
    iv_change: float | None = None
    max_pain: float | None = None
    underlying_value: float | None = None
    source: Literal["NSEPython"] = "NSEPython"


class MarketDataResult(BaseModel):
    ok: bool
    data: NormalizedOHLCV | None = None
    error: str | None = None


class OptionsChainResult(BaseModel):
    ok: bool
    data: NormalizedOptionsChain | None = None
    error: str | None = None
