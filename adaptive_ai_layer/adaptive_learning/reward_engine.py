from __future__ import annotations

from models.schemas import PaperTradeFeedback


class RewardEngine:
    """Computes safe paper-trading rewards with return, drawdown, and false-signal penalties."""

    def reward(self, feedback: PaperTradeFeedback) -> float:
        direction = 1.0 if feedback.signal.upper() == "BUY" else -1.0 if feedback.signal.upper() == "SELL" else 0.0
        directional_return = direction * feedback.realized_return
        drawdown_penalty = abs(feedback.max_adverse_excursion) * 0.5
        false_signal_penalty = 0.02 if directional_return < 0 and feedback.confidence > 0.65 else 0.0
        confidence_bonus = 0.01 if directional_return > 0 and feedback.confidence > 0.65 else 0.0
        return float(directional_return - drawdown_penalty - false_signal_penalty + confidence_bonus)
