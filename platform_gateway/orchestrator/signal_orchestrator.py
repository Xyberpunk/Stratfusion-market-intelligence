from __future__ import annotations

from uuid import uuid4

from shared.events.producer import KafkaEventProducer, KafkaProducerConfig
from shared.events.schemas import FinalSignalGeneratedEvent
from shared.events.topics import KafkaTopic
from shared.observability.metrics import LatencyTimer, MetricsRegistry

from models.schemas import UnifiedPipelineRequest, UnifiedPipelineResponse
from orchestrator.audit_logger import SignalAuditLogger
from orchestrator.dependency_resolver import DependencyResolver
from orchestrator.lifecycle_tracker import LifecycleTracker
from orchestrator.pipeline_state import PipelineState, SignalLifecycleState


class SignalOrchestrator:
    """Central signal lifecycle manager for dashboard-triggered and event-driven pipelines."""

    def __init__(self, kafka_enabled: bool = False, bootstrap_servers: str = "localhost:9092") -> None:
        self.lifecycle = LifecycleTracker()
        self.dependencies = DependencyResolver()
        self.audit = SignalAuditLogger()
        self.metrics = MetricsRegistry()
        self.producer = KafkaEventProducer(
            KafkaProducerConfig(bootstrap_servers=bootstrap_servers, client_id="platform-gateway-orchestrator", enabled=kafka_enabled)
        )

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    def create_pipeline(self, request: UnifiedPipelineRequest) -> PipelineState:
        correlation_id = str(uuid4())
        state = self.lifecycle.create(correlation_id, request.symbol)
        self.audit.record(correlation_id, "pipeline.created", {"symbol": request.symbol})
        self.metrics.inc("pipeline_created_total")
        return state

    def record_state(self, correlation_id: str, state: SignalLifecycleState, event_type: str, payload: dict[str, object]) -> PipelineState:
        updated = self.lifecycle.record(correlation_id, state, event_type, payload)
        self.audit.record(correlation_id, event_type, payload)
        self.metrics.inc(f"pipeline_state_{state.value.lower()}_total")
        return updated

    async def finalize(self, correlation_id: str, response: UnifiedPipelineResponse) -> PipelineState:
        state = self.lifecycle.get(correlation_id)
        if state is None:
            raise ValueError(f"Unknown correlation_id: {correlation_id}")
        missing = self.dependencies.missing(state)
        if missing:
            raise ValueError(f"Cannot finalize incomplete signal; missing states: {', '.join(item.value for item in missing)}")
        with LatencyTimer(self.metrics, "final_signal_publish"):
            event = FinalSignalGeneratedEvent(
                source="platform_gateway",
                symbol=response.symbol,
                correlation_id=correlation_id,
                payload=response.model_dump(mode="json"),
            )
            await self.producer.publish(KafkaTopic.FINAL_SIGNAL_GENERATED, event)
        return self.record_state(correlation_id, SignalLifecycleState.FINALIZED, "final.signal.generated", {"event_id": event.event_id})

    def fail(self, correlation_id: str, error: str) -> PipelineState:
        self.metrics.inc("pipeline_failed_total")
        self.audit.record(correlation_id, "pipeline.failed", {"error": error})
        return self.lifecycle.fail(correlation_id, error)

    def status(self, correlation_id: str) -> PipelineState | None:
        return self.lifecycle.get(correlation_id)
