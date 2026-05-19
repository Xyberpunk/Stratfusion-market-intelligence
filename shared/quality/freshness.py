from __future__ import annotations

from datetime import datetime, timedelta, timezone


class FreshnessChecker:
    """Checks whether data is stale for a configured SLA."""

    def is_stale(self, timestamp: datetime, max_age_seconds: int) -> bool:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - timestamp > timedelta(seconds=max_age_seconds)
