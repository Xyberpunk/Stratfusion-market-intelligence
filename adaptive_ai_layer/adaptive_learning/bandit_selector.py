from __future__ import annotations

import math
from collections import defaultdict


class SafeBanditSelector:
    """Upper-confidence-bound selector for paper-trading strategy research."""

    def __init__(self) -> None:
        self.counts: dict[str, int] = defaultdict(int)
        self.rewards: dict[str, float] = defaultdict(float)

    def update(self, strategy_name: str, reward: float) -> None:
        self.counts[strategy_name] += 1
        self.rewards[strategy_name] += reward

    def scores(self) -> dict[str, float]:
        total = sum(self.counts.values()) or 1
        result: dict[str, float] = {}
        for strategy, count in self.counts.items():
            mean_reward = self.rewards[strategy] / max(count, 1)
            exploration = math.sqrt(2 * math.log(total + 1) / max(count, 1))
            result[strategy] = mean_reward + exploration
        return result
