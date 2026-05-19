from __future__ import annotations

from typing import Any

from clients.service_client import ServiceClient


class AdaptiveAIClient:
    """Client for the Adaptive AI/ML Intelligence Layer."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.client = ServiceClient(base_url, timeout_seconds)

    async def health(self) -> str:
        try:
            data = await self.client.get("/health")
            return str(data.get("status", "unknown"))
        except Exception:
            return "unavailable"

    async def finbert_batch(self, items: list[dict[str, object]]) -> list[dict[str, Any]]:
        return await self.client.post("/sentiment/finbert/batch", {"items": items})

    async def regime_detect(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.post("/regime/detect", payload)

    async def anomaly_detect(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        return await self.client.post("/anomaly/detect", payload)

    async def weighting_suggest(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.post("/weighting/suggest", payload)
