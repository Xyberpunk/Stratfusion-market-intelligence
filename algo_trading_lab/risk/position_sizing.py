from __future__ import annotations


class PositionSizer:
    """Fixed-fractional position sizing."""

    def size(self, *, capital: float, risk_per_trade: float, entry_price: float, stop_loss: float) -> tuple[float, float]:
        risk_budget = capital * risk_per_trade
        per_unit_risk = abs(entry_price - stop_loss)
        if per_unit_risk <= 0:
            return 0.0, 0.0
        quantity = risk_budget / per_unit_risk
        max_affordable = capital / max(entry_price, 1e-9)
        quantity = min(quantity, max_affordable)
        return round(quantity, 4), round(quantity * per_unit_risk, 2)
