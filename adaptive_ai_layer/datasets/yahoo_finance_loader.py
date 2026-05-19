from __future__ import annotations

from datetime import datetime

from models.schemas import MarketBar


class YahooFinanceLoader:
    """Loads free Yahoo Finance historical OHLCV using yfinance."""

    def load(self, symbol: str, start: str, end: str, interval: str = "1d") -> list[MarketBar]:
        try:
            import yfinance as yf
        except Exception as exc:
            raise RuntimeError("yfinance is not installed") from exc
        data = yf.download(symbol, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
        bars: list[MarketBar] = []
        for timestamp, row in data.iterrows():
            bars.append(
                MarketBar(
                    symbol=symbol.upper(),
                    timestamp=timestamp.to_pydatetime() if hasattr(timestamp, "to_pydatetime") else datetime.fromisoformat(str(timestamp)),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                    source="yahoo_finance",
                )
            )
        return bars
