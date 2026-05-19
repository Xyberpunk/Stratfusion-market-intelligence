from __future__ import annotations

import csv
from pathlib import Path

from models.schemas import MarketBar


class NSEHistoricalLoader:
    """Loads NSE historical OHLCV exports from CSV."""

    def load_csv(self, path: str | Path, symbol: str) -> list[MarketBar]:
        bars: list[MarketBar] = []
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                bars.append(
                    MarketBar(
                        symbol=str(row.get("symbol") or symbol).upper(),
                        timestamp=row.get("timestamp") or row.get("Date") or row.get("date"),
                        open=float(row.get("open") or row.get("Open")),
                        high=float(row.get("high") or row.get("High")),
                        low=float(row.get("low") or row.get("Low")),
                        close=float(row.get("close") or row.get("Close")),
                        volume=float(row.get("volume") or row.get("Volume") or 0.0),
                        source="nse_historical",
                    )
                )
        return bars
