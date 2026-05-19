from __future__ import annotations

from config import Settings
from models import NewsItem
from sources.base import BaseScraper


class MoneycontrolScraper(BaseScraper):
    article_link_selectors = (
        "li.clearfix a[href*='/news/']",
        ".clearfix a[href*='/news/']",
        "#cagetory a[href*='/news/']",
        ".article_title a[href*='/news/']",
        "a[href*='/news/business/']",
        "a[href*='/news/stock-markets/']",
    )
    title_selectors = ("h1", ".article_title", ".arti_title", ".articleHead")
    summary_selectors = (".article_desc", ".article_summary", "h2", ".synopsis")
    author_selectors = (".article_author", ".author", ".auth_name", "[rel='author']")
    published_selectors = (
        "time[datetime]",
        ".article_schedule",
        ".article_date",
        ".pubtime",
        "meta[property='article:published_time']",
    )
    content_selectors = (
        "#contentdata",
        ".content_wrapper",
        ".article_content",
        ".article_wrap",
        "article",
    )
    tag_selectors = (".tags a", ".article_tags a", "meta[property='article:tag']")

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

    @property
    def source_name(self) -> str:
        return "moneycontrol"

    @property
    def start_urls(self) -> list[str]:
        return [
            "https://www.moneycontrol.com/news/business/markets/",
            "https://www.moneycontrol.com/news/business/stocks/",
            "https://www.moneycontrol.com/news/stock-markets/",
        ]

    async def scrape(self) -> list[NewsItem]:
        return await self.scrape_common()

    async def parse_article(self, url: str, listing_title: str | None = None) -> NewsItem | None:
        return await self.parse_article_common(url, listing_title)

    def normalize(self, payload: dict[str, object]) -> NewsItem:
        return self.normalize_common(payload)

    def validate(self, item: NewsItem) -> bool:
        return self.validate_common(item)
