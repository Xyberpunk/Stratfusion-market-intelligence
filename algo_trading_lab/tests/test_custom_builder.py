from __future__ import annotations

import pytest

from config import Settings
from custom_builder.strategy_builder import CustomStrategyBuilder
from models.schemas import CustomStrategyComponent, CustomStrategyConfig
from strategies.registry import StrategyRegistry


def test_custom_strategy_builder_validates_known_strategies() -> None:
    builder = CustomStrategyBuilder(StrategyRegistry(), Settings(max_strategy_weight=0.5))
    config = CustomStrategyConfig(
        name="My Adaptive NIFTY Strategy",
        strategies=[
            CustomStrategyComponent(name="RSI Reversal", weight=0.2),
            CustomStrategyComponent(name="MACD Momentum", weight=0.2),
        ],
    )
    assert builder.build(config).name == "My Adaptive NIFTY Strategy"


def test_custom_strategy_builder_rejects_unknown_strategy() -> None:
    builder = CustomStrategyBuilder(StrategyRegistry(), Settings(max_strategy_weight=0.5))
    config = CustomStrategyConfig(
        name="Invalid Strategy",
        strategies=[CustomStrategyComponent(name="Unknown Engine", weight=0.2)],
    )
    with pytest.raises(ValueError):
        builder.build(config)
