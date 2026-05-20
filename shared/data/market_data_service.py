from __future__ import annotations

from shared.data.candle_aggregator import CandleAggregator
from shared.data.candle_store import InMemoryCandleStore
from shared.data.nsepython_client import NSEPythonClient
from shared.data.options_chain_service import OptionsChainService
from shared.data.schemas import MarketDataResult, NormalizedOHLCV, OptionsChainResult
from shared.events.producer import KafkaEventProducer
from shared.events.schemas import MarketOHLCVRawEvent, MarketOptionsRawEvent
from shared.events.topics import KafkaTopic


class MarketDataService:
    """Fetches NSEPython live market data and publishes optional Kafka events."""

    def __init__(
        self,
        client: NSEPythonClient | None = None,
        producer: KafkaEventProducer | None = None,
        aggregator: CandleAggregator | None = None,
        candle_store: InMemoryCandleStore | None = None,
    ) -> None:
        self.client = client or NSEPythonClient()
        self.options = OptionsChainService()
        self.producer = producer
        self.aggregator = aggregator or CandleAggregator()
        self.candle_store = candle_store or InMemoryCandleStore()

    async def fetch_live_ohlcv(self, symbol: str, timeframe: str = "1m") -> MarketDataResult:
        if timeframe not in {"1m", "5m", "15m"}:
            return MarketDataResult(ok=False, error=f"unsupported timeframe: {timeframe}")
        try:
            payload = self.client.quote(symbol)
            snapshot = NormalizedOHLCV.model_validate(self.client.quote_to_ohlcv(symbol, payload, timeframe))
            updated = self.aggregator.add_tick(
                symbol=snapshot.symbol,
                price=snapshot.close,
                volume=snapshot.volume,
                timestamp=snapshot.timestamp,
            )
            self.candle_store.save_many(updated)
            latest = self.candle_store.latest(snapshot.symbol, timeframe, limit=1)
            data = latest[-1] if latest else snapshot
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
