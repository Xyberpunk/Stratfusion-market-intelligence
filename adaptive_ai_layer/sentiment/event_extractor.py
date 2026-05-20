from __future__ import annotations

import re


class FinancialEventExtractor:
    """Lightweight event extraction interface for headline/article sentiment."""

    patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        ("guidance", re.compile(r"\b(guidance|outlook|forecast|warns|cuts|raises)\b", re.I)),
        ("earnings", re.compile(r"\b(result|profit|loss|earnings|quarter|revenue)\b", re.I)),
        ("corporate_action", re.compile(r"\b(buyback|dividend|split|bonus|merger|acquisition)\b", re.I)),
        ("regulatory", re.compile(r"\b(sebi|rbi|approval|probe|penalty|regulator)\b", re.I)),
        ("order_win", re.compile(r"\b(order|contract|deal|project|tender)\b", re.I)),
    )

    def extract(self, text: str) -> str | None:
        for event_type, pattern in self.patterns:
            if pattern.search(text):
                return event_type
        return None
