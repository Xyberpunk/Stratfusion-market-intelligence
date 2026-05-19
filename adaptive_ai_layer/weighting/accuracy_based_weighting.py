from __future__ import annotations

from models.schemas import StrategyPerformanceRecord


class AccuracyBasedWeighting:
    """Adjusts weights from regime-conditioned performance memory."""

    def apply(self, weights: dict[str, float], records: list[StrategyPerformanceRecord], regime: str) -> dict[str, float]:
        if not records:
            return weights
        by_strategy = {record.strategy_name: record for record in records if record.regime == regime or record.regime == "unknown"}
        adjusted: dict[str, float] = {}
        for name, weight in weights.items():
            record = by_strategy.get(name)
            if record is None or record.sample_size < 10:
                adjusted[name] = weight
            else:
                risk_adjustment = max(0.3, 1.0 + record.avg_return - abs(record.max_drawdown))
                adjusted[name] = weight * (0.6 + record.accuracy) * risk_adjustment
        return adjusted
