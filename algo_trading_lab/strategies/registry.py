from __future__ import annotations

from strategies.ai_ml.finbert_sentiment import FinBERTSentimentStrategy
from strategies.ai_ml.lstm_interface import LSTMReadyStrategy
from strategies.ai_ml.transformer_sentiment import TransformerSentimentStrategy
from strategies.ai_ml.xgboost_interface import XGBoostReadyStrategy
from strategies.base import BaseStrategy
from strategies.mean_reversion.bollinger_reversion import BollingerReversionStrategy
from strategies.mean_reversion.rsi_reversal import RSIReversalStrategy
from strategies.mean_reversion.stochastic_reversal import StochasticReversalStrategy
from strategies.momentum.breakout import BreakoutStrategy
from strategies.momentum.macd import MACDMomentumStrategy
from strategies.momentum.moving_average import MovingAverageCrossoverStrategy
from strategies.momentum.supertrend import SuperTrendStrategy
from strategies.momentum.vwap import VWAPStrategy
from strategies.statistical.arima_interface import ARIMAReadyStrategy
from strategies.statistical.kalman_interface import KalmanReadyStrategy
from strategies.statistical.zscore_reversion import ZScoreMeanReversionStrategy
from strategies.volatility.atr_system import ATRSystemStrategy
from strategies.volatility.options_iv import OptionsIVStrategy


class StrategyRegistry:
    """Registry for all independent strategy engines."""

    core_strategy_names = [
        "MACD Momentum",
        "VWAP",
        "RSI Reversal",
        "ATR Volatility System",
        "FinBERT Sentiment",
    ]

    def __init__(self) -> None:
        strategies: list[BaseStrategy] = [
            BreakoutStrategy(),
            VWAPStrategy(),
            MovingAverageCrossoverStrategy(),
            MACDMomentumStrategy(),
            SuperTrendStrategy(),
            RSIReversalStrategy(),
            BollingerReversionStrategy(),
            StochasticReversalStrategy(),
            ATRSystemStrategy(),
            OptionsIVStrategy(),
            ZScoreMeanReversionStrategy(),
            ARIMAReadyStrategy(),
            KalmanReadyStrategy(),
            FinBERTSentimentStrategy(),
            TransformerSentimentStrategy(),
            XGBoostReadyStrategy(),
            LSTMReadyStrategy(),
        ]
        self._strategies = {strategy.name: strategy for strategy in strategies}

    def all(self) -> list[BaseStrategy]:
        return list(self._strategies.values())

    def names(self) -> list[str]:
        return list(self._strategies)

    def get(self, name: str) -> BaseStrategy:
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise ValueError(f"Unknown strategy: {name}") from exc

    def selected(self, names: list[str] | None) -> list[BaseStrategy]:
        if not names:
            return [self.get(name) for name in self.core_strategy_names]
        return [self.get(name) for name in names]
