from __future__ import annotations

from models.schemas import PaperTradeFeedback


class FeedbackStore:
    """Stores paper-trading feedback used for reward tracking and future learning."""

    def __init__(self) -> None:
        self._items: list[PaperTradeFeedback] = []

    def add(self, feedback: PaperTradeFeedback) -> None:
        self._items.append(feedback)

    def by_strategy(self, strategy_name: str) -> list[PaperTradeFeedback]:
        return [item for item in self._items if item.strategy_name == strategy_name]

    def all(self) -> list[PaperTradeFeedback]:
        return list(self._items)
