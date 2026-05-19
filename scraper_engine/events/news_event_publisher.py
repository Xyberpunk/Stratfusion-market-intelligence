from __future__ import annotations

from shared.events.producer import KafkaEventProducer, KafkaProducerConfig
from shared.events.schemas import NewsCleanedEvent, NewsRawEvent
from shared.events.topics import KafkaTopic
from shared.quality.source_reliability import SourceReliabilityScorer
from shared.quality.validators import DataQualityValidator

from models import NewsItem


class NewsEventPublisher:
    """Publishes scraper news lifecycle events while preserving MySQL and Chroma persistence."""

    def __init__(self, *, enabled: bool = False, bootstrap_servers: str = "localhost:9092") -> None:
        self.producer = KafkaEventProducer(
            KafkaProducerConfig(bootstrap_servers=bootstrap_servers, client_id="scraper-engine", enabled=enabled)
        )
        self.quality = DataQualityValidator()
        self.reliability = SourceReliabilityScorer()

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def publish_news_item(self, item: NewsItem) -> None:
        raw = NewsRawEvent(
            source=item.source,
            symbol=None,
            payload={
                "title": item.title,
                "url": item.url,
                "summary": item.summary,
                "published_at": item.published_at,
                "source_reliability_score": self.reliability.score(item.source),
            },
        )
        quality = self.quality.validate(raw)
        self.reliability.update(item.source, quality.quality_status != "FAIL")
        await self.producer.publish(KafkaTopic.NEWS_RAW, raw)
        if quality.quality_status == "FAIL":
            await self.producer.publish(
                KafkaTopic.SYSTEM_DEAD_LETTER,
                raw.model_copy(update={"event_type": "system.dead_letter", "payload": {"quality": quality.model_dump(mode="json"), "original": raw.payload}}),
            )
            return
        cleaned = NewsCleanedEvent(
            source=item.source,
            correlation_id=raw.correlation_id,
            payload={
                **item.raw_json(),
                "quality": quality.model_dump(mode="json"),
                "source_reliability_score": self.reliability.score(item.source),
            },
        )
        await self.producer.publish(KafkaTopic.NEWS_CLEANED, cleaned)
