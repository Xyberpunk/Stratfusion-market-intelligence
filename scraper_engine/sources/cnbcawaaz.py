from __future__ import annotations

from config import Settings
from models import NewsItem
from sources.base import BaseScraper


class CnbcAwaazScraper(BaseScraper):
    article_link_selectors = (
        "a[href*='/market/']",
        "a[href*='/business/']",
        "a[href*='/share-market/']",
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
        return "cnbcawaaz"

    @property
    def start_urls(self) -> list[str]:
        return [
            "https://hindi.cnbctv18.com/market/",
            "https://hindi.cnbctv18.com/business/",
        ]

    async def scrape(self) -> list[NewsItem]:
        return await self.scrape_common()

    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        item = await self.parse_article_common(url, listing_title)
        if item is not None:
            item.language = "hi"
        return item

    def normalize(self, payload: dict[str, object]) -> NewsItem:
        return self.normalize_common(payload)

    def validate(self, item: NewsItem) -> bool:
        return self.validate_common(item)
