from __future__ import annotations

from mlops.model_registry import MLOpsModelRegistry
from mlops.rollback import ModelRollbackService


def test_model_registry_activation_and_rollback() -> None:
    registry = MLOpsModelRegistry()
    first = registry.register("regime-xgb", "XGBClassifier", "/tmp/a", {"accuracy": 0.6})
    second = registry.register("regime-xgb", "XGBClassifier", "/tmp/b", {"accuracy": 0.7})
    registry.activate("regime-xgb", second.model_version)
    rolled = ModelRollbackService(registry).rollback_to_previous("regime-xgb")
    assert rolled.model_version == first.model_version
