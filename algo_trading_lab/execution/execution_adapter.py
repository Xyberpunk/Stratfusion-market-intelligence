from __future__ import annotations

from execution.mode import ExecutionMode
from execution.signal_context import UnifiedSignalContext
from models.schemas import GenerateSignalRequest


class ExecutionAdapter:
    """Adapts API/backtest requests into the unified execution context."""

    def from_generate_signal(self, request: GenerateSignalRequest, mode: ExecutionMode = ExecutionMode.PAPER) -> UnifiedSignalContext:
        return UnifiedSignalContext(
            symbol=request.symbol,
            mode=mode,
            market_data=request.market_data,
            sentiments=request.sentiments,
            options_chain=request.options_chain,
            capital=request.capital,
            risk_per_trade=request.risk_per_trade,
        )
