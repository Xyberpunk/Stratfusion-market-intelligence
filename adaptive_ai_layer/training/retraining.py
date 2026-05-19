from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.schemas import ModelRegistryItem


class RetrainingPolicy:
    """Determines whether a model should be retrained."""

    def should_retrain(self, item: ModelRegistryItem | None, min_accuracy: float = 0.52, max_age_days: int = 14) -> bool:
        if item is None:
            return True
        if item.metrics.get("accuracy", 0.0) < min_accuracy:
            return True
        return item.created_at < datetime.now(timezone.utc) - timedelta(days=max_age_days)
