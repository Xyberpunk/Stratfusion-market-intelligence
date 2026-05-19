from __future__ import annotations

from typing import Protocol


class OnlineLearner(Protocol):
    """Protocol for safe online learning experiments."""

    def partial_fit(self, features: list[float], target: str) -> None:
        ...

    def predict(self, features: list[float]) -> str:
        ...


class OnlineLearningInterface:
    """Adapter that keeps online learning experimental and isolated from live trading decisions."""

    def __init__(self, learner: OnlineLearner | None = None) -> None:
        self.learner = learner

    def available(self) -> bool:
        return self.learner is not None

    def update(self, features: list[float], target: str) -> None:
        if self.learner is None:
            return
        self.learner.partial_fit(features, target)
