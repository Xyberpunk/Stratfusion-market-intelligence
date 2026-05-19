from __future__ import annotations

from fastapi import APIRouter, Request

from models.schemas import FinBERTBatchRequest, FinBERTOutput

router = APIRouter()


@router.post("/sentiment/finbert/batch")
async def finbert_batch(payload: FinBERTBatchRequest, request: Request) -> list[FinBERTOutput]:
    outputs = request.app.state.service.finbert.batch_infer(payload.items)
    request.app.state.service.repository.save_sentiments(outputs)
    return outputs
