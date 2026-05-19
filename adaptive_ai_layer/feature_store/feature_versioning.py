from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256


class FeatureVersioner:
    """Deterministic feature version helper."""

    def version(self, feature_name: str, logic_signature: str = "default") -> str:
        digest = sha256(f"{feature_name}:{logic_signature}".encode("utf-8")).hexdigest()[:8]
        return f"v{datetime.now(timezone.utc).year}.{digest}"
