from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SignalLifecycleState(StrEnum):
    CREATED = "CREATED"
    DATA_COLLECTED = "DATA_COLLECTED"
    FEATURES_READY = "FEATURES_READY"
    REGIME_READY = "REGIME_READY"
    STRATEGIES_READY = "STRATEGIES_READY"
    ENSEMBLE_READY = "ENSEMBLE_READY"
    RISK_READY = "RISK_READY"
    FINALIZED = "FINALIZED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class PipelineEventRecord(BaseModel):
    correlation_id: str
    state: SignalLifecycleState
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class PipelineState(BaseModel):
    correlation_id: str
    symbol: str
    state: SignalLifecycleState
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    required_states: list[SignalLifecycleState] = Field(
        default_factory=lambda: [
            SignalLifecycleState.DATA_COLLECTED,
            SignalLifecycleState.FEATURES_READY,
            SignalLifecycleState.REGIME_READY,
            SignalLifecycleState.STRATEGIES_READY,
            SignalLifecycleState.ENSEMBLE_READY,
            SignalLifecycleState.RISK_READY,
        ]
    )
    completed_states: list[SignalLifecycleState] = Field(default_factory=list)
    events: list[PipelineEventRecord] = Field(default_factory=list)
    error: str | None = None
