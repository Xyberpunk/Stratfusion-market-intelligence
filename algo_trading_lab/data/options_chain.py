from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from logger import get_logger
from models.schemas import OptionsChainInput


class OptionsChainNormalizer:
    """Normalizes options-chain summaries into ensemble-ready features."""

    def __init__(self) -> None:
        self.logger = get_logger("options_chain_normalizer")

    def from_nsepython_payload(self, symbol: str, payload: dict[str, Any]) -> OptionsChainInput:
        records = payload.get("records", {}).get("data", [])
        call_oi_change = 0.0
        put_oi_change = 0.0
        call_oi = 0.0
        put_oi = 0.0
        iv_values: list[float] = []
        strikes: list[float] = []
        for row in records:
            ce = row.get("CE") or {}
            pe = row.get("PE") or {}
            call_oi += float(ce.get("openInterest", 0.0))
            put_oi += float(pe.get("openInterest", 0.0))
            call_oi_change += float(ce.get("changeinOpenInterest", 0.0))
            put_oi_change += float(pe.get("changeinOpenInterest", 0.0))
            if ce.get("impliedVolatility"):
                iv_values.append(float(ce["impliedVolatility"]))
            if pe.get("impliedVolatility"):
                iv_values.append(float(pe["impliedVolatility"]))
            if row.get("strikePrice"):
                strikes.append(float(row["strikePrice"]))
        pcr = put_oi / call_oi if call_oi > 0 else 1.0
        return OptionsChainInput(
            symbol=symbol.upper(),
            timestamp=datetime.now(timezone.utc),
            pcr=pcr,
            max_pain=self._estimate_max_pain(strikes) if strikes else None,
            iv=sum(iv_values) / len(iv_values) if iv_values else None,
            call_oi_change=call_oi_change,
            put_oi_change=put_oi_change,
        )

    @staticmethod
    def _estimate_max_pain(strikes: list[float]) -> float:
        ordered = sorted(strikes)
        return ordered[len(ordered) // 2]
