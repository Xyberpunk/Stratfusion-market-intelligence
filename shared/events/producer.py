from __future__ import annotations

from dataclasses import dataclass

from shared.events.schemas import BaseEvent
from shared.events.serializer import EventSerializer
from shared.events.topics import KafkaTopic


@dataclass(frozen=True)
class KafkaProducerConfig:
    bootstrap_servers: str = "localhost:9092"
    client_id: str = "stratfusion-producer"
    enabled: bool = False


class KafkaEventProducer:
    """Optional Kafka producer with in-memory fallback for local development."""

    def __init__(self, config: KafkaProducerConfig) -> None:
        self.config = config
        self._producer: object | None = None
        self.published_events: list[tuple[str, BaseEvent]] = []

    async def start(self) -> None:
        if not self.config.enabled:
            return
        try:
            from aiokafka import AIOKafkaProducer
        except Exception as exc:
            raise RuntimeError("aiokafka is required when Kafka is enabled") from exc
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=self.config.client_id,
            value_serializer=EventSerializer.dumps,
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()

    async def publish(self, topic: KafkaTopic | str, event: BaseEvent) -> None:
        topic_name = str(topic)
        self.published_events.append((topic_name, event))
        if self._producer is None:
            return
        await self._producer.send_and_wait(topic_name, event)
