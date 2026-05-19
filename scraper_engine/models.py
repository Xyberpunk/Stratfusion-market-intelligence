from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class NewsItem(BaseModel):
    """Canonical article contract emitted by every source scraper."""

    model_config = ConfigDict(str_strip_whitespace=True)

    source: str
    title: str = Field(min_length=1)
    url: str
    summary: str | None = None
    content: str | None = None
    author: str | None = None
    published_at: str | None = None
    scraped_at: str
    tags: list[str] = Field(default_factory=list)
    language: str = "en"
    url_hash: str
    content_hash: str
    semantic_hash: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        HttpUrl(value)
        return value

    def raw_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class ArticleCandidate(BaseModel):
    source: str
    title: str
    url: str
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)


class InsertResult(BaseModel):
    inserted: bool
    duplicate_reason: str | None = None
    article_id: int | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
