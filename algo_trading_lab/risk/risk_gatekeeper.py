from __future__ import annotations

from pydantic import BaseModel

from models.enums import RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, RiskOutput


class GatekeeperOutput(BaseModel):
    approved: bool
    final_action: str
    risk_level: str
    position_size: float
    stop_loss: float | None
    target: float | None
    reason: str


class RiskGatekeeper:
    """Final risk authority that can override any signal."""

    def evaluate(
        self,
        ensemble: EnsembleOutput,
        risk: RiskOutput,
        *,
        stale_data: bool = False,
        high_anomaly_severity: bool = False,
        drawdown_breach: bool = False,
    ) -> GatekeeperOutput:
        reasons: list[str] = []
        action = ensemble.suggested_action
        approved = True
        risk_level = risk.risk_level
        position_size = risk.position_size
        if stale_data:
            reasons.append("stale data prevents signal approval")
            approved = False
            action = "AVOID"
            risk_level = RiskLevel.HIGH
            position_size = 0.0
        if risk.risk_reward_ratio < 1.2 and action != TradingSignal.HOLD:
            reasons.append("poor risk/reward downgraded directional signal")
            action = TradingSignal.HOLD
            approved = False
        if risk.risk_level == RiskLevel.HIGH:
            reasons.append("high risk reduced position size")
            position_size *= 0.5
        if high_anomaly_severity:
            reasons.append("high anomaly severity requires stronger confirmation")
            if ensemble.confidence.value != "HIGH":
                action = TradingSignal.HOLD
                approved = False
        if drawdown_breach:
            reasons.append("recent drawdown breach blocks new trades")
            action = "AVOID"
            approved = False
            position_size = 0.0
        if ensemble.confidence.value == "LOW" and action != TradingSignal.HOLD:
            reasons.append("low confidence ensemble downgraded to HOLD")
            action = TradingSignal.HOLD
            approved = False
        return GatekeeperOutput(
            approved=approved and action != TradingSignal.HOLD,
            final_action=action.value if hasattr(action, "value") else str(action),
            risk_level=risk_level.value,
            position_size=round(position_size, 4),
            stop_loss=risk.stop_loss if position_size > 0 else None,
            target=risk.target if position_size > 0 else None,
            reason="; ".join(reasons) or "risk gatekeeper approved the ensemble signal",
        )
