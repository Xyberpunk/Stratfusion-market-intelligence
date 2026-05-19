from __future__ import annotations

from datetime import datetime, timezone


class ModelVersioner:
    """Creates monotonic timestamp-based model versions."""

    def next_version(self, model_name: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        safe_name = "".join(ch.lower() if ch.isalnum() else "-" for ch in model_name).strip("-")
        return f"{safe_name}-{stamp}"
