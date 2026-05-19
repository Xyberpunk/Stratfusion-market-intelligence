from __future__ import annotations

from platform_gateway.orchestrator.pipeline_state import PipelineState, SignalLifecycleState


class DependencyResolver:
    """Prevents final signals from being emitted until required lifecycle states are complete."""

    def missing(self, state: PipelineState) -> list[SignalLifecycleState]:
        completed = set(state.completed_states)
        return [required for required in state.required_states if required not in completed]

    def ready_to_finalize(self, state: PipelineState) -> bool:
        return not self.missing(state)
