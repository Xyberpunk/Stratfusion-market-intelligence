from __future__ import annotations

from fastapi import FastAPI

from adaptive_learning.bandit_selector import SafeBanditSelector
from adaptive_learning.paper_feedback_loop import PaperFeedbackLoop
from adaptive_learning.reward_engine import RewardEngine
from anomaly.anomaly_detector import AnomalyDetectionEngine
from config import Settings, get_settings
from features.feature_builder import AdaptiveFeatureBuilder
from logger import configure_logging
from memory.feedback_store import FeedbackStore
from memory.performance_memory import StrategyPerformanceMemory
from memory.regime_memory import RegimeMemory
from regime.regime_detector import RegimeDetectionEngine
from sentiment.finbert_service import FinBERTService
from storage.mysql import MySQLStore
from storage.repositories import InMemoryRepository
from training.model_registry import ModelRegistry
from training.trainer import TrainingPipeline
from weighting.dynamic_weight_engine import DynamicWeightEngine


class AdaptiveAIService:
    """Application service for adaptive AI/ML intelligence."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.feature_builder = AdaptiveFeatureBuilder()
        self.regime_detector = RegimeDetectionEngine(settings)
        self.anomaly_detector = AnomalyDetectionEngine(settings)
        self.weight_engine = DynamicWeightEngine(settings)
        self.finbert = FinBERTService(settings)
        self.model_registry = ModelRegistry()
        self.trainer = TrainingPipeline(settings, self.model_registry)
        self.repository = InMemoryRepository()
        self.performance_memory = StrategyPerformanceMemory()
        self.regime_memory = RegimeMemory()
        self.feedback_store = FeedbackStore()
        self.feedback_loop = PaperFeedbackLoop(self.feedback_store, RewardEngine(), SafeBanditSelector())
        self.mysql = MySQLStore(settings)

    async def start(self) -> None:
        await self.mysql.connect()

    async def stop(self) -> None:
        await self.mysql.close()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    service = AdaptiveAIService(settings)
    app = FastAPI(
        title="Adaptive AI/ML Intelligence Layer",
        version="1.0.0",
        description="Market-regime intelligence, adaptive weighting, anomaly detection, sentiment, and model training API.",
    )
    app.state.service = service

    from api.routes_anomaly import router as anomaly_router
    from api.routes_features import router as features_router
    from api.routes_regime import router as regime_router
    from api.routes_sentiment import router as sentiment_router
    from api.routes_training import router as training_router
    from api.routes_weighting import router as weighting_router

    app.include_router(features_router)
    app.include_router(sentiment_router)
    app.include_router(regime_router)
    app.include_router(anomaly_router)
    app.include_router(weighting_router)
    app.include_router(training_router)

    @app.on_event("startup")
    async def startup() -> None:
        await service.start()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await service.stop()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
