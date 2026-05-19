from __future__ import annotations


class SourceReliabilityScorer:
    """Tracks source reliability penalties from quality failures."""

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def score(self, source: str) -> float:
        return self._scores.get(source, 0.85)

    def update(self, source: str, passed: bool) -> float:
        current = self.score(source)
        updated = min(1.0, current + 0.02) if passed else max(0.0, current - 0.08)
        self._scores[source] = updated
        return updated
