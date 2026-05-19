from __future__ import annotations

from training.walk_forward import WalkForwardSplitter


def test_walk_forward_splitter_expanding_windows() -> None:
    splits = WalkForwardSplitter().split(100, 4)
    assert len(splits) == 4
    assert len(splits[0][0]) < len(splits[-1][0])
    assert min(len(test) for _, test in splits) > 0
