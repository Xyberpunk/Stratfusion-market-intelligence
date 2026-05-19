from __future__ import annotations

from collections import defaultdict


class BanditSelectorInterface:
    """Safe experimental bandit selector for paper-trading research only."""

    def __init__(self) -> None:
        self.rewards: dict[str, list[float]] = defaultdict(list)

    def record_reward(self, strategy_name: str, reward: float) -> None:
        self.rewards[strategy_name].append(float(reward))

    def expected_values(self) -> dict[str, float]:
        return {
            name: sum(values) / len(values)
            for name, values in self.rewards.items()
            if values
        }
