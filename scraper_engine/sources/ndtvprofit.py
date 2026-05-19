from __future__ import annotations

from config import Settings
from models import NewsItem
from sources.base import BaseScraper


class NdtvProfitScraper(BaseScraper):
    article_link_selectors = (
        "a[href*='/markets/']",
        "a[href*='/business/']",
        "a[href*='/stock-market-news/']",
        "article a[href]",
        ".story-card a[href]",
    )
    title_selectors = ("h1", ".headline", ".story-title")
    summary_selectors = (".summary", ".excerpt", "h2")
    author_selectors = (".author", ".byline", "[rel='author']")
    published_selectors = ("time[datetime]", ".published-date", ".story-date", "meta[property='article:published_time']")
    content_selectors = (".story-content", ".article-content", "article", ".content")

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

    @property
    def source_name(self) -> str:
        return "ndtvprofit"

    @property
    def start_urls(self) -> list[str]:
        return [
            "https://www.ndtvprofit.com/markets",
            "https://www.ndtvprofit.com/business",
            "https://www.ndtvprofit.com/stock-market-news",
        ]

    async def scrape(self) -> list[NewsItem]:
        return await self.scrape_common()

    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        return await self.parse_article_common(url, listing_title)

    def normalize(self, payload: dict[str, object]) -> NewsItem:
        return self.normalize_common(payload)

    def validate(self, item: NewsItem) -> bool:
        return self.validate_common(item)
