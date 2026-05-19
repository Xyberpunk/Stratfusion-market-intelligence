from __future__ import annotations

from memory.feedback_store import FeedbackStore


class SignalFeedbackMemory(FeedbackStore):
    """Persistent feedback memory facade for signal false-positive/false-negative tracking."""
