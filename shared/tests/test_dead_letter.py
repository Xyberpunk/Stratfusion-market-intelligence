from __future__ import annotations

import pytest

from shared.events.dead_letter import DeadLetterPublisher
from shared.events.producer import KafkaEventProducer, KafkaProducerConfig
from shared.events.schemas import NewsRawEvent


@pytest.mark.asyncio
async def test_dead_letter_publisher_preserves_correlation_id() -> None:
    producer = KafkaEventProducer(KafkaProducerConfig(enabled=False))
    original = NewsRawEvent(source="test", symbol="INFY", payload={"title": "x"})
    event = await DeadLetterPublisher(producer).publish_failure(original, "news.raw", RuntimeError("bad event"))
    assert event.correlation_id == original.correlation_id
    assert producer.published_events[0][0] == "system.dead_letter"
