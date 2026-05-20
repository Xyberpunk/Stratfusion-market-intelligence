from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class NSEPythonClient:
    """Defensive NSEPython adapter used as the platform market heartbeat."""

    @retry(wait=wait_exponential_jitter(initial=0.5, max=6), stop=stop_after_attempt(3), reraise=True)
    def quote(self, symbol: str) -> dict[str, Any]:
        from nsepython import nse_quote

        return dict(nse_quote(symbol.upper()))

    @retry(wait=wait_exponential_jitter(initial=0.5, max=6), stop=stop_after_attempt(3), reraise=True)
    def option_chain(self, symbol: str) -> dict[str, Any]:
        from nsepython import nse_optionchain_scrapper

        return dict(nse_optionchain_scrapper(symbol.upper()))

    def quote_to_ohlcv(self, symbol: str, payload: dict[str, Any], timeframe: str) -> dict[str, Any]:
        price_info = payload.get("priceInfo", {})
        last_price = float(price_info.get("lastPrice") or price_info.get("close") or 0.0)
        intraday = price_info.get("intraDayHighLow", {}) or {}
        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(timezone.utc),
            "timeframe": timeframe,
            "open": float(price_info.get("open") or last_price),
            "high": float(intraday.get("max") or price_info.get("intraDayHigh") or last_price),
            "low": float(intraday.get("min") or price_info.get("intraDayLow") or last_price),
            "close": last_price,
            "volume": float(payload.get("marketDeptOrderBook", {}).get("totalTradedVolume") or payload.get("preOpenMarket", {}).get("totalTradedVolume") or 0.0),
            "source": "NSEPython",
        }
