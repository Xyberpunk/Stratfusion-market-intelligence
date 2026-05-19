from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clients.adaptive_ai_client import AdaptiveAIClient
from clients.algo_lab_client import AlgoLabClient
from config import Settings, get_settings
from logger import configure_logging
from storage.news_repository import NewsRepository


class PlatformGatewayService:
    """Orchestrates scraper news, Adaptive AI, and Algo Trading Lab APIs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.adaptive_ai = AdaptiveAIClient(settings.adaptive_ai_url, settings.request_timeout_seconds)
        self.algo_lab = AlgoLabClient(settings.algo_lab_url, settings.request_timeout_seconds)
        self.news = NewsRepository(settings)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    service = PlatformGatewayService(settings)
    app = FastAPI(
        title="StratFusion Platform Gateway",
        version="1.0.0",
        description="Unified orchestration API connecting scraper_engine, adaptive_ai_layer, and algo_trading_lab.",
    )
    app.state.service = service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.routes_news import router as news_router
    from api.routes_pipeline import router as pipeline_router
    from api.routes_status import router as status_router

    app.include_router(status_router)
    app.include_router(news_router)
    app.include_router(pipeline_router)
    return app


app = create_app()
