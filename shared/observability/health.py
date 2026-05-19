from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    name: str
    status: str
    detail: str | None = None
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthRegistry:
    """Stores latest component health snapshots."""

    def __init__(self) -> None:
        self._items: dict[str, ComponentHealth] = {}

    def update(self, name: str, status: str, detail: str | None = None) -> ComponentHealth:
        item = ComponentHealth(name=name, status=status, detail=detail, checked_at=datetime.now(timezone.utc))
        self._items[name] = item
        return item

    def all(self) -> list[ComponentHealth]:
        return list(self._items.values())
