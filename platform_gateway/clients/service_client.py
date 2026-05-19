from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class UpstreamServiceError(RuntimeError):
    """Raised when an upstream service is unavailable or returns an error."""


class ServiceClient:
    """Small async HTTP client with bounded retries for internal services."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @retry(wait=wait_exponential_jitter(initial=0.3, max=3), stop=stop_after_attempt(3), reraise=True)
    async def get(self, path: str) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(f"{self.base_url}{path}")
            if response.status_code >= 400:
                raise UpstreamServiceError(f"GET {path} failed with {response.status_code}: {response.text}")
            return response.json()

    @retry(wait=wait_exponential_jitter(initial=0.3, max=3), stop=stop_after_attempt(3), reraise=True)
    async def post(self, path: str, payload: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}{path}", json=payload)
            if response.status_code >= 400:
                raise UpstreamServiceError(f"POST {path} failed with {response.status_code}: {response.text}")
            return response.json()
