from __future__ import annotations

from datetime import datetime, timezone

from models.enums import ConfidenceLabel, RiskLevel, TradingSignal
from models.schemas import EnsembleOutput, RiskOutput
from risk.risk_gatekeeper import RiskGatekeeper


def test_risk_gatekeeper_blocks_low_rr() -> None:
    ensemble = EnsembleOutput(
        symbol="INFY",
        timestamp=datetime.now(timezone.utc),
        bullish_probability=0.7,
        bearish_probability=0.2,
        neutral_probability=0.1,
        confidence=ConfidenceLabel.HIGH,
        suggested_action=TradingSignal.BUY,
        risk_level=RiskLevel.MODERATE,
        explanation="Combined market intelligence suggests bullish probability.",
        strategy_breakdown=[],
    )
    risk = RiskOutput(
        symbol="INFY",
        entry_price=100,
        stop_loss=98,
        target=101,
        risk_reward_ratio=0.5,
        position_size=100,
        capital_at_risk=200,
        max_drawdown_limit=0.15,
        risk_level=RiskLevel.MODERATE,
    )
    output = RiskGatekeeper().evaluate(ensemble, risk)
    assert output.approved is False
    assert output.final_action == "HOLD"
