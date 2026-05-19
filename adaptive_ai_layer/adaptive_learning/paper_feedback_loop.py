from __future__ import annotations

from adaptive_learning.bandit_selector import SafeBanditSelector
from adaptive_learning.reward_engine import RewardEngine
from memory.feedback_store import FeedbackStore
from models.schemas import PaperTradeFeedback


class PaperFeedbackLoop:
    """Records paper feedback, computes reward, and updates experimental selectors."""

    def __init__(self, feedback_store: FeedbackStore, reward_engine: RewardEngine, bandit: SafeBanditSelector) -> None:
        self.feedback_store = feedback_store
        self.reward_engine = reward_engine
        self.bandit = bandit

    def record(self, feedback: PaperTradeFeedback) -> dict[str, float | str]:
        self.feedback_store.add(feedback)
        reward = self.reward_engine.reward(feedback)
        self.bandit.update(feedback.strategy_name, reward)
        return {
            "strategy_name": feedback.strategy_name,
            "reward": reward,
            "message": "Paper feedback recorded for adaptive research memory. It does not trigger autonomous live trading.",
        }
