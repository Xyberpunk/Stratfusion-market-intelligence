from __future__ import annotations

from config import Settings
from models import NewsItem
from sources.base import BaseScraper


class CnbcTv18Scraper(BaseScraper):
    article_link_selectors = (
        "a[href*='/market/']",
        "a[href*='/stocks/']",
        "a[href*='/business/']",
        "article a[href]",
        ".story-card a[href]",
    )
    title_selectors = ("h1", ".article-title", ".story-title")
    summary_selectors = (".article-summary", ".story-summary", "h2")
    author_selectors = (".author-name", ".article-author", "[rel='author']")
    published_selectors = ("time[datetime]", ".publish-date", ".article-date", "meta[property='article:published_time']")
    content_selectors = (".article-content", ".story-content", "article", ".content")

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

    @property
    def source_name(self) -> str:
        return "cnbctv18"

    @property
    def start_urls(self) -> list[str]:
        return [
            "https://www.cnbctv18.com/market/",
            "https://www.cnbctv18.com/market/stocks/",
            "https://www.cnbctv18.com/business/",
        ]

    async def scrape(self) -> list[NewsItem]:
        return await self.scrape_common()

    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        return await self.parse_article_common(url, listing_title)

    def normalize(self, payload: dict[str, object]) -> NewsItem:
        return self.normalize_common(payload)

    def validate(self, item: NewsItem) -> bool:
        return self.validate_common(item)
