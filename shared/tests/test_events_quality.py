from __future__ import annotations

from shared.events.schemas import MarketOHLCVRawEvent
from shared.events.serializer import EventSerializer
from shared.quality.validators import DataQualityValidator


def test_event_serialization_roundtrip() -> None:
    event = MarketOHLCVRawEvent(source="test", symbol="INFY", payload={"open": 1, "high": 2, "low": 1, "close": 2, "volume": 10})
    loaded = EventSerializer.loads(EventSerializer.dumps(event))
    assert loaded.event_id == event.event_id
    assert loaded.correlation_id == event.correlation_id


def test_data_quality_invalid_ohlc_fails() -> None:
    event = MarketOHLCVRawEvent(source="test", symbol="INFY", payload={"open": 10, "high": 9, "low": 8, "close": 10, "volume": 10})
    result = DataQualityValidator().validate(event)
    assert result.quality_status == "FAIL"
