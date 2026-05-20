from __future__ import annotations

import pytest

from shared.data.market_data_service import MarketDataService


class FailingClient:
    def quote(self, symbol: str):
        raise RuntimeError("nse down")

    def option_chain(self, symbol: str):
        raise RuntimeError("nse down")


@pytest.mark.asyncio
async def test_market_data_service_safe_failure() -> None:
    service = MarketDataService(client=FailingClient())
    result = await service.fetch_live_ohlcv("INFY")
    assert result.ok is False
    assert "nse down" in result.error
