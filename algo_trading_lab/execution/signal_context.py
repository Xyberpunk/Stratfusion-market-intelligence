from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from execution.mode import ExecutionMode
from models.schemas import MarketDataPoint, OptionsChainInput, SentimentInput


class UnifiedSignalContext(BaseModel):
    """Serializable context shared by backtest, paper, and live-simulation execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    symbol: str
    mode: ExecutionMode
    market_data: list[MarketDataPoint]
    sentiments: list[SentimentInput]
    options_chain: OptionsChainInput | None = None
    capital: float = 1_000_000.0
    risk_per_trade: float = 0.01
