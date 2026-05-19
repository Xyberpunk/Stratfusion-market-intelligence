from __future__ import annotations

from shared.events.producer import KafkaEventProducer
from shared.events.schemas import BaseEvent, DeadLetterEvent
from shared.events.topics import KafkaTopic


class DeadLetterPublisher:
    """Publishes failed events to the shared dead-letter topic."""

    def __init__(self, producer: KafkaEventProducer) -> None:
        self.producer = producer

    async def publish_failure(self, original: BaseEvent, topic: str, error: Exception, retryable: bool = False) -> DeadLetterEvent:
        event = DeadLetterEvent(
            source="dead_letter_publisher",
            symbol=original.symbol,
            correlation_id=original.correlation_id,
            payload={"original_event": original.model_dump(mode="json")},
            original_topic=topic,
            error=str(error),
            retryable=retryable,
        )
        await self.producer.publish(KafkaTopic.SYSTEM_DEAD_LETTER, event)
        return event
