from __future__ import annotations

from config import Settings
from models import NewsItem
from sources.base import BaseScraper


class EtMarketsScraper(BaseScraper):
    article_link_selectors = (
        "a[href*='/markets/']",
        "a[href*='/stocks/']",
        "a[href*='/news/']",
        "article a[href]",
        ".eachStory a[href]",
    )
    title_selectors = ("h1", ".article_title", ".artTitle", ".headline")
    summary_selectors = (".summary", ".artSyn", "h2")
    author_selectors = (".auth_detail", ".byline", "[rel='author']")
    published_selectors = ("time[datetime]", ".publish_on", ".date-format", "meta[property='article:published_time']")
    content_selectors = (".artText", ".article_wrap", ".article-content", "article")

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

    @property
    def source_name(self) -> str:
        return "etmarkets"

    @property
    def start_urls(self) -> list[str]:
        return [
            "https://economictimes.indiatimes.com/markets",
            "https://economictimes.indiatimes.com/markets/stocks",
            "https://economictimes.indiatimes.com/markets/stock-market-news",
        ]

    async def scrape(self) -> list[NewsItem]:
        return await self.scrape_common()

    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        return await self.parse_article_common(url, listing_title)

    def normalize(self, payload: dict[str, object]) -> NewsItem:
        return self.normalize_common(payload)

    def validate(self, item: NewsItem) -> bool:
        return self.validate_common(item)
