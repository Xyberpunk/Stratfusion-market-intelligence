from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from shared.events.schemas import BaseEvent


class QualityStatus(str):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class DataQualityResult(BaseModel):
    event_id: str
    quality_status: str
    issues: list[str] = Field(default_factory=list)
    source_reliability_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityValidator:
    """Validates incoming event payloads before downstream processing."""

    def validate(self, event: BaseEvent) -> DataQualityResult:
        issues: list[str] = []
        payload = event.payload
        if event.event_type in {"market.ohlcv.raw", "features.generated"}:
            issues.extend(self._validate_ohlcv(payload))
        if event.event_type in {"market.options.raw"}:
            issues.extend(self._validate_options(payload))
        if event.event_type in {"news.raw", "news.cleaned"}:
            issues.extend(self._validate_news(payload))
        if event.timestamp > datetime.now(timezone.utc):
            issues.append("event timestamp is in the future")
        reliability = float(payload.get("source_reliability_score", 0.85))
        if reliability < 0.4:
            issues.append("low source reliability")
        status = QualityStatus.FAIL if any("invalid" in issue or "missing" in issue for issue in issues) else QualityStatus.WARN if issues else QualityStatus.PASS
        return DataQualityResult(
            event_id=event.event_id,
            quality_status=str(status),
            issues=issues,
            source_reliability_score=max(0.0, min(1.0, reliability)),
        )

    @staticmethod
    def _validate_ohlcv(payload: dict[str, Any]) -> list[str]:
        issues: list[str] = []
        for key in ("open", "high", "low", "close"):
            if key not in payload:
                issues.append(f"missing {key}")
        if issues:
            return issues
        open_price = float(payload["open"])
        high = float(payload["high"])
        low = float(payload["low"])
        close = float(payload["close"])
        if min(open_price, high, low, close) <= 0:
            issues.append("invalid non-positive price")
        if high < max(open_price, low, close):
            issues.append("invalid OHLC candle: high below price component")
        if low > min(open_price, high, close):
            issues.append("invalid OHLC candle: low above price component")
        if float(payload.get("volume", 0.0)) < 0:
            issues.append("invalid negative volume")
        return issues

    @staticmethod
    def _validate_options(payload: dict[str, Any]) -> list[str]:
        issues: list[str] = []
        if float(payload.get("pcr", 0.0)) < 0:
            issues.append("invalid negative PCR")
        if payload.get("iv") is not None and float(payload["iv"]) < 0:
            issues.append("invalid negative IV")
        return issues

    @staticmethod
    def _validate_news(payload: dict[str, Any]) -> list[str]:
        title = str(payload.get("title") or payload.get("text") or "").strip()
        if not title:
            return ["missing empty news headline"]
        return []
