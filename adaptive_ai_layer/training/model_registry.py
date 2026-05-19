from __future__ import annotations

from datetime import datetime, timezone

from models.enums import TargetKind
from models.schemas import ModelRegistryItem


class ModelRegistry:
    """In-process model registry with persistence-ready records."""

    def __init__(self) -> None:
        self._items: dict[str, ModelRegistryItem] = {}

    def register(self, model_name: str, model_type: str, target_kind: TargetKind, path: str | None, metrics: dict[str, float]) -> ModelRegistryItem:
        item = ModelRegistryItem(
            model_name=model_name,
            model_type=model_type,
            target_kind=target_kind,
            path=path,
            metrics=metrics,
            created_at=datetime.now(timezone.utc),
        )
        self._items[model_name] = item
        return item

    def list_models(self) -> list[ModelRegistryItem]:
        return list(self._items.values())
