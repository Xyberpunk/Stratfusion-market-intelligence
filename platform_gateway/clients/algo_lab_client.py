from __future__ import annotations

from typing import Any

from clients.service_client import ServiceClient


class AlgoLabClient:
    """Client for the Algo Trading Lab API."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.client = ServiceClient(base_url, timeout_seconds)

    async def health(self) -> str:
        try:
            data = await self.client.get("/health")
            return str(data.get("status", "unknown"))
        except Exception:
            return "unavailable"

    async def strategies(self) -> list[dict[str, str]]:
        return await self.client.get("/strategies")

    async def generate_signal(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.post("/signals/generate", payload)
