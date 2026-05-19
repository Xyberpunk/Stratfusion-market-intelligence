from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from shared.events.schemas import BaseEvent


class EventSerializer:
    """JSON serializer for Pydantic event envelopes."""

    @staticmethod
    def dumps(event: BaseEvent) -> bytes:
        return event.model_dump_json().encode("utf-8")

    @staticmethod
    def loads(raw: bytes | str) -> BaseEvent:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return BaseEvent.model_validate_json(text)

    @staticmethod
    def json_default(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")

    @staticmethod
    def payload_bytes(payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, default=EventSerializer.json_default, ensure_ascii=False).encode("utf-8")
