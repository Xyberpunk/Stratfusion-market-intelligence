from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logger import get_logger
from models.schemas import MarketDataPoint


class NSEPythonClient:
    """Thin NSEPython adapter with defensive import and normalized output."""

    def __init__(self) -> None:
        self.logger = get_logger("nsepython_client")

    def is_available(self) -> bool:
        try:
            import nsepython  # noqa: F401
        except Exception:
            return False
        return True

    def fetch_quote_snapshot(self, symbol: str) -> MarketDataPoint | None:
        try:
            from nsepython import nse_quote

            data: dict[str, Any] = nse_quote(symbol.upper())
            price_info = data.get("priceInfo", {})
            return MarketDataPoint(
                symbol=symbol.upper(),
                timestamp=datetime.now(timezone.utc),
                open=float(price_info.get("open", price_info.get("lastPrice", 0.0))),
                high=float(price_info.get("intraDayHighLow", {}).get("max", price_info.get("lastPrice", 0.0))),
                low=float(price_info.get("intraDayHighLow", {}).get("min", price_info.get("lastPrice", 0.0))),
                close=float(price_info.get("lastPrice", 0.0)),
                volume=float(data.get("preOpenMarket", {}).get("totalBuyQuantity", 0.0)),
                source="nsepython",
            )
        except Exception as exc:
            self.logger.warning("nse_quote_fetch_failed", symbol=symbol, error=str(exc))
            return None
