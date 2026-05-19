from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils.hashing import hash_content, hash_url, normalize_text, normalize_url, semantic_fingerprint

EXCESS_SPACE_RE = re.compile(r"[ \t\r\f\v]+")
LINE_BREAK_RE = re.compile(r"\n{3,}")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.replace("\u00a0", " ")
    value = EXCESS_SPACE_RE.sub(" ", value)
    value = LINE_BREAK_RE.sub("\n\n", value)
    value = "\n".join(line.strip() for line in value.splitlines())
    value = value.strip()
    return value or None


def soup_text(soup: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = clean_text(node.get_text(" ", strip=True))
            if text:
                return text
    return None


def soup_attr(soup: BeautifulSoup, selectors: list[str], attr: str) -> str | None:
    for selector in selectors:
        node = soup.select_one(selector)
        if node and node.get(attr):
            value = clean_text(str(node.get(attr)))
            if value:
                return value
    return None


def extract_meta(soup: BeautifulSoup, names: list[str]) -> str | None:
    for name in names:
        selectors = [
            f'meta[property="{name}"]',
            f'meta[name="{name}"]',
            f'meta[itemprop="{name}"]',
        ]
        value = soup_attr(soup, selectors, "content")
        if value:
            return value
    return None


def extract_article_text(soup: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        container = soup.select_one(selector)
        if not container:
            continue
        for unwanted in container.select("script, style, noscript, iframe, figure, aside, nav, form"):
            unwanted.decompose()
        paragraphs = [clean_text(p.get_text(" ", strip=True)) for p in container.select("p")]
        text = "\n\n".join(p for p in paragraphs if p)
        if len(text) >= 80:
            return text
        fallback = clean_text(container.get_text("\n", strip=True))
        if fallback and len(fallback) >= 80:
            return fallback
    return None


def absolutize_url(base_url: str, url: str) -> str:
    return normalize_url(urljoin(base_url, url))


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(raw)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def db_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return parse_datetime(value)


def normalized_item_payload(
    *,
    source: str,
    title: str,
    url: str,
    scraped_at: str,
    summary: str | None = None,
    content: str | None = None,
    author: str | None = None,
    published_at: str | None = None,
    tags: list[str] | None = None,
    language: str = "en",
) -> dict[str, object]:
    canonical_url = normalize_url(url)
    title_text = clean_text(title) or ""
    summary_text = clean_text(summary)
    content_text = clean_text(content)
    basis = content_text or summary_text or title_text
    return {
        "source": source,
        "title": title_text,
        "url": canonical_url,
        "summary": summary_text,
        "content": content_text,
        "author": clean_text(author),
        "published_at": published_at,
        "scraped_at": scraped_at,
        "tags": tags or [],
        "language": language,
        "url_hash": hash_url(canonical_url),
        "content_hash": hash_content(basis),
        "semantic_hash": semantic_fingerprint(title_text, summary_text, content_text),
    }


def compact_for_embedding(title: str, summary: str | None, content: str | None, max_chars: int = 4000) -> str:
    parts = [title, summary or "", content or ""]
    return normalize_text(" ".join(part for part in parts if part))[:max_chars]
