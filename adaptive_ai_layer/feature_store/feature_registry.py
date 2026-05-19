from __future__ import annotations

from feature_store.feature_definitions import DEFAULT_FEATURE_DEFINITIONS, FeatureDefinition


class FeatureRegistry:
    """In-process feature registry that mirrors persisted feature_definitions."""

    def __init__(self) -> None:
        self._items = {item.feature_name: item for item in DEFAULT_FEATURE_DEFINITIONS}

    def register(self, definition: FeatureDefinition) -> None:
        self._items[definition.feature_name] = definition

    def get(self, feature_name: str) -> FeatureDefinition | None:
        return self._items.get(feature_name)

    def all(self) -> list[FeatureDefinition]:
        return list(self._items.values())
