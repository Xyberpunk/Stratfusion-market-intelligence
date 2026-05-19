from __future__ import annotations

from mlops.model_registry import MLOpsModelRegistry, RegisteredModel


class ModelRollbackService:
    """Rolls active model pointer back to a previous version."""

    def __init__(self, registry: MLOpsModelRegistry) -> None:
        self.registry = registry

    def rollback_to_previous(self, model_name: str) -> RegisteredModel:
        versions = self.registry.versions(model_name)
        if len(versions) < 2:
            raise ValueError("No previous model version exists")
        previous = versions[-2]
        return self.registry.activate(model_name, previous.model_version)
