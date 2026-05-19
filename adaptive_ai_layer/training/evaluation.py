from __future__ import annotations

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from models.model_outputs import EvaluationReport


class ModelEvaluator:
    """Evaluates classification models with macro metrics."""

    def evaluate(self, model_name: str, y_true: list[str], y_pred: list[str]) -> EvaluationReport:
        labels = sorted(set(y_true) | set(y_pred))
        return EvaluationReport(
            model_name=model_name,
            accuracy=float(accuracy_score(y_true, y_pred)),
            precision_macro=float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            recall_macro=float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            f1_macro=float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            confusion_matrix=confusion_matrix(y_true, y_pred, labels=labels).tolist(),
            metadata={"labels": labels},
        )
