from __future__ import annotations

import asyncio
import json
import random
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from pydantic import ValidationError

from config import Settings
from logger import get_logger
from models import ArticleCandidate, NewsItem
from utils.normalization import (
    absolutize_url,
    clean_text,
    extract_article_text,
    extract_meta,
    normalized_item_payload,
    soup_attr,
    soup_text,
)
from utils.time_utils import utc_now_iso
from utils.user_agents import random_user_agent


class RobotsCacheEntry:
    def __init__(self, parser: RobotFileParser, loaded_at: float) -> None:
        self.parser = parser
        self.loaded_at = loaded_at


class BaseScraper(ABC):
    """Async Playwright scraper with ethical pacing and defensive parsing."""

    article_link_selectors: tuple[str, ...] = (
        "a[href*='/news/']",
        "article a[href]",
        ".article a[href]",
        ".story a[href]",
        ".news a[href]",
    )
    title_selectors: tuple[str, ...] = (
        "h1",
        "meta[property='og:title']",
        "meta[name='twitter:title']",
    )
    summary_selectors: tuple[str, ...] = (
        "h2",
        ".summary",
        ".article_summary",
        "meta[name='description']",
        "meta[property='og:description']",
    )
    author_selectors: tuple[str, ...] = (
        ".author",
        ".article_author",
        "[rel='author']",
        "meta[name='author']",
    )
    published_selectors: tuple[str, ...] = (
        "time[datetime]",
        "meta[property='article:published_time']",
        "meta[name='publish-date']",
        "meta[name='publish_date']",
        "meta[name='date']",
    )
    content_selectors: tuple[str, ...] = (
        "article",
        ".article_content",
        ".article-content",
        ".story-content",
        ".content_wrapper",
        ".content",
    )
    tag_selectors: tuple[str, ...] = (
        "meta[property='article:tag']",
        ".tags a",
        ".tag a",
    )

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("scraper", source=self.source_name)
        self._playwright: Any = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._robots: dict[str, RobotsCacheEntry] = {}
        self._last_fetch_at = 0.0

    @property
    @abstractmethod
    def source_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def start_urls(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def scrape(self) -> list[NewsItem]:
        raise NotImplementedError

    @abstractmethod
    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, payload: dict[str, object]) -> NewsItem:
        raise NotImplementedError

    @abstractmethod
    def validate(self, item: NewsItem) -> bool:
        raise NotImplementedError

    async def start(self) -> None:
        if self._context is not None:
            return
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.settings.headless)
        storage_state = Path("cache") / f"{self.source_name}_state.json"
        state = str(storage_state) if storage_state.exists() else None
        self._context = await self._browser.new_context(
            user_agent=random_user_agent(),
            viewport={
                "width": self.settings.playwright_viewport_width,
                "height": self.settings.playwright_viewport_height,
            },
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            storage_state=state,
        )
        self._context.set_default_timeout(self.settings.timeout_seconds * 1000)
        self.logger.info("scraper_started", headless=self.settings.headless)

    async def close(self) -> None:
        storage_state = Path("cache") / f"{self.source_name}_state.json"
        storage_state.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self._context is not None:
                await self._context.storage_state(path=str(storage_state))
                await self._context.close()
            if self._browser is not None:
                await self._browser.close()
            if self._playwright is not None:
                await self._playwright.stop()
        finally:
            self._context = None
            self._browser = None
            self._playwright = None
            self.logger.info("scraper_closed")

    async def _page(self) -> Page:
        if self._context is None:
            await self.start()
        if self._context is None:
            raise RuntimeError("Playwright context failed to initialize")
        return await self._context.new_page()

    async def _pace(self) -> None:
        minimum_gap = random.uniform(
            self.settings.request_delay_min_seconds,
            self.settings.request_delay_max_seconds,
        )
        elapsed = time.monotonic() - self._last_fetch_at
        if elapsed < minimum_gap:
            await asyncio.sleep(minimum_gap - elapsed)
        self._last_fetch_at = time.monotonic()

    async def _robots_parser(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        cached = self._robots.get(root)
        now = time.monotonic()
        if cached and now - cached.loaded_at < self.settings.robots_cache_ttl_seconds:
            return cached.parser
        robots_url = f"{root}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            timeout = aiohttp.ClientTimeout(total=min(15, self.settings.timeout_seconds))
            async with aiohttp.ClientSession(timeout=timeout, headers={"User-Agent": random_user_agent()}) as session:
                async with session.get(robots_url) as response:
                    if response.status >= 400:
                        parser.parse([])
                    else:
                        parser.parse((await response.text()).splitlines())
        except Exception as exc:
            self.logger.warning("robots_fetch_failed", robots_url=robots_url, error=str(exc))
            parser.parse([])
        self._robots[root] = RobotsCacheEntry(parser, now)
        return parser

    async def allowed_by_robots(self, url: str) -> bool:
        parser = await self._robots_parser(url)
        allowed = parser.can_fetch("*", url)
        if not allowed:
            self.logger.warning("robots_disallowed", url=url)
        return allowed

    async def fetch_html(self, url: str) -> str | None:
        if not await self.allowed_by_robots(url):
            return None
        await self._pace()
        page = await self._page()
        try:
            self.logger.info("page_fetch_start", url=url)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=self.settings.timeout_seconds * 1000)
            status = response.status if response else None
            if status in {403, 429}:
                backoff = random.uniform(60, 180)
                self.logger.warning("rate_or_access_limited", url=url, status=status, backoff_seconds=backoff)
                await asyncio.sleep(backoff)
                return None
            if status and status >= 500:
                self.logger.warning("page_server_error", url=url, status=status)
                return None
            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            html = await page.content()
            await self.save_raw_html(url, html)
            self.logger.info("page_fetch_ok", url=url, status=status, bytes=len(html))
            return html
        except Exception as exc:
            self.logger.exception("page_fetch_failed", url=url, error=str(exc))
            return None
        finally:
            await page.close()

    async def save_raw_html(self, url: str, html: str) -> None:
        parsed = urlparse(url)
        safe_path = parsed.path.strip("/").replace("/", "_") or "index"
        safe_path = "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in safe_path)
        file_path = Path("storage/raw") / self.source_name / f"{safe_path[:120]}.html"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(file_path, "w", encoding="utf-8") as handle:
                await handle.write(html)
        except Exception as exc:
            self.logger.warning("raw_html_write_failed", url=url, error=str(exc))

    def extract_candidates(self, html: str, base_url: str) -> list[ArticleCandidate]:
        soup = BeautifulSoup(html, "lxml")
        candidates: dict[str, ArticleCandidate] = {}
        selectors = list(self.article_link_selectors)
        for selector in selectors:
            for anchor in soup.select(selector):
                href = anchor.get("href")
                if not href:
                    continue
                title = clean_text(anchor.get_text(" ", strip=True)) or clean_text(anchor.get("title"))
                if not title or len(title) < 12:
                    continue
                url = absolutize_url(base_url, str(href))
                if not self.is_probable_article_url(url):
                    continue
                candidates[url] = ArticleCandidate(source=self.source_name, title=title, url=url)
        items = list(candidates.values())[: self.settings.max_articles_per_source]
        self.logger.info("candidates_extracted", base_url=base_url, count=len(items))
        return items

    def is_probable_article_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme.startswith("http"):
            return False
        path = parsed.path.lower()
        blocked = ("/video", "/videos", "/photos", "/live-tv", "/podcast", "/author/")
        if any(part in path for part in blocked):
            return False
        return "/news/" in path or path.endswith(".html") or any(char.isdigit() for char in path)

    async def scrape_common(self) -> list[NewsItem]:
        await self.start()
        self.logger.info("scrape_start", start_urls=self.start_urls)
        collected: list[NewsItem] = []
        seen_urls: set[str] = set()
        try:
            for start_url in self.start_urls:
                html = await self.fetch_html(start_url)
                if not html:
                    continue
                candidates = self.extract_candidates(html, start_url)
                semaphore = asyncio.Semaphore(self.settings.article_concurrency)

                async def parse_candidate(candidate: ArticleCandidate) -> NewsItem | None:
                    async with semaphore:
                        if candidate.url in seen_urls:
                            return None
                        seen_urls.add(candidate.url)
                        try:
                            return await self.parse_article(candidate.url, candidate.title)
                        except Exception as exc:
                            self.logger.exception("article_parse_failed", url=candidate.url, error=str(exc))
                            return None

                results = await asyncio.gather(*(parse_candidate(candidate) for candidate in candidates))
                collected.extend(item for item in results if item is not None and self.validate(item))
        finally:
            self.logger.info("scrape_stop", articles=len(collected))
        return collected

    async def parse_article_common(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        html = await self.fetch_html(url)
        if not html:
            if listing_title:
                payload = normalized_item_payload(
                    source=self.source_name,
                    title=listing_title,
                    url=url,
                    scraped_at=utc_now_iso(),
                    language="en",
                )
                return self.normalize(payload)
            return None
        soup = BeautifulSoup(html, "lxml")
        title = self._extract_title(soup) or listing_title
        if not title:
            return None
        summary = self._extract_summary(soup)
        content = extract_article_text(soup, list(self.content_selectors))
        author = self._extract_author(soup)
        published_at = self._extract_published_at(soup)
        tags = self._extract_tags(soup)
        language = extract_meta(soup, ["og:locale", "language"]) or "en"
        payload = normalized_item_payload(
            source=self.source_name,
            title=title,
            url=url,
            summary=summary,
            content=content,
            author=author,
            published_at=published_at,
            scraped_at=utc_now_iso(),
            tags=tags,
            language=language,
        )
        return self.normalize(payload)

    def normalize_common(self, payload: dict[str, object]) -> NewsItem:
        try:
            return NewsItem.model_validate(payload)
        except ValidationError as exc:
            self.logger.warning("article_validation_failed", errors=json.loads(exc.json()))
            raise

    def validate_common(self, item: NewsItem) -> bool:
        if not item.title or not item.url:
            return False
        if len(item.title) < 8:
            return False
        return True

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        meta_title = extract_meta(soup, ["og:title", "twitter:title"])
        return meta_title or soup_text(soup, [selector for selector in self.title_selectors if not selector.startswith("meta")])

    def _extract_summary(self, soup: BeautifulSoup) -> str | None:
        meta_summary = extract_meta(soup, ["description", "og:description", "twitter:description"])
        return meta_summary or soup_text(soup, [selector for selector in self.summary_selectors if not selector.startswith("meta")])

    def _extract_author(self, soup: BeautifulSoup) -> str | None:
        meta_author = extract_meta(soup, ["author", "article:author"])
        return meta_author or soup_text(soup, [selector for selector in self.author_selectors if not selector.startswith("meta")])

    def _extract_published_at(self, soup: BeautifulSoup) -> str | None:
        for selector in self.published_selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            value = node.get("datetime") or node.get("content") or node.get_text(" ", strip=True)
            if value:
                return clean_text(str(value))
        return extract_meta(soup, ["article:published_time", "publish-date", "publish_date", "date"])

    def _extract_tags(self, soup: BeautifulSoup) -> list[str]:
        tags: list[str] = []
        for selector in self.tag_selectors:
            for node in soup.select(selector):
                value = node.get("content") or node.get_text(" ", strip=True)
                value = clean_text(str(value)) if value else None
                if value and value not in tags:
                    tags.append(value)
        return tags[:20]
