from __future__ import annotations

import pandas as pd

from models.enums import TargetKind
from training.target_engineering import TargetEngineer


class LabelBuilder:
    """Builds target labels for configured training objectives."""

    def __init__(self) -> None:
        self.engineer = TargetEngineer()

    def build(self, frame: pd.DataFrame, target_kind: TargetKind, horizon: int) -> pd.Series:
        if target_kind == TargetKind.DIRECTIONAL:
            return self.engineer.directional(frame, horizon)
        if target_kind == TargetKind.REGIME:
            return self.engineer.regime(frame)
        if target_kind == TargetKind.STRATEGY_SUITABILITY:
            return self.engineer.strategy_suitability(frame)
        raise ValueError(f"Unsupported target kind: {target_kind}")
