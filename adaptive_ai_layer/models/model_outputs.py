from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ModelPrediction(BaseModel):
    model_name: str
    symbol: str
    timestamp: datetime
    prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float]
    features_used: dict[str, Any]
    explanation: str


class EvaluationReport(BaseModel):
    model_name: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    confusion_matrix: list[list[int]]
    metadata: dict[str, Any]
