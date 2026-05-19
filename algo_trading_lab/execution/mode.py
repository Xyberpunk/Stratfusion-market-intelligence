from __future__ import annotations

from enum import StrEnum


class ExecutionMode(StrEnum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    LIVE_SIMULATION = "LIVE_SIMULATION"
