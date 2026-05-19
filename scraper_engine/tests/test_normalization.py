from bs4 import BeautifulSoup

from config import Settings
from sources.moneycontrol import MoneycontrolScraper
from utils.normalization import clean_text, compact_for_embedding, extract_article_text, parse_datetime


def test_clean_text_removes_excess_spacing() -> None:
    assert clean_text("  A\u00a0  B\n\n\nC  ") == "A B\n\nC"


def test_extract_article_text_from_selector() -> None:
    soup = BeautifulSoup(
        """
        <article>
          <script>ignore()</script>
          <p>Infosys cut FY guidance after demand slowed.</p>
          <p>The management warned of weaker discretionary spending across key markets.</p>
        </article>
        """,
        "lxml",
    )
    text = extract_article_text(soup, ["article"])
    assert text is not None
    assert "Infosys cut FY guidance" in text
    assert "ignore" not in text


def test_parse_datetime_iso_to_utc_naive_datetime() -> None:
    parsed = parse_datetime("2026-05-19T12:30:00+05:30")
    assert parsed is not None
    assert parsed.hour == 7
    assert parsed.minute == 0


def test_compact_for_embedding_includes_title_summary_content() -> None:
    text = compact_for_embedding("Title", "Summary", "Content")
    assert text == "title summary content"


def test_moneycontrol_candidate_extraction_from_listing_html() -> None:
    scraper = MoneycontrolScraper(Settings(max_articles_per_source=5))
    html = """
    <html><body>
      <li class="clearfix">
        <a href="/news/business/markets/infosys-cuts-fy-guidance-123456.html">
          Infosys cuts FY guidance as demand slows
        </a>
      </li>
    </body></html>
    """
    candidates = scraper.extract_candidates(html, "https://www.moneycontrol.com/news/business/markets/")
    assert len(candidates) == 1
    assert candidates[0].title == "Infosys cuts FY guidance as demand slows"
    assert candidates[0].url == "https://www.moneycontrol.com/news/business/markets/infosys-cuts-fy-guidance-123456.html"
