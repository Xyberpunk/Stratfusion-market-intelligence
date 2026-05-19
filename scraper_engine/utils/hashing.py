from __future__ import annotations

import hashlib
import re
from urllib.parse import ParseResult, urlparse, urlunparse
WHITESPACE_RE = re.compile(r"\s+")


def normalize_url(url: str) -> str:
    """Normalize URLs for exact duplicate detection."""
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    normalized = ParseResult(scheme, netloc, path, "", "", "")
    return urlunparse(normalized)


def normalize_text(text: str | None) -> str:
    """Normalize text for hashing and semantic preprocessing."""
    if not text:
        return ""
    text = text.replace("\u00a0", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip().casefold()


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_url(url: str) -> str:
    return _sha256(normalize_url(url))


def hash_content(content: str | None) -> str:
    return _sha256(normalize_text(content))


def semantic_fingerprint(title: str, summary: str | None = None, content: str | None = None) -> str:
    signal_text = " ".join(part for part in (title, summary, content) if part)
    return hash_content(signal_text[:4000])
