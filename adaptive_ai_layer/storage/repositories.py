from __future__ import annotations

from collections import defaultdict

from models.model_outputs import ModelPrediction
from models.schemas import (
    AnomalyOutput,
    FinBERTOutput,
    ModelRegistryItem,
    PaperTradeFeedback,
    RegimeOutput,
    StrategyPerformanceRecord,
    TrainingRunOutput,
    WeightingOutput,
)


class InMemoryRepository:
    """Process-local repository used by default and by tests."""

    def __init__(self) -> None:
        self.regimes: dict[str, RegimeOutput] = {}
        self.anomalies: list[AnomalyOutput] = []
        self.sentiments: list[FinBERTOutput] = []
        self.weights: list[WeightingOutput] = []
        self.training_runs: dict[str, TrainingRunOutput] = {}
        self.models: dict[str, ModelRegistryItem] = {}
        self.predictions: list[ModelPrediction] = []
        self.strategy_memory: dict[str, list[StrategyPerformanceRecord]] = defaultdict(list)
        self.paper_feedback: list[PaperTradeFeedback] = []

    def save_regime(self, output: RegimeOutput) -> None:
        self.regimes[output.symbol.upper()] = output

    def save_anomalies(self, outputs: list[AnomalyOutput]) -> None:
        self.anomalies.extend(outputs)

    def save_sentiments(self, outputs: list[FinBERTOutput]) -> None:
        self.sentiments.extend(outputs)

    def save_weighting(self, output: WeightingOutput) -> None:
        self.weights.append(output)

    def save_training_run(self, output: TrainingRunOutput) -> None:
        self.training_runs[output.run_id] = output

    def save_model(self, item: ModelRegistryItem) -> None:
        self.models[item.model_name] = item

    def list_models(self) -> list[ModelRegistryItem]:
        return list(self.models.values())

    def save_strategy_memory(self, record: StrategyPerformanceRecord) -> None:
        self.strategy_memory[record.strategy_name].append(record)

    def get_strategy_memory(self, strategy_name: str) -> list[StrategyPerformanceRecord]:
        return self.strategy_memory.get(strategy_name, [])

    def save_feedback(self, feedback: PaperTradeFeedback) -> None:
        self.paper_feedback.append(feedback)
