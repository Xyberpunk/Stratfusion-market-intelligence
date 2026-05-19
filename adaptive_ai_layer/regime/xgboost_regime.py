from __future__ import annotations

import pandas as pd


class XGBoostRegimeInterface:
    """Production-ready interface for an XGBoost regime classifier."""

    def train(self, features: pd.DataFrame, labels: pd.Series) -> object:
        try:
            from xgboost import XGBClassifier
        except Exception as exc:
            raise RuntimeError("xgboost is not installed") from exc
        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            eval_metric="mlogloss",
        )
        model.fit(features, labels)
        return model
