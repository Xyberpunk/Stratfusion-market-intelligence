from __future__ import annotations

from config import Settings
from models.enums import SentimentLabel
from models.schemas import NewsSentimentEvent
from sentiment.finbert_service import FinBERTService


def test_finbert_service_lexical_fallback_batch() -> None:
    service = FinBERTService(Settings(finbert_enabled=False))
    outputs = service.batch_infer([NewsSentimentEvent(symbol="INFY", text="Infosys profit rises and company raises guidance")])
    assert outputs[0].sentiment == SentimentLabel.BULLISH
    assert outputs[0].confidence > 0
    assert outputs[0].event_type == "guidance"
