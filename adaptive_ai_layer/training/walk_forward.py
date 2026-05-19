from __future__ import annotations

import numpy as np


class WalkForwardSplitter:
    """Creates expanding-window walk-forward splits for time-series model evaluation."""

    def split(self, n_samples: int, n_splits: int) -> list[tuple[np.ndarray, np.ndarray]]:
        if n_samples < n_splits + 2:
            raise ValueError("Not enough samples for requested walk-forward splits")
        fold_size = n_samples // (n_splits + 1)
        splits: list[tuple[np.ndarray, np.ndarray]] = []
        for fold in range(1, n_splits + 1):
            train_end = fold * fold_size
            test_end = min(n_samples, train_end + fold_size)
            train_idx = np.arange(0, train_end)
            test_idx = np.arange(train_end, test_end)
            if len(test_idx) > 0:
                splits.append((train_idx, test_idx))
        return splits
