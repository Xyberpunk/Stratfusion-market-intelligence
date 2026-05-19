from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4


correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_or_create_correlation_id() -> str:
    current = correlation_id_var.get()
    if current:
        return current
    created = str(uuid4())
    correlation_id_var.set(created)
    return created


def set_correlation_id(correlation_id: str) -> None:
    correlation_id_var.set(correlation_id)
