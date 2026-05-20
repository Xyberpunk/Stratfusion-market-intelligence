from __future__ import annotations

from config import Settings
from models.enums import RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, FinalTradingGuidance, RiskOutput
from risk.drawdown_control import DrawdownControl
from risk.position_sizing import PositionSizer
from risk.stop_loss import StopLossCalculator
from risk.target_calculator import TargetCalculator
from strategies.base import StrategyContext


class RiskEngine:
    """Computes risk outputs and overrides unsafe trade guidance."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stop_loss = StopLossCalculator()
        self.target = TargetCalculator()
        self.position_sizer = PositionSizer()
        self.drawdown_control = DrawdownControl()

    def evaluate(
        self,
        *,
        context: StrategyContext,
        ensemble: EnsembleOutput,
        capital: float,
        risk_per_trade: float,
    ) -> FinalTradingGuidance:
        if context.features.empty:
            risk = RiskOutput(
                symbol=context.symbol.upper(),
                approved=False,
                input_action=ensemble.suggested_action.value,
                final_action=TradingSignal.HOLD.value,
                entry_price=0.0,
                stop_loss=None,
                target=None,
                risk_reward_ratio=0.0,
                position_size=0.0,
                capital_at_risk=0.0,
                max_drawdown_limit=self.settings.max_drawdown_limit,
                risk_level=RiskLevel.HIGH,
                reason="No market data is available.",
            )
            return FinalTradingGuidance(ensemble=ensemble, risk=risk, final_action=TradingSignal.HOLD, final_explanation="Risk engine moved action to HOLD because no market data is available.")
        latest = context.features.iloc[-1]
        entry = float(latest["close"])
        atr = float(latest.get("atr_14", entry * 0.02))
        proposed_action = ensemble.suggested_action
        action_for_risk = proposed_action if proposed_action != TradingSignal.HOLD else TradingSignal.BUY
        stop = self.stop_loss.calculate(entry_price=entry, atr=atr, action=action_for_risk)
        target = self.target.calculate(entry_price=entry, stop_loss=stop, action=action_for_risk)
        reward = abs(target - entry)
        risk_distance = abs(entry - stop)
        rr = reward / risk_distance if risk_distance > 0 else 0.0
        position_size, capital_at_risk = self.position_sizer.size(
            capital=capital,
            risk_per_trade=risk_per_trade,
            entry_price=entry,
            stop_loss=stop,
        )
        risk_level = self._risk_level(context, rr)
        final_action = self._override_action(proposed_action, risk_level, rr, context, ensemble)
        approved = final_action == proposed_action and final_action != TradingSignal.HOLD and risk_level not in {RiskLevel.HIGH, RiskLevel.EXTREME}
        if risk_level == RiskLevel.EXTREME:
            position_size = 0.0
            capital_at_risk = 0.0
            stop = None
            target = None
        elif risk_level == RiskLevel.HIGH:
            position_size = round(position_size * 0.5, 4)
            capital_at_risk = round(capital_at_risk * 0.5, 2)
        risk = RiskOutput(
            symbol=context.symbol.upper(),
            approved=approved,
            input_action=proposed_action.value,
            final_action=final_action.value,
            entry_price=round(entry, 2),
            stop_loss=stop,
            target=target,
            risk_reward_ratio=round(rr, 3),
            position_size=position_size,
            capital_at_risk=capital_at_risk,
            max_drawdown_limit=self.settings.max_drawdown_limit,
            risk_level=risk_level,
            reason=self._risk_reason(proposed_action, final_action, risk_level, rr, context),
        )
        final_explanation = self._final_explanation(ensemble, risk, final_action)
        return FinalTradingGuidance(ensemble=ensemble, risk=risk, final_action=final_action, final_explanation=final_explanation)

    def _risk_level(self, context: StrategyContext, risk_reward_ratio: float) -> RiskLevel:
        atr_pct = float(context.features.iloc[-1].get("atr_pct", 0.0))
        drawdown = abs(self.drawdown_control.max_drawdown(context.features["close"].tail(60)))
        if atr_pct >= self.settings.high_volatility_atr_pct * 2.2 or drawdown >= self.settings.max_drawdown_limit * 1.25:
            return RiskLevel.EXTREME
        if atr_pct >= self.settings.high_volatility_atr_pct * 1.5 or risk_reward_ratio < 1.2 or drawdown >= self.settings.max_drawdown_limit:
            return RiskLevel.HIGH
        if atr_pct >= self.settings.high_volatility_atr_pct or risk_reward_ratio < 1.8:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    def _override_action(self, action: TradingSignal, risk_level: RiskLevel, risk_reward_ratio: float, context: StrategyContext, ensemble: EnsembleOutput) -> TradingSignal:
        if action == TradingSignal.HOLD:
            return TradingSignal.HOLD
        if risk_level == RiskLevel.EXTREME:
            return TradingSignal.AVOID
        if ensemble.confidence.value in {"LOW"}:
            return TradingSignal.HOLD
        panic_return = float(context.features["close"].pct_change(5).iloc[-1]) if len(context.features.index) >= 6 else 0.0
        if risk_level == RiskLevel.HIGH and (risk_reward_ratio < 1.5 or panic_return <= self.settings.panic_drawdown_pct):
            return TradingSignal.HOLD
        return action

    def _risk_reason(self, proposed: TradingSignal, final: TradingSignal, risk_level: RiskLevel, rr: float, context: StrategyContext) -> str:
        if final != proposed:
            return f"Risk engine overrode {proposed.value} to {final.value}; risk level is {risk_level.value} and risk/reward is {rr:.2f}."
        atr_pct = float(context.features.iloc[-1].get("atr_pct", 0.0))
        return f"Risk engine approved {final.value}; risk level is {risk_level.value}, ATR percentage is {atr_pct:.2%}, and risk/reward is {rr:.2f}."

    @staticmethod
    def _final_explanation(ensemble: EnsembleOutput, risk: RiskOutput, final_action: TradingSignal) -> str:
        base = (
            f"Combined market intelligence suggests {ensemble.bullish_probability:.0%} bullish probability, "
            f"{ensemble.bearish_probability:.0%} bearish probability, and {ensemble.neutral_probability:.0%} neutral probability. "
            f"Suggested action is {ensemble.suggested_action.value} with {ensemble.confidence.value} confidence. "
            f"Risk level is {risk.risk_level.value}, stop loss is {risk.stop_loss}, target is {risk.target}, and risk/reward is {risk.risk_reward_ratio:.2f}."
        )
        if final_action != ensemble.suggested_action:
            return f"{base} Risk controls changed the final action to {final_action.value}."
        return f"{base} Final action remains {final_action.value} after risk checks."
