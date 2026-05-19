from __future__ import annotations

from collections import defaultdict

from models.schemas import AccuracyOutput


class RegimePerformanceAnalyzer:
    """Summarizes strategy performance by regime."""

    def best_by_regime(self, outputs: list[AccuracyOutput]) -> dict[str, AccuracyOutput]:
        grouped: dict[str, list[AccuracyOutput]] = defaultdict(list)
        for output in outputs:
            grouped[output.regime].append(output)
        return {
            regime: max(items, key=lambda item: (item.accuracy, item.sample_size))
            for regime, items in grouped.items()
            if items
        }
