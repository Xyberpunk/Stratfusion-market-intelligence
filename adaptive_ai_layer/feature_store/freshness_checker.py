from __future__ import annotations

from datetime import datetime, timedelta, timezone


class FeatureFreshnessChecker:
    """Classifies feature freshness for serving and risk gating."""

    def status(self, timestamp: datetime, max_age_seconds: int = 900) -> str:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - timestamp
        if age <= timedelta(seconds=max_age_seconds):
            return "FRESH"
        if age <= timedelta(seconds=max_age_seconds * 4):
            return "STALE"
        return "EXPIRED"
