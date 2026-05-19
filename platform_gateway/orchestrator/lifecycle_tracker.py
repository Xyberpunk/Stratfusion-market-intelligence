from __future__ import annotations

from datetime import datetime, timezone

from platform_gateway.orchestrator.pipeline_state import PipelineEventRecord, PipelineState, SignalLifecycleState


class LifecycleTracker:
    """Tracks end-to-end signal pipeline lifecycle by correlation id."""

    def __init__(self) -> None:
        self._states: dict[str, PipelineState] = {}

    def create(self, correlation_id: str, symbol: str) -> PipelineState:
        state = PipelineState(correlation_id=correlation_id, symbol=symbol.upper(), state=SignalLifecycleState.CREATED)
        self._states[correlation_id] = state
        self.record(correlation_id, SignalLifecycleState.CREATED, "pipeline.created", {})
        return state

    def record(self, correlation_id: str, lifecycle_state: SignalLifecycleState, event_type: str, payload: dict[str, object]) -> PipelineState:
        state = self._states[correlation_id]
        if lifecycle_state not in state.completed_states and lifecycle_state not in {SignalLifecycleState.CREATED, SignalLifecycleState.FAILED, SignalLifecycleState.EXPIRED}:
            state.completed_states.append(lifecycle_state)
        state.state = lifecycle_state
        state.updated_at = datetime.now(timezone.utc)
        state.events.append(PipelineEventRecord(correlation_id=correlation_id, state=lifecycle_state, event_type=event_type, payload=payload))
        return state

    def fail(self, correlation_id: str, error: str) -> PipelineState:
        state = self._states[correlation_id]
        state.error = error
        return self.record(correlation_id, SignalLifecycleState.FAILED, "pipeline.failed", {"error": error})

    def get(self, correlation_id: str) -> PipelineState | None:
        return self._states.get(correlation_id)
