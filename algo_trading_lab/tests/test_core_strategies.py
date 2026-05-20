from __future__ import annotations

from data.feature_builder import FeatureBuilder
from models.enums import TradingSignal
from strategies.base import StrategyContext
from strategies.mean_reversion.rsi_reversal import RSIReversalStrategy
from strategies.momentum.macd import MACDMomentumStrategy
from strategies.momentum.vwap import VWAPStrategy
from strategies.volatility.atr_system import ATRSystemStrategy
from tests.test_strategies import sample_market_data


def context(rows: int = 80) -> StrategyContext:
    return StrategyContext(symbol="INFY", features=FeatureBuilder().build(sample_market_data("INFY", rows)), sentiments=[])


def test_macd_strategy_is_defensive_and_emits_signal() -> None:
    signal = MACDMomentumStrategy().generate(context())
    assert signal.signal in {TradingSignal.BUY, TradingSignal.SELL, TradingSignal.HOLD}
    assert signal.reason


def test_vwap_strategy_is_defensive_and_emits_signal() -> None:
    signal = VWAPStrategy().generate(context())
    assert signal.signal in {TradingSignal.BUY, TradingSignal.SELL, TradingSignal.HOLD}
    assert "VWAP" in signal.reason


def test_rsi_strategy_oversold_buy() -> None:
    ctx = context()
    ctx.features.loc[ctx.features.index[-1], "rsi"] = 20
    signal = RSIReversalStrategy().generate(ctx)
    assert signal.signal == TradingSignal.BUY


def test_atr_breakout_strategy_is_defensive_and_emits_signal() -> None:
    signal = ATRSystemStrategy().generate(context())
    assert signal.signal in {TradingSignal.BUY, TradingSignal.SELL, TradingSignal.HOLD}
    assert signal.reason
