import pytest

from dedupe import ExactDeduper, SemanticDeduper
from models import NewsItem
from utils.normalization import normalized_item_payload


class FakeStorage:
    def __init__(self, *, has_url: bool = False, has_content: bool = False) -> None:
        self.has_url = has_url
        self.has_content = has_content

    async def exists_by_url_hash(self, url_hash: str) -> bool:
        return self.has_url

    async def exists_by_content_hash(self, source: str, content_hash: str) -> bool:
        return self.has_content


class FakeChroma:
    def __init__(self, similarity: float) -> None:
        self.similarity = similarity

    def query_similar(self, *, embedding: list[float], n_results: int = 5) -> list[dict[str, object]]:
        return [
            {
                "id": "article:10",
                "metadata": {"article_id": 10, "source": "moneycontrol"},
                "document": "infosys cuts guidance",
                "distance": 1.0 - self.similarity,
                "similarity": self.similarity,
            }
        ]


def make_item() -> NewsItem:
    return NewsItem.model_validate(
        normalized_item_payload(
            source="moneycontrol",
            title="Infosys cuts FY guidance",
            url="https://www.moneycontrol.com/news/business/markets/infosys.html",
            summary="Revenue growth outlook reduced",
            content="Infosys cut its revenue guidance amid weaker discretionary spending.",
            scraped_at="2026-05-19T00:00:00+00:00",
        )
    )


@pytest.mark.asyncio
async def test_exact_dedupe_detects_url_hash() -> None:
    deduper = ExactDeduper(FakeStorage(has_url=True))  # type: ignore[arg-type]
    assert await deduper.duplicate_reason(make_item()) == "url_hash"


@pytest.mark.asyncio
async def test_exact_dedupe_detects_content_hash() -> None:
    deduper = ExactDeduper(FakeStorage(has_content=True))  # type: ignore[arg-type]
    assert await deduper.duplicate_reason(make_item()) == "content_hash"


def test_semantic_dedupe_above_threshold() -> None:
    deduper = SemanticDeduper(FakeChroma(0.93), threshold=0.92)  # type: ignore[arg-type]
    match = deduper.find_duplicate([0.1, 0.2])
    assert match.is_duplicate is True
    assert match.matched_article_id == 10


def test_semantic_dedupe_at_threshold_is_not_duplicate() -> None:
    deduper = SemanticDeduper(FakeChroma(0.92), threshold=0.92)  # type: ignore[arg-type]
    assert deduper.find_duplicate([0.1, 0.2]).is_duplicate is False
