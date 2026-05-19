from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from models.enums import StrategyCategory, TradingSignal
from models.schemas import OptionsChainInput, SentimentInput, StrategySignal


@dataclass(frozen=True)
class StrategyContext:
    symbol: str
    features: pd.DataFrame
    sentiments: list[SentimentInput]
    options_chain: OptionsChainInput | None = None


class BaseStrategy(ABC):
    """Base class for independent strategy engines."""

    name: str
    category: StrategyCategory

    @abstractmethod
    def generate(self, context: StrategyContext) -> StrategySignal:
        raise NotImplementedError

    def _latest_timestamp(self, context: StrategyContext) -> datetime:
        if context.features.empty:
            return datetime.now(timezone.utc)
        value = context.features.iloc[-1]["timestamp"]
        return pd.to_datetime(value).to_pydatetime()

    def _signal(self, context: StrategyContext, score: float, confidence: float, reason: str, metadata: dict[str, object]) -> StrategySignal:
        bounded_score = max(-1.0, min(1.0, float(score)))
        bounded_confidence = max(0.0, min(1.0, float(confidence)))
        if bounded_score > 0.15:
            signal = TradingSignal.BUY
        elif bounded_score < -0.15:
            signal = TradingSignal.SELL
        else:
            signal = TradingSignal.HOLD
        return StrategySignal(
            strategy_name=self.name,
            symbol=context.symbol.upper(),
            timestamp=self._latest_timestamp(context),
            signal=signal,
            confidence=bounded_confidence,
            score=bounded_score,
            reason=reason,
            metadata=metadata,
        )

    def _hold(self, context: StrategyContext, reason: str) -> StrategySignal:
        return self._signal(context, 0.0, 0.1, reason, {})

    def _has_rows(self, context: StrategyContext, minimum: int = 2) -> bool:
        return len(context.features.index) >= minimum
