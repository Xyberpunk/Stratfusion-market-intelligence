from __future__ import annotations

import csv
from pathlib import Path

from models.schemas import MarketBar


class KaggleOHLCVLoader:
    """Loads generic Kaggle OHLCV CSV datasets."""

    def load_csv(self, path: str | Path, symbol: str, source: str = "kaggle_ohlcv") -> list[MarketBar]:
        bars: list[MarketBar] = []
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                bars.append(
                    MarketBar(
                        symbol=str(row.get("symbol") or symbol).upper(),
                        timestamp=row.get("timestamp") or row.get("date") or row.get("Date"),
                        open=float(row.get("open") or row.get("Open")),
                        high=float(row.get("high") or row.get("High")),
                        low=float(row.get("low") or row.get("Low")),
                        close=float(row.get("close") or row.get("Close")),
                        volume=float(row.get("volume") or row.get("Volume") or 0.0),
                        source=source,
                    )
                )
        return bars
