from __future__ import annotations

from config import Settings
from models.schemas import UnifiedPipelineResponse, utc_now
from storage.pipeline_repository import PipelineRepository


def test_pipeline_repository_in_memory_final_signal_round_trip() -> None:
    repo = PipelineRepository(Settings(pipeline_mysql_enabled=False))
    response = UnifiedPipelineResponse(
        symbol="INFY",
        timestamp=utc_now(),
        sentiment_outputs=[],
        regime={"regime": "TRENDING"},
        anomalies=[],
        weighting={"weights": {}},
        trading_guidance={"guidance": {"final_action": "HOLD", "ensemble": {"bullish_probability": 0.5, "bearish_probability": 0.2, "neutral_probability": 0.3}, "risk": {"risk_level": "MODERATE"}}},
        latest_news=[],
        explanation="Combined market intelligence suggests neutral probability.",
    )
    import asyncio

    asyncio.run(repo.save_final_signal("corr-1", response))
    assert repo.get_latest_signal("INFY") == response
    assert repo.get_pipeline_run("corr-1")["status"] == "FINALIZED"
