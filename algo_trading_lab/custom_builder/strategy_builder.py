from __future__ import annotations

from config import Settings
from custom_builder.config_validator import CustomStrategyConfigValidator
from models.schemas import CustomStrategyConfig
from strategies.registry import StrategyRegistry


class CustomStrategyBuilder:
    """Creates validated custom strategy configurations."""

    def __init__(self, registry: StrategyRegistry, settings: Settings) -> None:
        self.validator = CustomStrategyConfigValidator(registry, settings)

    def build(self, config: CustomStrategyConfig) -> CustomStrategyConfig:
        return self.validator.validate(config)
