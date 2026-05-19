from __future__ import annotations

import uuid
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from config import Settings
from features.feature_builder import AdaptiveFeatureBuilder
from models.enums import TargetKind
from models.schemas import FeatureBuildRequest, TrainingRunOutput, TrainingRunRequest
from training.evaluation import ModelEvaluator
from training.label_builder import LabelBuilder
from training.model_registry import ModelRegistry
from training.walk_forward import WalkForwardSplitter


class TrainingPipeline:
    """End-to-end feature generation, labeling, walk-forward training, evaluation, and persistence."""

    def __init__(self, settings: Settings, model_registry: ModelRegistry | None = None) -> None:
        self.settings = settings
        self.feature_builder = AdaptiveFeatureBuilder()
        self.labels = LabelBuilder()
        self.splitter = WalkForwardSplitter()
        self.evaluator = ModelEvaluator()
        self.registry = model_registry or ModelRegistry()

    def run(self, request: TrainingRunRequest) -> TrainingRunOutput:
        feature_request = FeatureBuildRequest(
            symbol=request.symbol,
            market_data=request.market_data,
            sentiment_events=request.sentiment_events,
            options_chain=request.options_chain,
        )
        frame = self.feature_builder.build_frame(feature_request)
        if len(frame.index) < 40:
            raise ValueError("At least 40 feature rows are required for training")
        labels = self.labels.build(frame, request.target_kind, request.horizon)
        dataset = frame.copy()
        dataset["target"] = labels
        dataset = dataset.iloc[:-request.horizon].dropna(subset=["target"])
        feature_columns = self._feature_columns(dataset)
        x = dataset[feature_columns]
        y = dataset["target"].astype(str)
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y)
        all_true: list[str] = []
        all_pred: list[str] = []
        model = self._new_model()
        for train_idx, test_idx in self.splitter.split(len(dataset.index), request.walk_forward_splits):
            model = self._new_model()
            model.fit(x.iloc[train_idx], y_encoded[train_idx])
            pred = model.predict(x.iloc[test_idx])
            all_true.extend(encoder.inverse_transform(y_encoded[test_idx]).tolist())
            all_pred.extend(encoder.inverse_transform(pred).tolist())
        report = self.evaluator.evaluate(request.model_name, all_true, all_pred)
        model.fit(x, y_encoded)
        run_id = str(uuid.uuid4())
        model_path = self._persist_model(request.model_name, run_id, model, encoder, feature_columns)
        metrics = {
            "accuracy": report.accuracy,
            "precision_macro": report.precision_macro,
            "recall_macro": report.recall_macro,
            "f1_macro": report.f1_macro,
        }
        self.registry.register(request.model_name, "RandomForestClassifier", request.target_kind, str(model_path), metrics)
        return TrainingRunOutput(
            run_id=run_id,
            model_name=request.model_name,
            target_kind=request.target_kind,
            symbol=request.symbol.upper(),
            metrics=metrics,
            feature_columns=feature_columns,
            model_path=str(model_path),
            explanation=(
                "Model trained with walk-forward validation. Random forests are used as the default stable baseline; "
                "XGBoost and LightGBM interfaces can replace the estimator without changing the pipeline contract."
            ),
        )

    @staticmethod
    def _feature_columns(frame: pd.DataFrame) -> list[str]:
        excluded = {"symbol", "timestamp", "source", "target"}
        columns = [column for column in frame.columns if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])]
        return columns

    @staticmethod
    def _new_model() -> RandomForestClassifier:
        return RandomForestClassifier(n_estimators=160, max_depth=6, min_samples_leaf=5, random_state=42, n_jobs=-1)

    def _persist_model(self, model_name: str, run_id: str, model: object, encoder: LabelEncoder, feature_columns: list[str]) -> Path:
        path = self.settings.model_dir / f"{model_name}_{run_id}.joblib"
        joblib.dump({"model": model, "encoder": encoder, "feature_columns": feature_columns}, path)
        return path
