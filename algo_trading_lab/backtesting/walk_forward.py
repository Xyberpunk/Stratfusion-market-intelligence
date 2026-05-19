from __future__ import annotations

from models.schemas import MarketDataPoint


class WalkForwardSplitter:
    """Creates deterministic train/test splits for walk-forward testing."""

    def split(self, points: list[MarketDataPoint], train_ratio: float) -> tuple[list[MarketDataPoint], list[MarketDataPoint]]:
        ordered = sorted(points, key=lambda point: point.timestamp)
        cut = max(1, min(len(ordered) - 1, int(len(ordered) * train_ratio)))
        return ordered[:cut], ordered[cut:]
