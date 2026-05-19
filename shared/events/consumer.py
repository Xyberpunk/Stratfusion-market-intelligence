from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from shared.events.schemas import BaseEvent
from shared.events.serializer import EventSerializer


@dataclass(frozen=True)
class KafkaConsumerConfig:
    bootstrap_servers: str = "localhost:9092"
    group_id: str = "stratfusion-consumer"
    enable_auto_commit: bool = False
    enabled: bool = False


class KafkaEventConsumer:
    """Optional Kafka consumer wrapper with canonical event deserialization."""

    def __init__(self, config: KafkaConsumerConfig, topics: list[str]) -> None:
        self.config = config
        self.topics = topics
        self._consumer: object | None = None

    async def start(self) -> None:
        if not self.config.enabled:
            return
        try:
            from aiokafka import AIOKafkaConsumer
        except Exception as exc:
            raise RuntimeError("aiokafka is required when Kafka is enabled") from exc
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.group_id,
            enable_auto_commit=self.config.enable_auto_commit,
        )
        await self._consumer.start()

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()

    async def events(self) -> AsyncIterator[BaseEvent]:
        if self._consumer is None:
            return
        async for message in self._consumer:
            yield EventSerializer.loads(message.value)
