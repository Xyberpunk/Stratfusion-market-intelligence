from __future__ import annotations

from fastapi import FastAPI

from accuracy.accuracy_tracker import AccuracyTracker
from accuracy.strategy_performance_store import StrategyPerformanceStore
from ai.anomaly_detector import AnomalyDetector
from ai.explanation_engine import ExplanationEngine
from backtesting.backtester import Backtester
from config import Settings, get_settings
from custom_builder.custom_strategy_runner import CustomStrategyRunner
from custom_builder.strategy_builder import CustomStrategyBuilder
from data.feature_builder import FeatureBuilder
from ensemble.dynamic_weighting import DynamicWeightingEngine
from ensemble.ensemble_engine import EnsembleEngine
from ensemble.weight_manager import WeightManager
from explanation.explanation_engine import FinalExplanationEngine
from logger import configure_logging
from models.enums import RiskLevel
from models.schemas import (
    BacktestRunRequest,
    EnsembleRunRequest,
    FinalTradingGuidance,
    GenerateSignalRequest,
)
from regime.regime_detector import RegimeDetector
from risk.risk_engine import RiskEngine
from storage.mysql import MySQLClient
from storage.repositories import InMemoryRepository
from strategies.base import StrategyContext
from strategies.registry import StrategyRegistry


class AlgoTradingLabService:
    """Application service composing all Algo Trading Lab engines."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.feature_builder = FeatureBuilder()
        self.registry = StrategyRegistry()
        self.repository = InMemoryRepository()
        self.performance_store = StrategyPerformanceStore()
        self.regime_detector = RegimeDetector(settings)
        self.weight_manager = WeightManager(settings, self.registry)
        self.ensemble_engine = EnsembleEngine(DynamicWeightingEngine(self.weight_manager), ExplanationEngine())
        self.final_explainer = FinalExplanationEngine()
        self.risk_engine = RiskEngine(settings)
        self.backtester = Backtester(self.feature_builder)
        self.accuracy_tracker = AccuracyTracker()
        self.custom_builder = CustomStrategyBuilder(self.registry, settings)
        self.custom_runner = CustomStrategyRunner(self.registry)
        self.anomaly_detector = AnomalyDetector()
        self.mysql = MySQLClient(settings)

    async def start(self) -> None:
        await self.mysql.connect()

    async def stop(self) -> None:
        await self.mysql.close()

    def list_strategies(self) -> list[dict[str, str]]:
        return [
            {"name": strategy.name, "category": strategy.category.value}
            for strategy in self.registry.all()
        ]

    def generate_signal(self, request: GenerateSignalRequest) -> dict[str, object]:
        features = self.feature_builder.build(request.market_data)
        context = StrategyContext(
            symbol=request.symbol,
            features=features,
            sentiments=request.sentiments,
            options_chain=request.options_chain,
        )
        regime = self.regime_detector.detect(context)
        self.repository.save_regime(regime)
        strategies = self.registry.selected(request.strategy_names)
        signals = [strategy.generate(context) for strategy in strategies]
        risk_level = self._preliminary_risk_level(context)
        ensemble = self.ensemble_engine.run(
            symbol=request.symbol,
            signals=signals,
            regime=regime,
            custom_weights=request.custom_weights,
            accuracy=self.performance_store.all(),
            risk_level=risk_level,
        )
        guidance = self.risk_engine.evaluate(
            context=context,
            ensemble=ensemble,
            capital=request.capital,
            risk_per_trade=request.risk_per_trade,
        )
        anomalies = self.anomaly_detector.detect(context)
        sentiment_score = self._sentiment_score(request)
        options_summary = request.options_chain.model_dump() if request.options_chain else None
        guidance.final_explanation = self.final_explainer.explain(
            ensemble=guidance.ensemble,
            risk=guidance.risk,
            strategy_signals=signals,
            sentiment_score=sentiment_score,
            options_summary=options_summary,
            regime_explanation=f"Regime detector classified the market as {regime.regime.value} with {regime.confidence:.0%} confidence.",
        )
        self.repository.save_ensemble(ensemble)
        self.repository.save_risk(guidance.risk)
        return {
            "guidance": guidance,
            "regime": regime,
            "strategy_signals": signals,
            "anomalies": anomalies,
            "dashboard_sections": ["Web & News Market Intelligence", "AI Algo Trading Lab"],
        }

    @staticmethod
    def _sentiment_score(request: GenerateSignalRequest) -> float | None:
        if not request.sentiments:
            return None
        weighted = sum(item.sentiment_score * item.confidence for item in request.sentiments)
        confidence = sum(item.confidence for item in request.sentiments) or 1.0
        return weighted / confidence

    def run_ensemble(self, request: EnsembleRunRequest):
        output = self.ensemble_engine.run(
            symbol=request.symbol,
            signals=request.signals,
            regime=request.regime,
            custom_weights=request.custom_weights,
            accuracy=self.performance_store.all(),
            risk_level=request.risk_level,
        )
        self.repository.save_ensemble(output)
        return output

    def run_backtest(self, request: BacktestRunRequest) -> dict[str, object]:
        if request.custom_strategy:
            config = self.custom_builder.build(request.custom_strategy)
            strategy = self.registry.get(config.strategies[0].name)
        else:
            strategy = self.registry.get(request.strategy_name or "Moving Average Crossover")
        result = self.backtester.run_single_strategy(
            strategy=strategy,
            symbol=request.symbol,
            market_data=request.market_data,
        )
        run_id = self.repository.save_backtest(result)
        accuracy = self.accuracy_tracker.from_backtest(result=result)
        self.performance_store.add(accuracy)
        self.repository.save_accuracy(accuracy)
        return {"run_id": run_id, "result": result, "accuracy_record": accuracy}

    def _preliminary_risk_level(self, context: StrategyContext) -> RiskLevel:
        if context.features.empty:
            return RiskLevel.HIGH
        atr_pct = float(context.features.iloc[-1].get("atr_pct", 0.0))
        if atr_pct >= self.settings.high_volatility_atr_pct * 1.5:
            return RiskLevel.HIGH
        if atr_pct >= self.settings.high_volatility_atr_pct:
            return RiskLevel.MODERATE
        return RiskLevel.LOW


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    service = AlgoTradingLabService(settings)
    app = FastAPI(
        title="Adaptive Quant Intelligence Platform - Algo Trading Lab",
        version="1.0.0",
        description="Adaptive multi-strategy trading intelligence API with regime-aware ensemble and risk controls.",
    )
    app.state.service = service

    from api.routes_backtest import router as backtest_router
    from api.routes_custom_builder import router as custom_router
    from api.routes_signals import router as signals_router
    from api.routes_strategies import router as strategies_router

    app.include_router(strategies_router)
    app.include_router(signals_router)
    app.include_router(backtest_router)
    app.include_router(custom_router)

    @app.on_event("startup")
    async def on_startup() -> None:
        await service.start()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await service.stop()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
