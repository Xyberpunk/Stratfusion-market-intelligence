from __future__ import annotations

from config import Settings
from models.schemas import CustomStrategyConfig
from strategies.registry import StrategyRegistry


class CustomStrategyConfigValidator:
    """Validates user-created strategy combinations."""

    def __init__(self, registry: StrategyRegistry, settings: Settings) -> None:
        self.registry = registry
        self.settings = settings

    def validate(self, config: CustomStrategyConfig) -> CustomStrategyConfig:
        known = set(self.registry.names())
        unknown = [component.name for component in config.strategies if component.name not in known]
        if unknown:
            raise ValueError(f"Unknown strategies: {', '.join(unknown)}")
        for component in config.strategies:
            if component.weight > self.settings.max_strategy_weight:
                raise ValueError(
                    f"{component.name} weight {component.weight:.2f} exceeds max allowed {self.settings.max_strategy_weight:.2f}"
                )
        return config
