from __future__ import annotations

from pydantic import BaseModel


class EvaluationRecord(BaseModel):
    model_name: str
    model_version: str
    metrics: dict[str, float]
    dataset_name: str = "walk_forward"


class EvaluationStore:
    """Stores model evaluation metrics by version."""

    def __init__(self) -> None:
        self._records: list[EvaluationRecord] = []

    def add(self, record: EvaluationRecord) -> None:
        self._records.append(record)

    def by_model(self, model_name: str) -> list[EvaluationRecord]:
        return [record for record in self._records if record.model_name == model_name]
