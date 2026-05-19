from __future__ import annotations

from data.feature_builder import FeatureBuilder
from execution.signal_context import UnifiedSignalContext
from models.schemas import StrategySignal
from strategies.base import StrategyContext
from strategies.registry import StrategyRegistry


class StrategyRunner:
    """Runs the same strategy implementations in backtest, paper, and live-simulation modes."""

    def __init__(self, registry: StrategyRegistry | None = None, feature_builder: FeatureBuilder | None = None) -> None:
        self.registry = registry or StrategyRegistry()
        self.feature_builder = feature_builder or FeatureBuilder()

    def run(self, context: UnifiedSignalContext, strategy_names: list[str] | None = None) -> list[StrategySignal]:
        features = self.feature_builder.build(context.market_data)
        strategy_context = StrategyContext(
            symbol=context.symbol,
            features=features,
            sentiments=context.sentiments,
            options_chain=context.options_chain,
        )
        return [strategy.generate(strategy_context) for strategy in self.registry.selected(strategy_names)]
