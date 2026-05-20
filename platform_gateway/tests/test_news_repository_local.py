from __future__ import annotations

from datetime import datetime, timezone

import pytest

from config import Settings
from storage.news_repository import NewsRepository


@pytest.mark.asyncio
async def test_news_repository_uses_local_memory_when_mysql_disabled() -> None:
    repo = NewsRepository(Settings(scraper_mysql_enabled=False))
    assert await repo.status() == "local-memory"

    repo.record_dashboard_headlines(
        [
            {
                "symbol": "INFY",
                "timestamp": datetime.now(timezone.utc),
                "text": "Infosys raises guidance after strong revenue growth",
                "source": "dashboard",
            }
        ],
        [
            {
                "text": "Infosys raises guidance after strong revenue growth",
                "sentiment": "bullish",
                "confidence": 0.82,
            }
        ],
    )

    rows = await repo.latest(symbol="INFY", limit=5)
    assert len(rows) == 1
    assert rows[0].source == "dashboard"
    assert rows[0].sentiment == "bullish"
    assert rows[0].sentiment_score == 0.82
