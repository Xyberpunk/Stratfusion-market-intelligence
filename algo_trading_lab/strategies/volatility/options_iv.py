from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class OptionsIVStrategy(BaseStrategy):
    name = "Options Chain PCR"
    category = StrategyCategory.VOLATILITY

    def generate(self, context: StrategyContext) -> StrategySignal:
        chain = context.options_chain
        if chain is None:
            return self._hold(context, "Options chain input is unavailable.")
        pcr_bias = max(-1.0, min(1.0, (chain.pcr - 1.0) * 1.5))
        oi_bias = 0.0
        total_oi_change = abs(chain.call_oi_change) + abs(chain.put_oi_change)
        if total_oi_change > 0:
            oi_bias = (chain.put_oi_change - chain.call_oi_change) / total_oi_change
        iv_penalty = -0.15 if chain.iv is not None and chain.iv > 35 else 0.0
        score = max(-1.0, min(1.0, 0.65 * pcr_bias + 0.35 * oi_bias + iv_penalty))
        reason = "Options chain positioning is bullish." if score > 0.15 else "Options chain positioning is bearish." if score < -0.15 else "Options chain positioning is balanced."
        return self._signal(context, score, min(0.85, 0.45 + abs(score) * 0.4), reason, chain.model_dump())
