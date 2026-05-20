from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from shared.data.schemas import NormalizedOptionsChain, OptionsChainResult


class OptionsChainService:
    """Normalizes NSE options-chain payloads into platform schema."""

    def normalize(self, symbol: str, payload: dict[str, Any]) -> OptionsChainResult:
        try:
            records = payload.get("records", {})
            rows = records.get("data", [])
            call_oi = put_oi = call_change = put_change = 0.0
            iv_values: list[float] = []
            strikes: list[float] = []
            underlying = records.get("underlyingValue")
            for row in rows:
                ce = row.get("CE") or {}
                pe = row.get("PE") or {}
                call_oi += float(ce.get("openInterest") or 0.0)
                put_oi += float(pe.get("openInterest") or 0.0)
                call_change += float(ce.get("changeinOpenInterest") or 0.0)
                put_change += float(pe.get("changeinOpenInterest") or 0.0)
                for option in (ce, pe):
                    if option.get("impliedVolatility") is not None:
                        iv_values.append(float(option["impliedVolatility"]))
                if row.get("strikePrice") is not None:
                    strikes.append(float(row["strikePrice"]))
            iv = sum(iv_values) / len(iv_values) if iv_values else None
            pcr = put_oi / call_oi if call_oi > 0 else None
            return OptionsChainResult(
                ok=True,
                data=NormalizedOptionsChain(
                    symbol=symbol.upper(),
                    timestamp=datetime.now(timezone.utc),
                    pcr=pcr,
                    call_oi=call_oi,
                    put_oi=put_oi,
                    call_oi_change=call_change,
                    put_oi_change=put_change,
                    iv=iv,
                    iv_change=None,
                    max_pain=self._max_pain(strikes),
                    underlying_value=float(underlying) if underlying is not None else None,
                ),
            )
        except Exception as exc:
            return OptionsChainResult(ok=False, error=str(exc))

    @staticmethod
    def _max_pain(strikes: list[float]) -> float | None:
        if not strikes:
            return None
        ordered = sorted(strikes)
        return ordered[len(ordered) // 2]
