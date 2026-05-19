from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from mlops.model_versioning import ModelVersioner


class RegisteredModel(BaseModel):
    model_name: str
    model_version: str
    model_type: str
    path: str | None
    metrics: dict[str, float] = Field(default_factory=dict)
    active: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MLOpsModelRegistry:
    """Model registry with active-version selection and rollback support."""

    def __init__(self) -> None:
        self.versioner = ModelVersioner()
        self._models: dict[str, list[RegisteredModel]] = {}

    def register(self, model_name: str, model_type: str, path: str | None, metrics: dict[str, float]) -> RegisteredModel:
        item = RegisteredModel(
            model_name=model_name,
            model_version=self.versioner.next_version(model_name),
            model_type=model_type,
            path=path,
            metrics=metrics,
            active=False,
        )
        self._models.setdefault(model_name, []).append(item)
        if not any(model.active for model in self._models[model_name]):
            self.activate(model_name, item.model_version)
        return item

    def activate(self, model_name: str, model_version: str) -> RegisteredModel:
        versions = self._models.get(model_name, [])
        selected: RegisteredModel | None = None
        for item in versions:
            item.active = item.model_version == model_version
            if item.active:
                selected = item
        if selected is None:
            raise ValueError(f"Unknown model version: {model_name}:{model_version}")
        return selected

    def active(self, model_name: str) -> RegisteredModel | None:
        return next((item for item in self._models.get(model_name, []) if item.active), None)

    def versions(self, model_name: str) -> list[RegisteredModel]:
        return self._models.get(model_name, [])
