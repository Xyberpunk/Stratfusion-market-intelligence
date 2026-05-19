from __future__ import annotations


class CompletenessChecker:
    """Checks required payload fields."""

    def missing_fields(self, payload: dict[str, object], required: set[str]) -> list[str]:
        return sorted(field for field in required if payload.get(field) in {None, ""})
