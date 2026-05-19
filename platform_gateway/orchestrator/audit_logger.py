from __future__ import annotations

from typing import Any

from shared.observability.audit import AuditLog, AuditRecord


class SignalAuditLogger:
    """Audit trail adapter for signal orchestration events."""

    def __init__(self) -> None:
        self.audit = AuditLog()

    def record(self, correlation_id: str, event_type: str, payload: dict[str, Any]) -> None:
        self.audit.append(AuditRecord(correlation_id=correlation_id, event_type=event_type, service="platform_gateway", payload=payload))

    def trail(self, correlation_id: str) -> list[AuditRecord]:
        return self.audit.by_correlation_id(correlation_id)
