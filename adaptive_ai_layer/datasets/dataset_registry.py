from __future__ import annotations

from datasets.financial_phrasebank import FinancialPhraseBankLoader
from datasets.kaggle_ohlcv_loader import KaggleOHLCVLoader
from datasets.nse_historical_loader import NSEHistoricalLoader
from datasets.yahoo_finance_loader import YahooFinanceLoader


class DatasetRegistry:
    """Registry for lightweight, free dataset loaders."""

    def __init__(self) -> None:
        self.financial_phrasebank = FinancialPhraseBankLoader()
        self.yahoo_finance = YahooFinanceLoader()
        self.nse_historical = NSEHistoricalLoader()
        self.kaggle_ohlcv = KaggleOHLCVLoader()

    def names(self) -> list[str]:
        return ["financial_phrasebank", "yahoo_finance", "nse_historical", "kaggle_ohlcv"]
