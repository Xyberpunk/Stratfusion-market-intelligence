from __future__ import annotations


class ExtremeOutlierChecker:
    """Simple defensive outlier checks before feature/model processing."""

    def impossible_price(self, price: float) -> bool:
        return price <= 0 or price > 10_000_000

    def extreme_return(self, current: float, previous: float, threshold: float = 0.4) -> bool:
        if previous <= 0:
            return True
        return abs(current / previous - 1) > threshold
