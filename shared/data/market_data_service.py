from __future__ import annotations

from shared.data.nsepython_client import NSEPythonClient
from shared.data.options_chain_service import OptionsChainService
from shared.data.schemas import MarketDataResult, NormalizedOHLCV, OptionsChainResult
from shared.events.producer import KafkaEventProducer
from shared.events.schemas import MarketOHLCVRawEvent, MarketOptionsRawEvent
from shared.events.topics import KafkaTopic


class MarketDataService:
    """Fetches NSEPython live market data and publishes optional Kafka events."""

    def __init__(self, client: NSEPythonClient | None = None, producer: KafkaEventProducer | None = None) -> None:
        self.client = client or NSEPythonClient()
        self.options = OptionsChainService()
        self.producer = producer

    async def fetch_live_ohlcv(self, symbol: str, timeframe: str = "1m") -> MarketDataResult:
        if timeframe not in {"1m", "5m", "15m"}:
            return MarketDataResult(ok=False, error=f"unsupported timeframe: {timeframe}")
        try:
            payload = self.client.quote(symbol)
            data = NormalizedOHLCV.model_validate(self.client.quote_to_ohlcv(symbol, payload, timeframe))
            if self.producer:
                await self.producer.publish(
                    KafkaTopic.MARKET_OHLCV_RAW,
                    MarketOHLCVRawEvent(source="NSEPython", symbol=data.symbol, payload=data.model_dump(mode="json")),
                )
            return MarketDataResult(ok=True, data=data)
        except Exception as exc:
            return MarketDataResult(ok=False, error=str(exc))

    async def fetch_options_chain(self, symbol: str) -> OptionsChainResult:
        try:
            payload = self.client.option_chain(symbol)
            result = self.options.normalize(symbol, payload)
            if result.ok and result.data and self.producer:
                await self.producer.publish(
                    KafkaTopic.MARKET_OPTIONS_RAW,
                    MarketOptionsRawEvent(source="NSEPython", symbol=result.data.symbol, payload=result.data.model_dump(mode="json")),
                )
            return result
        except Exception as exc:
            return OptionsChainResult(ok=False, error=str(exc))
