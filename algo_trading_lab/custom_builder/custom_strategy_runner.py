from __future__ import annotations

from models.schemas import CustomStrategyConfig, StrategySignal
from strategies.base import StrategyContext
from strategies.registry import StrategyRegistry


class CustomStrategyRunner:
    """Runs the selected components of a custom strategy."""

    def __init__(self, registry: StrategyRegistry) -> None:
        self.registry = registry

    def run(self, config: CustomStrategyConfig, context: StrategyContext) -> tuple[list[StrategySignal], dict[str, float]]:
        signals: list[StrategySignal] = []
        weights: dict[str, float] = {}
        for component in config.strategies:
            strategy = self.registry.get(component.name)
            signals.append(strategy.generate(context))
            weights[component.name] = component.weight
        return signals, weights
