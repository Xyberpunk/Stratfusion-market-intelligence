from __future__ import annotations

from collections import defaultdict

from config import Settings
from models.enums import MarketRegime, StrategyCategory
from models.schemas import AccuracyOutput, RegimeOutput, StrategySignal
from strategies.registry import StrategyRegistry


class WeightManager:
    """Produces static, custom, regime-adjusted, accuracy-adjusted, confidence-adjusted weights."""

    default_weights: dict[str, float] = {
        "MACD Momentum": 0.25,
        "VWAP": 0.20,
        "RSI Reversal": 0.20,
        "ATR Volatility System": 0.15,
        "FinBERT Sentiment": 0.20,
    }

    def __init__(self, settings: Settings, registry: StrategyRegistry) -> None:
        self.settings = settings
        self.registry = registry
        self.category_by_strategy = {strategy.name: strategy.category for strategy in registry.all()}

    def base_weights(self, signals: list[StrategySignal], custom_weights: dict[str, float] | None = None) -> dict[str, float]:
        if not signals:
            return {}
        weights = {signal.strategy_name: self.default_weights.get(signal.strategy_name, 0.10) for signal in signals}
        if custom_weights:
            for signal in signals:
                if signal.strategy_name in custom_weights:
                    weights[signal.strategy_name] = max(0.0, custom_weights[signal.strategy_name])
        return self._normalize_and_cap(weights)

    def apply_regime(self, weights: dict[str, float], regime: RegimeOutput | None) -> dict[str, float]:
        if regime is None:
            return self._normalize_and_cap(weights)
        multipliers: dict[StrategyCategory, float] = defaultdict(lambda: 1.0)
        if regime.regime in {MarketRegime.TRENDING, MarketRegime.BULLISH, MarketRegime.BEARISH}:
            multipliers[StrategyCategory.MOMENTUM] = 1.35
            multipliers[StrategyCategory.MEAN_REVERSION] = 0.75
        if regime.regime == MarketRegime.SIDEWAYS:
            multipliers[StrategyCategory.MEAN_REVERSION] = 1.4
            multipliers[StrategyCategory.MOMENTUM] = 0.75
        if regime.regime == MarketRegime.HIGH_VOLATILITY:
            multipliers[StrategyCategory.VOLATILITY] = 1.45
            multipliers[StrategyCategory.MOMENTUM] = 0.9
        if regime.regime == MarketRegime.PANIC:
            multipliers[StrategyCategory.VOLATILITY] = 1.25
            multipliers[StrategyCategory.AI_ML] = 0.85
            multipliers[StrategyCategory.MOMENTUM] = 0.7
            multipliers[StrategyCategory.MEAN_REVERSION] = 0.65
        adjusted = {}
        for name, weight in weights.items():
            category = self.category_by_strategy.get(name, StrategyCategory.STATISTICAL)
            adjusted[name] = weight * multipliers[category]
        return self._normalize_and_cap(adjusted)

    def apply_accuracy(self, weights: dict[str, float], accuracy: list[AccuracyOutput]) -> dict[str, float]:
        if not accuracy:
            return self._normalize_and_cap(weights)
        accuracy_by_name = {item.strategy_name: item for item in accuracy}
        adjusted = {}
        for name, weight in weights.items():
            item = accuracy_by_name.get(name)
            multiplier = 1.0 if item is None or item.sample_size < 10 else max(0.6, min(1.35, 0.75 + item.accuracy))
            adjusted[name] = weight * multiplier
        return self._normalize_and_cap(adjusted)

    def apply_confidence(self, weights: dict[str, float], signals: list[StrategySignal]) -> dict[str, float]:
        confidence = {signal.strategy_name: signal.confidence for signal in signals}
        adjusted = {name: weight * (0.5 + confidence.get(name, 0.5)) for name, weight in weights.items()}
        return self._normalize_and_cap(adjusted)

    def _normalize_and_cap(self, weights: dict[str, float]) -> dict[str, float]:
        positive = {name: max(0.0, value) for name, value in weights.items()}
        if not positive:
            return {}
        total = sum(positive.values())
        if total <= 0:
            equal = 1.0 / len(positive)
            positive = {name: equal for name in positive}
        else:
            positive = {name: value / total for name, value in positive.items()}
        return self._cap_with_floor(positive)

    def _cap_with_floor(self, weights: dict[str, float]) -> dict[str, float]:
        floor = 0.05 if len(weights) * 0.05 < 1.0 else 0.0
        cap = self.settings.max_strategy_weight
        bounded = {name: min(max(value, floor), cap) for name, value in weights.items()}
        for _ in range(8):
            total = sum(bounded.values())
            if total <= 0:
                equal = 1.0 / len(bounded)
                return {name: equal for name in bounded}
            bounded = {name: value / total for name, value in bounded.items()}
            overflow = {name: value for name, value in bounded.items() if value > cap}
            under = {name: value for name, value in bounded.items() if value <= cap}
            if not overflow:
                return {name: max(value, floor) for name, value in bounded.items()}
            fixed_total = len(overflow) * cap
            remaining = max(0.0, 1.0 - fixed_total)
            under_total = sum(under.values()) or 1.0
            bounded = {name: cap for name in overflow}
            bounded.update({name: max(floor, value / under_total * remaining) for name, value in under.items()})
        total = sum(bounded.values()) or 1.0
        normalized = {name: min(value / total, cap) for name, value in bounded.items()}
        remainder = 1.0 - sum(normalized.values())
        receivers = [name for name, value in normalized.items() if value < cap]
        if receivers and remainder > 0:
            add = remainder / len(receivers)
            for name in receivers:
                normalized[name] = min(cap, normalized[name] + add)
        return normalized
