from __future__ import annotations

import pytest

from models.schemas import UnifiedPipelineRequest
from orchestrator.pipeline_state import SignalLifecycleState
from orchestrator.signal_orchestrator import SignalOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_lifecycle_finalizes_complete_pipeline() -> None:
    orchestrator = SignalOrchestrator(kafka_enabled=False)
    request = UnifiedPipelineRequest(symbol="INFY", market_data=[])
    state = orchestrator.create_pipeline(request)
    for lifecycle_state in (
        SignalLifecycleState.DATA_COLLECTED,
        SignalLifecycleState.FEATURES_READY,
        SignalLifecycleState.REGIME_READY,
        SignalLifecycleState.STRATEGIES_READY,
        SignalLifecycleState.ENSEMBLE_READY,
        SignalLifecycleState.RISK_READY,
    ):
        orchestrator.record_state(state.correlation_id, lifecycle_state, lifecycle_state.value.lower(), {})
    assert orchestrator.dependencies.ready_to_finalize(orchestrator.status(state.correlation_id))
