from __future__ import annotations

from collections import defaultdict

from models.schemas import AccuracyOutput, BacktestResult, CustomStrategyConfig, EnsembleOutput, RegimeOutput, RiskOutput


class InMemoryRepository:
    """Deterministic process-local repository used when MySQL is disabled."""

    def __init__(self) -> None:
        self.ensemble_signals: list[EnsembleOutput] = []
        self.regime_snapshots: dict[str, RegimeOutput] = {}
        self.risk_outputs: dict[str, RiskOutput] = {}
        self.backtests: dict[int, BacktestResult] = {}
        self.accuracy: dict[str, list[AccuracyOutput]] = defaultdict(list)
        self.custom_strategies: dict[str, CustomStrategyConfig] = {}
        self._backtest_id = 1

    def save_ensemble(self, output: EnsembleOutput) -> None:
        self.ensemble_signals.append(output)

    def save_regime(self, output: RegimeOutput) -> None:
        self.regime_snapshots[output.symbol] = output

    def get_regime(self, symbol: str) -> RegimeOutput | None:
        return self.regime_snapshots.get(symbol)

    def save_risk(self, output: RiskOutput) -> None:
        self.risk_outputs[output.symbol] = output

    def get_risk(self, symbol: str) -> RiskOutput | None:
        return self.risk_outputs.get(symbol)

    def save_backtest(self, result: BacktestResult) -> int:
        run_id = self._backtest_id
        self.backtests[run_id] = result
        self._backtest_id += 1
        return run_id

    def get_backtest(self, run_id: int) -> BacktestResult | None:
        return self.backtests.get(run_id)

    def save_accuracy(self, output: AccuracyOutput) -> None:
        self.accuracy[output.strategy_name].append(output)

    def get_accuracy(self, strategy_name: str) -> list[AccuracyOutput]:
        return self.accuracy.get(strategy_name, [])

    def save_custom_strategy(self, config: CustomStrategyConfig) -> None:
        self.custom_strategies[config.name] = config

    def list_custom_strategies(self) -> list[CustomStrategyConfig]:
        return list(self.custom_strategies.values())
