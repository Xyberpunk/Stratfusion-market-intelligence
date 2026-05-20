from __future__ import annotations

from models.enums import StrategyCategory
from strategies.base import BaseStrategy, StrategyContext, StrategySignal


class MACDMomentumStrategy(BaseStrategy):
    name = "MACD Momentum"
    category = StrategyCategory.MOMENTUM

    def generate(self, context: StrategyContext) -> StrategySignal:
        if not self._has_rows(context, 26):
            return self._hold(context, "Insufficient candles for MACD.")
        latest = context.features.iloc[-1]
        previous = context.features.iloc[-2]
        macd = float(latest.get("macd", 0.0))
        signal = float(latest.get("macd_signal", 0.0))
        histogram = float(latest.get("macd_histogram", macd - signal))
        previous_histogram = float(previous.get("macd_histogram", previous.get("macd", 0.0) - previous.get("macd_signal", 0.0)))
        bullish_crossover = float(previous.get("macd", 0.0)) <= float(previous.get("macd_signal", 0.0)) and macd > signal
        bearish_crossover = float(previous.get("macd", 0.0)) >= float(previous.get("macd_signal", 0.0)) and macd < signal
        rising_positive = histogram > 0 and histogram > previous_histogram
        falling_negative = histogram < 0 and histogram < previous_histogram
        if bullish_crossover or rising_positive:
            strength = min(1.0, abs(histogram) / max(abs(macd), 1e-6) + (0.25 if bullish_crossover else 0.0))
            return self._signal(context, max(0.25, strength), min(0.9, 0.5 + strength * 0.35), "MACD is bullish from crossover or rising positive histogram.", {"macd": macd, "macd_signal": signal, "histogram": histogram, "bullish_crossover": bullish_crossover})
        if bearish_crossover or falling_negative:
            strength = min(1.0, abs(histogram) / max(abs(macd), 1e-6) + (0.25 if bearish_crossover else 0.0))
            return self._signal(context, -max(0.25, strength), min(0.9, 0.5 + strength * 0.35), "MACD is bearish from crossover or falling negative histogram.", {"macd": macd, "macd_signal": signal, "histogram": histogram, "bearish_crossover": bearish_crossover})
        return self._signal(context, 0.0, 0.35, "MACD has no clear crossover or histogram momentum.", {"macd": macd, "macd_signal": signal, "histogram": histogram})
