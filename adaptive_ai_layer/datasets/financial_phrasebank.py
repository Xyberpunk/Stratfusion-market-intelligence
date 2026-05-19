from __future__ import annotations

import csv
from pathlib import Path

from models.enums import SentimentLabel
from models.schemas import NewsSentimentEvent


class FinancialPhraseBankLoader:
    """Loads Financial PhraseBank-style CSV rows for sentiment calibration."""

    def load_csv(self, path: str | Path, text_column: str = "sentence", label_column: str = "label") -> list[NewsSentimentEvent]:
        rows: list[NewsSentimentEvent] = []
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                label = self._map_label(row[label_column])
                rows.append(NewsSentimentEvent(text=row[text_column], sentiment=label, source="financial_phrasebank"))
        return rows

    @staticmethod
    def _map_label(value: str) -> SentimentLabel:
        lowered = value.strip().lower()
        if lowered in {"positive", "bullish", "1"}:
            return SentimentLabel.BULLISH
        if lowered in {"negative", "bearish", "-1"}:
            return SentimentLabel.BEARISH
        return SentimentLabel.NEUTRAL
