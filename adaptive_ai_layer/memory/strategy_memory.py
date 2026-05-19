from __future__ import annotations

from memory.performance_memory import StrategyPerformanceMemory
from models.schemas import StrategyPerformanceRecord


class PersistentStrategyMemory(StrategyPerformanceMemory):
    """Strategy performance memory facade ready for MySQL-backed persistence."""

    def update_from_feedback(self, record: StrategyPerformanceRecord) -> None:
        self.add(record)
